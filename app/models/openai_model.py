from app.models import utils

import streamlit as st
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


K = 6
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


def _clean_llm_response(llm_response):
    answer = llm_response["result"]
    sources = [source.metadata["source"] for source in llm_response["source_documents"]]
    return answer, sources


@st.cache_resource
def load_chain(index_change=0):
    if index_change:
        index = utils.get_index("openai")
    retriever = index.as_retriever(search_kwargs={"k": K})

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )
    return qa_chain


def run(qa_chain, question):
    llm_response = qa_chain(question)
    answer, sources = _clean_llm_response(llm_response)

    return answer, utils.clean_source(set(sources))
