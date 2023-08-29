from models import ask_site

import streamlit as st


if "site_chain" not in st.session_state:
    st.session_state["site_chain"] = None


def _scrape_handler(site, scrape):
    if scrape:
        urls = ask_site.get_urls(site)
        st.warning(
            'Ao marcar a opção "Todo o site" será feito a leitura de todas as\
            páginas do site.',
            icon="⚠️",
        )
        st.session_state["site_chain"] = ask_site.load_site_chain(site=urls)
    else:
        st.session_state["site_chain"] = ask_site.load_site_chain(
            site=[site],
        )
    return None


def sidebar():
    with st.sidebar:
        site = st.text_input("Coloque seu site aqui", "https://example.com")
        scrape = st.checkbox("Todo o site", key="scrape")
        submitted = st.button("Confirmar")
        if site and submitted:
            with st.spinner("Carregando o modelo..."):
                _scrape_handler(site, scrape)


def _ask_site(chain, query):
    answer, sources = ask_site.run(chain, query)
    return {"role": "Site_Assistant", "content": answer, "sources": sources}


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
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").write(query)

        if not st.session_state["site_chain"]:
            st.info("Por favor, insira um link para continuar.")
            st.stop()

        model_response = _ask_site(chain=st.session_state["site_chain"], query=query)

        st.session_state.messages.append(model_response)
        st.chat_message("assistant").write(f"{model_response['content']}")

        st.info(f"Essa resposta foi retirada de {model_response['sources']}", icon="ℹ️")


if __name__ == "__main__":
    main()
