# 🦜️🔗 Langchain "converse com..." Demo

![Python](https://img.shields.io/badge/python-3.10-blue)

- [🦜️🔗 Langchain "converse com..." Demo](#️-langchain-converse-com-demo)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Main](#main)
  - [Ask File / Talk With Your Documents](#ask-file--talk-with-your-documents)
  - [Website QA / Talk With Your Website](#website-qa--talk-with-your-website)
  - [Duck Duck go](#duck-duck-go)

The goal of this project is to explore some functions of Langchain, compare ChatGPT responses with those obtained from smaller models (mDeBERTa), and test a cheaper way to use ChatGPT to answer questions related to a website.

## Introduction

The models used in this project were ChatGPT and mDeBERTa. The latter was used only to answer questions based on provided documents.

In this application, we have a variety of QA (question answering) models, which means that each page has the function of answering questions based on a context provided by the user themselves. These contexts can come from files or websites.

Nearly all functionalities in this project follow the well-known QA flow: 1. The texts are broken down into chunks and transformed into embeddings. 2. An indexer creates indexes for these embeddings and stores them in what we call a knowledge base. 3. When the user asks a question, a semantic search is performed on our knowledge base, which returns the most likely snippets to contain the answer (ranked results). 4. These snippets, along with the user's question, are then sent to the QA model, which returns the final answer to the user. The image below illustrates this flow.

<div style="text-align: center;"> 
    <img src="assets\qa_flow.png" alt="QA flow">
</div>
<p style="text-align: center;"> 
    Question Answering flow
</p>

I used an identical system to answer questions based on a website provided by the user. In this scenario, the document that composes the embedding is the content of the link provided by the user.

The only exception is Duck Duck Go. In this case, a web search is performed using the Duck Duck Go API with the constraint that the result must have the same domain as the one specified by the user. More details about the system can be found in the [Duck Duck go](#duck-duck-go) section.

## Installation

In this project, we used pipenv and docker. If you don't have Docker installed, here are the installation links for [linux](https://docs.docker.com/desktop/install/linux-install/) and [windows](https://docs.docker.com/desktop/install/windows-install/). If you already have Docker installed, simply run the following command in the terminal:

```console
docker-compose build
```

The process may take a while when it is executed for the first time. Then run:

```console
docker-compose up
```

If everything goes well, you will see the message "_You can now view your Streamlit app in your browser._". Then just type in your browser: "<http://localhost:8001/>" to access the application.

## Main

The main page is simply the chatgpt-3.5 turbo. You need to enter your OpenAI Key to be able to use it.

![main](https://github.com/danqroz/QA-doc-and-site/assets/75531272/ec2b4d92-340a-4bf7-9f17-174d21063425)

## Ask File / Talk With Your Documents

On _Ask File_ page, you can chat with this README that already had generated indexes and it is available for the models. You can ask any question about this project.

You can also upload documents up to 200mb in .txt or .pdf format. To upload, you need to select one or more embedding models. The "HuggingFace embedding" will be used to generate the embeddings that will be indexed and available for mDeBERTa. The "OpenAI embedding" will be available for ChatGPT.

You can also upload multiple documents at once. After successfully submitting the files, you can already chat with the documents, both new and old ones for which you have already generated indexes. At the end, the source from which the answer was taken is provided.

## Website QA / Talk With Your Website

In this section, the user must provide a URL before asking questions. By default, only the provided page will be scraped, but the user has the option to select "_Entire Website_" where the entire website will be scraped. Keep in mind that this action can be costly, as the entire website will be embedded using the "text-embedding-ada-002" model from OpenAI.

After entering a valid URL and deciding whether or not to use the "_Entire Website_", you can ask questions about the provided website.

## Duck Duck go

The high cost of processing an entire website, as mentioned in the previous section, can be bypassed by using a free embedding model, initially. For example, we could use the model that generates embeddings for mDeBERTa: ["intfloat/multilingual-e5-base"](https://huggingface.co/intfloat/multilingual-e5-base).

However, I decided to do this test using the Duck-Duck-Go Search. Since we don't have an intelligent model like ChatGPT to automatically translate the information, we have to check first if the language of the provided website and the language in which the user wrote the question are the same. If necessary, translate the user's question to the same language as the website.

The flow can then be described in the following steps. 1. Translate the user's query, if necessary. 2. Use the Duck Duck Go API to search the user's question on the web with the following restriction: the answer must be in the same domain as the one specified by the user. 3. We pass the snippets (these are similar to the returned by semantic search in QA flow) with the answers found by Duck Duck Go and the user's question to ChatGPT. 4. The model takes care of finding the answer and translating it back, if necessary, to the user's language.

<div style="text-align: center;">
    <img src="assets\duck_go_flow.png" alt="Duck Go flow">
</div>
<p style="text-align: center;"> 
    Duck-Duck-go Search flow
</p>

Note that in this way, we do not generate the semantic indexes. Duck Duck Go itself takes care of searching for the information we want. Although the model seems to work well, it is slower than QA flow. This is because a knowledge base with indexes is not created to perform the semantic search. In other words, the entire flow is repeated for each question.

