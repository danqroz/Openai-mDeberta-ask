from models import duck_go
import streamlit as st


def sidebar():
    with st.sidebar:
        url = st.text_input("Your url here!", "https://example.com")
        submitted = st.button("Confirm")
        if url and submitted:
            with st.spinner("Url submitted, loading model..."):
                url = duck_go.clean_url(url)
                st.session_state["chat_model"] = duck_go.load_model()
                st.session_state["translate_chain"] = duck_go.load_translate_chain()
                st.session_state["url"] = url
                st.session_state["site_language"] = duck_go.get_languages(url=url)


def _ask_duck_go(url, query, chat_model):
    answer = duck_go.run(
        url=url,
        query=query,
        chat_model=chat_model,
        user_lang=st.session_state["user_language"],
    )
    return {"role": "Duck-go_Assistant", "content": answer, "sources": url}


def update_tranlated_prompt(site_lang):
    st.session_state["translate_chain"] = duck_go.check_chain_language(
        chain=st.session_state["translate_chain"], language=site_lang
    )


def main():
    sidebar()
    st.title("💬 Fale Com Seu Site")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "Site_Assistant",
                "content": "Como posso ajudar?",
                "sources": "code",
            }
        ]
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if query := st.chat_input():
        if "user_language" not in st.session_state:
            user_language = duck_go.get_languages(query=query)
            st.session_state["user_language"] = user_language

        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").write(query)

        if st.session_state["user_language"] != st.session_state["site_language"]:
            update_tranlated_prompt(st.session_state["site_language"])
            query = duck_go.translate_query(query, st.session_state["translate_chain"])

        if "url" not in st.session_state:
            st.info("Please, insert a link to continue.")
            st.stop()
        with st.spinner("Please wait a moment..."):
            model_response = _ask_duck_go(
                url=st.session_state["url"],
                query=query,
                chat_model=st.session_state["chat_model"],
            )
            st.session_state.messages.append(model_response)
            st.chat_message("assistant").write(f"{model_response['content']}")


if __name__ == "__main__":
    main()
