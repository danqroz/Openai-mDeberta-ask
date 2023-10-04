from app.models import utils

import os
import re
from typing import List, Tuple
import langdetect

import streamlit as st
import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
from langchain.vectorstores import FAISS


PATTERN = re.compile(r"\[CLS\]|\[SEP\]")
DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)


class DeBerta:
    def __init__(self):
        self.k = 8
        self.min_score = 2.9
        self.model_name = "timpal0l/mdeberta-v3-base-squad2"
        self.max_seq_len = 512
        self.tokenizer, self.model = self._load_model()

    def _clean_answer(self, answer: str, question: str) -> str:
        return answer.replace(question, "")

    def _get_top_answers(
        self,
        answer_list: List[str],
        score_list: List[float],
    ) -> List[str]:
        """
        Get the top answers from a list based on their corresponding scores.

        This function takes two lists, `answer_list` and `score_list`, where each answer
        in `answer_list` corresponds to a score in `score_list`. It returns a list of
        answers sorted by their scores in descending order.

        Args:
            answer_list (List[str]): A list of answers.
            score_list (List[float]): A list of scores corresponding to the answers.

        Returns:
            List[str]: A list of answers sorted by score in descending order.

        If answer list or the score list is empty, the function returns
        a list with a single element: ["No answer found."].
        """
        tuple_score = list(enumerate(score_list))
        tuple_score = sorted(tuple_score, key=lambda x: x[1], reverse=True)
        indices_answer = [tuple[0] for tuple in tuple_score]
        score_list = [score_list[i] for i in indices_answer]
        answer_list = [answer_list[i] for i in indices_answer]

        if not score_list:
            return ["No answer found."]
        return answer_list

    def _answers_from_docs(
        self, docs: List[str], question: str
    ) -> Tuple[List[str], List[float], List[str]]:
        """
        Extract answers from a list of documents using a question.

        This function takes a list of documents (`docs`) and a question. It processes
        each document, identifies potential answers to the question, and returns the
        answers, their corresponding scores, and the sources files of the answers.

        Args:
            docs (List[str]): A list of documents to search for answers.
            question (str): The question for which answers are being sought.

        Returns:
            Tuple[List[str], List[float], List[str]]: A tuple containing:
                - List[str]: A list of extracted answers.
                - List[float]: A list of scores associated with each answer.
                - List[str]: A list of sources indicating where each answer was found.

        The function uses tokenization, model inference, and score filtering to identify
        relevant answers. It considers language compatibility and a minimum score
        threshold to include an answer in the results.

        Note:
        - The function may return empty lists for answers, scores, and sources if no
        satisfactory answers are found by the model.
        """
        answers, scores, sources = [], [], []
        for doc in docs:
            content = doc.page_content
            source = os.path.basename(doc.metadata["source"])

            inputs = self.tokenizer.encode_plus(
                question,
                content,
                add_special_tokens=True,
                max_length=self.max_seq_len,
                truncation=True,
                return_tensors="pt",
            ).to(DEVICE)
            input_ids = inputs["input_ids"].tolist()[0]

            answer_start_scores, answer_end_scores = self.model(
                **inputs, return_dict=False
            )
            answer_start_score = torch.max(answer_start_scores).item()

            answer_start = torch.argmax(answer_start_scores)
            answer_end = torch.argmax(answer_end_scores) + 1
            answer = self.tokenizer.decode(input_ids[answer_start:answer_end])
            no_special_token_answer = re.sub(PATTERN, "", answer).strip()

            if (
                no_special_token_answer
                and (answer_start_score > self.min_score)
                and (
                    langdetect.detect(no_special_token_answer)
                    == langdetect.detect(question)
                )
            ):
                answers.append(no_special_token_answer)
                scores.append(answer_start_score)
                sources.append(source)
        return answers, scores, sources

    def _load_model(self) -> Tuple[AutoTokenizer, AutoModelForQuestionAnswering]:
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
        model.to(DEVICE)
        return tokenizer, model

    def run(self, question: str, index: FAISS) -> Tuple[str, List[str]]:
        """
        Uses the model "timpal0l/mdeberta-v3-base-squad2" to retrieve answers for a
        given question.

        Args:
        question (str): The question for which you want to find answers.
        index (list): A list of indices to search for answers in.

        Returns:
        Tuple[str, List[str]]: A tuple containing:
            - str: The answer to the question.
            - List[str]: A list of source files related to the question.

        """
        docs = index.similarity_search(question, k=self.k)
        answers, scores, sources = self._answers_from_docs(docs=docs, question=question)
        answer_list = self._get_top_answers(answers, scores)
        clean_answers = [self._clean_answer(answer, question) for answer in answer_list]
        return ", ".join(clean_answers), utils.clean_source(set(sources))


@st.cache_resource
def load_model() -> DeBerta:
    model = DeBerta()
    return model
