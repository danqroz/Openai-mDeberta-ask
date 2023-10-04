import re
from pypdf import PdfReader
import os
import streamlit as st
from typing import Union, Tuple, Any, List

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import FAISS


APP_PATH = os.path.dirname(os.path.abspath(__file__ + "/../"))
DATA_PATH = os.path.join(APP_PATH, "data")
OPENAI_INDEX_PATH = os.path.join(DATA_PATH, "index_openai")
HF_INDEX_PATH = os.path.join(DATA_PATH, "index_hf")
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"


def setup_for_embeddings(
    embedding_model: str, return_embeddings: bool = False
) -> Union[Tuple[str, Embeddings], str]:
    """
    Set up the environment by providing the path for working with text embeddings.

    This function configures the environment for working with text embeddings, such as
    OpenAI's GPT-3 or Hugging Face's transformer models.

    Args:
        embedding_model (str): The name of the embedding model to use (e.g., "openai").
        return_embeddings (bool, optional): Whether to return the embeddings object.
            Default is False.

    Returns:
        Union[Tuple[str, Embeddings], str]: Depending on the `return_embeddings` flag:
            - If `return_embeddings` is True and `embedding_model` is "openai", returns
              a tuple containing the path to the OpenAI index and an OpenAIEmbeddings
              object.
            - If `return_embeddings` is True and `embedding_model` is not "openai",
              returns a tuple containing the path to the Hugging Face index and a
              HuggingFaceEmbeddings object.
            - If `return_embeddings` is False and `embedding_model` is "openai", returns
              the path to the OpenAI index.
            - If `return_embeddings` is False and `embedding_model` is not "openai",
              returns the path to the Hugging Face index.
    """
    if return_embeddings:
        if embedding_model.lower() == "openai":
            return OPENAI_INDEX_PATH, OpenAIEmbeddings(
                model="text-embedding-ada-002",
            )
        return HF_INDEX_PATH, HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    if embedding_model.lower() == "openai":
        return OPENAI_INDEX_PATH
    return HF_INDEX_PATH


def get_index(model_name: str = "huggingf") -> FAISS:
    index_path, embeddings = setup_for_embeddings(model_name, return_embeddings=True)
    index = FAISS.load_local(folder_path=index_path, embeddings=embeddings)
    return index


@st.cache_resource
def load_indexes(index_change: int = 0) -> FAISS:
    """
    Load a FAISS index for similarity search.

    Args:
        index_change (int, optional): trick parameter to force streamlit to re-load
        index each time a new `index_change` is provided.

    Returns:
        FAISS: The loaded FAISS index for similarity search.

    Note:
    - This function may be used with Streamlit's `st.cache_resource` decorator to
      efficiently cache and retrieve the index.
    """
    if index_change:
        return get_index("huggingf")
    return get_index("huggingf")


def _pdf_reader(file: Any) -> str:
    reader = PdfReader(file)
    total_pages = len(reader.pages)

    pdf_content = ""
    for page_number in range(total_pages):
        page = reader.pages[page_number]
        pdf_content += page.extract_text()
    return pdf_content


def _clean_text(text: str) -> str:
    lines = text.replace("\r", "").split("\n")
    cleaned_lines = " ".join([line.strip() for line in lines if line.strip()])
    no_spaces_text = re.sub(r"\s+", " ", cleaned_lines)
    return re.sub(r"\s*-\s*", "-", no_spaces_text)


def _get_file_name(path: str) -> str:
    normalized_path = os.path.normpath(path.replace("\\", "/"))
    basename = os.path.basename(normalized_path)
    return os.path.splitext(basename)[0]


def clean_source(sources: List[str]) -> str:
    """
    Clean and format a list of source filenames.

    This function takes a list of source filenames and cleans them, extracting only
    the file names without their paths or extensions. It then joins the cleaned
    filenames into a comma-separated string.

    Args:
        sources (List[str]): A list of source filenames.

    Returns:
        str: A comma-separated string containing the cleaned source filenames.

    Example:
        If `sources` is ["/path/to/file1.txt", "/path/to/file2.csv"], the function
        will return "file1, file2".
    """
    clean_sources = [_get_file_name(source) for source in sources]
    return ", ".join(clean_sources)


def pdf_to_txt(file: str, path: str) -> None:
    """
    Convert a PDF file to plain text and save it.

    This function takes the path to a PDF file (`file`) and a destination path (`path`)
    where the plain text content will be saved. It reads the content of the PDF file,
    cleans the text, and saves it as a text file with the same name as the PDF file
    but with a ".txt" extension.

    Args:
        file (str): The path to the PDF file to be converted.
        path (str): The path where the plain text content will be saved.

    Returns:
        None

    Note:
    - The function uses the `_pdf_reader` function to extract text content from the PDF.
    - The extracted text is cleaned using the `_clean_text` function before saving it
      as a text file.
    """
    save_path = path.replace(".pdf", ".txt")
    pdf_content = _pdf_reader(file)

    cleaned_content = _clean_text(pdf_content)

    with open(save_path, "w", encoding="utf-8") as file:
        file.write(cleaned_content)


def remove_files() -> None:
    """
    Remove all files in a specified directory.

    This function iterates through all items in the directory specified by `DATA_PATH`
    and removes any files found. It does not remove directories or subdirectories.

    Returns:
        None
    """
    for item in os.listdir(DATA_PATH):
        if os.path.isfile(item_path := os.path.join(DATA_PATH, item)):
            os.remove(item_path)
