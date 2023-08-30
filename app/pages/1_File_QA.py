from models import create_knowledge_base, openai_model, mdeberta, utils

import os
from io import StringIO
import streamlit as st
from streamlit_toggle import st_toggle_switch


if "openai_change" not in st.session_state:
    st.session_state["openai_change"] = 1

if "huggingf_change" not in st.session_state:
    st.session_state["huggingf_change"] = 1

if os.environ.get("OPENAI_API_KEY"):
    openai_chain = openai_model.load_chain(st.session_state["openai_change"])

index_hf = mdeberta.load_indexes(index_change=st.session_state["huggingf_change"])

mdeberta_tokenizer, mdeberta_model = mdeberta.load_model()

avatars = {
    "user": "\U0001F600",
    "chatgpt": "\U0001F916",
    "mdeberta": "\U0001F47D",
    "assistant": "\U0001F4BB",
}

embedding_models = {
    "HuggingFace Embedding": "huggingf",
    "ChatGPT Embedding": "openai",
    "All": "Todos",
}


def _select_index_names():
    selected_indexes = [
        value
        for index, value in embedding_models.items()
        if st.checkbox(index, key=index)
    ]
    if "Todos" in selected_indexes:
        selected_indexes = list(embedding_models.values())[:-1]
    return selected_indexes


def _save_files(uploaded_files):
    for uploaded_file in uploaded_files:
        path = os.path.join(utils.DATA_PATH, f"{uploaded_file.name}")
        if uploaded_file.type.split(os.sep)[1] == "pdf":
            utils.pdf_to_txt(uploaded_file, path)
        else:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(string_data)
    return None


def _create_index_for_files(selected_indexes):
    for index_name in selected_indexes:
        st.session_state[f"{index_name}_change"] += 1
        with st.spinner(f"Generating indexes for the {index_name} embeddings"):
            create_knowledge_base.create_index(index_name)
    utils.remove_files()
    st.info("Generated Embeddings", icon="🔥")


def _ask_gpt(query):
    answer, sources = openai_model.run(openai_chain, query)
    return {"role": "File_Assistent", "content": answer, "sources": sources}


def _ask_mdeberta(query):
    answer, sources = mdeberta.run(
        mdeberta_tokenizer,
        mdeberta_model,
        query,
        index=index_hf,
    )
    return {"role": "mdeberta", "content": answer, "sources": sources}


def generate_response(query, model_name):
    if model_name == "mdeberta":
        return _ask_mdeberta(query)
    return _ask_gpt(query)


def _no_model_selected_handler():
    no_model_selected_answer = {
        "role": "assistant",
        "content": "Oops! No model has been selected.\
                    Please choose a model from the left-hand menu.",
        "sources": "code",
    }
    st.session_state.messages.append(no_model_selected_answer)
    st.chat_message("assistant").write(no_model_selected_answer["content"])


def _no_embeddings_selected_handler(selected_embeddings):
    if not selected_embeddings:
        st.error(
            "Please, you need to select an embedding model",
            icon="🚨",
        )
        st.stop()


def _no_api_key_handler():
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("Ops, it looks like you don't provide an OpenAI Key", icon="🚨")
        st.stop()


def _sidebar():
    with st.sidebar:
        st.write("Please choose at least one model:")
        options = ["mDeBERTa", "ChatGPT"]
        models_selected = [
            name.lower() for name in options if st_toggle_switch(name, label_after=True)
        ]
        if "chatgpt" in models_selected:
            _no_api_key_handler()

        with st.expander("Upload your files"):
            selected_embeddings = _select_index_names()
            uploaded_files = st.file_uploader(
                "Choose files", accept_multiple_files=True, type=["pdf", "txt"]
            )

            submitted = st.button("Upload")
            if uploaded_files is not None and submitted:
                _no_embeddings_selected_handler(selected_embeddings)

                _save_files(uploaded_files)
                _create_index_for_files(selected_embeddings)
                submitted = False
    return models_selected


def main():
    models_selected = _sidebar()
    st.title("💬 Talk to your document")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "fileQA_assistant", "content": "How can I help you?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if query := st.chat_input():
        if not models_selected:
            _no_model_selected_handler()
        else:
            st.session_state.messages.append({"role": "user", "content": query})
            st.chat_message("user", avatar=avatars["user"]).write(query)
            for model in models_selected:
                model_response = generate_response(query=query, model_name=model)
                st.session_state.messages.append(model_response)
                msg = st.chat_message("assistant", avatar=avatars[model])
                msg.write(f"{model.upper()}:")
                msg.write(f"{model_response['content']}")

            st.info(
                f"This answer was taken from: {model_response['sources']}", icon="ℹ️"
            )


if __name__ == "__main__":
    main()
