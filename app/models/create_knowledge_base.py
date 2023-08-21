from app.models import utils
import os

from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
DATA_PATH = utils.DATA_PATH


def _check_index_existence(index_path):
    if not os.path.exists(index_path):
        os.makedirs(index_path)
        return None

    existent_index = [
        # index.split(".")[0]
        os.path.splitext(index)[0]
        for index in os.listdir(index_path)
        if index.endswith(".pkl")
    ]
    return existent_index


def _split_text():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ","],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def create_index(embedding_name="huggingf"):
    index_path, embeddings = utils.setup_for_embeddings(
        # openai_api_key=openai_api_key,
        embedding_name,
        return_embeddings=True,
    )

    old_index_name = _check_index_existence(index_path)
    chunks = _split_text()
    new_index = FAISS.from_documents(chunks, embeddings)
    if old_index_name:
        old_index = FAISS.load_local(
            folder_path=index_path,
            embeddings=embeddings,
        )
        old_index.merge_from(new_index)
        old_index.save_local(
            folder_path=index_path,
        )
        return
    new_index.save_local(index_path)
    return None


if __name__ == "__main__":
    create_index()
