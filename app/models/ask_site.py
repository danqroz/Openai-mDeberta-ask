from app.models import utils
from urllib.parse import urljoin, urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup as bs


from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

PROMPT_TEMPLATE = """
Use a seguinte passagem de texto para responder a pergunta ao final.
Se você não souber a resposta ou a resposta não estiver no texto apenas diga que não
sabe. É importante que você só responda se a resposta estiver no texto abaixo:
{context}

Pergunta: {question}
Resposta em português:
"""

PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE, input_variables=["context", "question"]
)

urls = list()


def _format_link(site):
    if site.startswith("http"):
        return site
    return "https://" + site


def full_scrape_urls(site):
    site = _format_link(site)
    domain = urlparse(site).netloc
    response = requests.get(site)
    soup = bs(response.content, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.startswith("#"):  # and (site := site + href) not in url:
            site = urljoin(site, href)
            if site not in urls and domain in site:
                urls.append(site)
                scrape_urls(site)


def scrape_urls(site):
    domain = urlparse(site).netloc
    response = requests.get(site)
    soup = bs(response.content, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.startswith("#"):  # and (site := site + href) not in url:
            site = urljoin(site, href)
            if site not in urls and domain in site:
                urls.append(site)


def _clean_llm_response(llm_response):
    answer = llm_response["result"]
    sources = [source.metadata["source"] for source in llm_response["source_documents"]]
    return answer, sources


def _split_text():
    documents = _get_site_data()
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ","],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def _get_site_data():
    loaders = UnstructuredURLLoader(urls=urls)
    data = loaders.load()
    return data


def get_urls(site):
    full_scrape_urls(site)
    return urls


@st.cache_resource
def load_site_chain(site):
    if not urls:
        urls.extend(site)

    chunks = _split_text()
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    knowledge_base = FAISS.from_documents(chunks, embeddings)

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
        chain_type="stuff",
        retriever=knowledge_base.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )
    return qa_chain


def run(qa_chain, question):
    llm_response = qa_chain(question)
    answer, sources = _clean_llm_response(llm_response)
    return answer, set(sources)
