import os

import openai
import streamlit as st


def sidebar():
    with st.sidebar:
        api_key = st.text_input(
            "OpenAI API Key", key="chatbot_api_key", type="password"
        )
        if api_key:
            os.environ["OPENAI_API_KEY"] = st.session_state["chatbot_api_key"]

        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
        "[View the source code](https://github.com/danqroz/QA-doc-and-site)"
    return None


def main():
    sidebar()
    st.title("💬 Chatbot")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if query := st.chat_input():
        if not st.session_state["chatbot_api_key"]:
            st.info("Please enter an API key to proceed.")
            st.stop()
        os.environ["OPENAI_API_KEY"] = st.session_state["chatbot_api_key"]
        openai.api_key = st.session_state["chatbot_api_key"]
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").write(query)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=st.session_state.messages
        )
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.chat_message("assistant").write(msg.content)


if __name__ == "__main__":
    main()
