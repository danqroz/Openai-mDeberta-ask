from app.models import utils

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser

from langchain.tools import DuckDuckGoSearchResults
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS

import langdetect
from iso639 import Lang
from operator import itemgetter
import streamlit as st
import re


CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

TRANSLATE_PROMPT = PromptTemplate.from_template(
    """Translate the following text to {site_language}:

    {query}

    translation:"""
)

QA_PROMPT = PromptTemplate.from_template(
    """
    Use the following pieces of context to answer the question at the end. Answer it
    with the maximum of detail you can. If you don't know the answer or you think the
    answer is not in the context, please do not answer.

    {context}

    Question: {question}
    Answer in {user_language}:
    """
)


def clean_url(url):
    match = re.search(r"(?:https?://)?(?:www\.)?([^/]+)", url)
    if match:
        return match.group(1)
    return url


def _split_results(results):
    contents = list()
    for snippet in results.split("[snippet: "):
        if snippet:
            content_, link = snippet.rsplit(", link: ", 1)
            content, title = content_.rsplit(", title: ", 1)
            doc = Document(
                page_content=content,
                metadata={
                    "source": link[:-1] if link.endswith("]") else link,
                    "title": title.rsplit(" - ", 1)[0],
                },
            )
            contents.append(doc)
    return contents


def _create_site_chunks(url, query=""):
    search = DuckDuckGoSearchResults()
    results = search.run(f"site:{url} {query}")
    chunks = _split_results(results)
    return chunks


def _create_retriever(url, query):
    chunks = _create_site_chunks(url, query)
    _, hf_embeddings = utils.setup_for_embeddings(
        embedding_model="huggingface", return_embeddings=True
    )
    vector_store = FAISS.from_documents(chunks, embedding=hf_embeddings)
    retriever = vector_store.as_retriever()
    return retriever


def _get_site_language(url):
    chunks = _create_site_chunks(url)[:3]
    chunk_content = ""
    if not chunks:
        raise ValueError("Tem certeza que este url existe?")

    for chunk in chunks:
        chunk.page_content = " ".join(chunk.page_content.split())
        chunk_content += chunk.page_content
    return langdetect.detect(chunk_content)


def get_languages(url="", query=""):
    if url:
        return Lang(_get_site_language(url)).name
    return Lang(langdetect.detect(query)).name


@st.cache_resource
def load_model():
    chat_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    return chat_model


@st.cache_resource
def load_translate_chain():
    translate_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    translate_chain = TRANSLATE_PROMPT | translate_model | StrOutputParser()
    return translate_chain


def create_chain(chat_model, retriever):
    ask_site_chain = (
        {
            "context": itemgetter("question") | retriever,
            "question": itemgetter("question"),
            "user_language": itemgetter("user_language"),
        }
        | QA_PROMPT
        | chat_model
        | StrOutputParser()
    )
    return ask_site_chain


def check_chain_language(chain, language):
    chain.first = chain.first.partial(site_language=language)
    return chain


def translate_query(query, chain):
    return chain.invoke({"query": query})


def run(url, query, chat_model, user_lang):
    retriever = _create_retriever(url, query)
    ask_site_chain = create_chain(chat_model, retriever)

    answer = ask_site_chain.invoke({"question": query, "user_language": user_lang})
    return answer
