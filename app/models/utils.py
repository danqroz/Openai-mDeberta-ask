import re
from pypdf import PdfReader
import os

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

APP_PATH = os.path.dirname(os.path.abspath(__file__ + "/../"))
DATA_PATH = os.path.join(APP_PATH, "data")
OPENAI_INDEX_PATH = os.path.join(DATA_PATH, "index_openai")
HF_INDEX_PATH = os.path.join(DATA_PATH, "index_hf")
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"


def setup_for_embeddings(embedding_model, return_embeddings=False):
    if return_embeddings:
        if embedding_model.lower() == "openai":
            return OPENAI_INDEX_PATH, OpenAIEmbeddings(
                model="text-embedding-ada-002",
            )
        return HF_INDEX_PATH, HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    if embedding_model.lower() == "openai":
        return OPENAI_INDEX_PATH
    return HF_INDEX_PATH


def get_index(model_name: str = "huggingf"):
    index_path, embeddings = setup_for_embeddings(model_name, return_embeddings=True)
    index = FAISS.load_local(folder_path=index_path, embeddings=embeddings)
    return index


def _pdf_reader(file):
    reader = PdfReader(file)
    total_pages = len(reader.pages)

    pdf_content = ""
    for page_number in range(total_pages):
        page = reader.pages[page_number]
        pdf_content += page.extract_text()
    return pdf_content


def _clean_text(text):
    lines = text.replace("\r", "").split("\n")
    cleaned_lines = " ".join([line.strip() for line in lines if line.strip()])
    no_spaces_text = re.sub(r"\s+", " ", cleaned_lines)
    return re.sub(r"\s*-\s*", "-", no_spaces_text)


def _get_file_name(path):
    normalized_path = os.path.normpath(path.replace("\\", "/"))
    basename = os.path.basename(normalized_path)
    return os.path.splitext(basename)[0]


def clean_source(sources):
    clean_sources = [_get_file_name(source) for source in sources]
    return ", ".join(clean_sources)


def pdf_to_txt(file, path):
    save_path = path.replace(".pdf", ".txt")
    pdf_content = _pdf_reader(file)

    cleaned_content = _clean_text(pdf_content)

    with open(save_path, "w", encoding="utf-8") as file:
        file.write(cleaned_content)


def remove_files():
    for item in os.listdir(DATA_PATH):
        if os.path.isfile(item_path := os.path.join(DATA_PATH, item)):
            os.remove(item_path)
