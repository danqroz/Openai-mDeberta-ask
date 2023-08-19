import os
import re

import streamlit as st
import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer

from app.models import utils

PATTERN = re.compile(r"\[CLS\]|\[SEP\]")
MAX_SEQ_LEN = 512
MODEL_NAME = "timpal0l/mdeberta-v3-base-squad2"
DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
MIN_SCORE = 2.9
K = 10


def _clean_answer(answer, question):
    return answer.replace(question, "")


def _get_top_answers(
    answer_list: list[str],
    score_list: list[float],
):
    tupla_score = list(enumerate(score_list))
    # ordenar a lista em ordem decrescente
    tupla_score = sorted(tupla_score, key=lambda x: x[1], reverse=True)
    # obtendo os índices correspondentes em answer_list
    indices_answer = [tupla[0] for tupla in tupla_score]
    # obtendo os elementos correspondentes em cada lista
    score_list = [score_list[i] for i in indices_answer]
    answer_list = [answer_list[i] for i in indices_answer]

    if not score_list:
        return ["Nenhuma resposta encontrada."]
    return answer_list


def _answers_from_docs(tokenizer, model, docs, question):
    answers, scores, sources = [], [], []
    for doc in docs:
        content = doc.page_content
        source = os.path.basename(doc.metadata["source"])

        inputs = tokenizer.encode_plus(
            question,
            content,
            add_special_tokens=True,
            max_length=MAX_SEQ_LEN,
            truncation=True,
            return_tensors="pt",
        ).to(DEVICE)
        input_ids = inputs["input_ids"].tolist()[0]

        answer_start_scores, answer_end_scores = model(**inputs, return_dict=False)
        answer_start_score = torch.max(answer_start_scores).item()

        answer_start = torch.argmax(answer_start_scores)
        answer_end = torch.argmax(answer_end_scores) + 1
        answer = tokenizer.decode(input_ids[answer_start:answer_end])
        no_special_token_answer = re.sub(PATTERN, "", answer).strip()

        if no_special_token_answer and answer_start_score > MIN_SCORE:
            # Get the most likely end of answer with the argmax of the score
            answers.append(no_special_token_answer)
            scores.append(answer_start_score)
            sources.append(source)
    return answers, scores, sources


@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)
    model.to(DEVICE)
    return tokenizer, model


def run(tokenizer, model, question):
    index = utils.get_index()
    docs = index.similarity_search(question, k=K)
    answers, scores, sources = _answers_from_docs(tokenizer, model, docs, question)
    answer_list = _get_top_answers(answers, scores)
    clean_answers = [_clean_answer(answer, question) for answer in answer_list]
    return ", ".join(clean_answers), utils.clean_source(set(sources))
