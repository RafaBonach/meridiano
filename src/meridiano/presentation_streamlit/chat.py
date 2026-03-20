import streamlit as st
from meridiano.service_streamlit.rag import RAGService
from meridiano import database

def show():
    st.header("💬 Chatbot")

    if database.get_total_article_count() == 0:
        st.write("Nenhum artigo encontrado na base de dados. Por favor, adicione artigos para que o chatbot possa utilizá-los como base de conhecimento.")
        return

    if "rag_service" not in st.session_state:
        st.session_state.rag_service = RAGService()
        st.session_state.rag_service.load_articles_feed(st.session_state.feed_profile_name, st.session_state.effective_config)


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Digite sua pergunta aqui..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                response = st.session_state.rag_service.answer_question(prompt)
                st.write(response[-1].content)
                st.session_state.messages.append({"role": "assistant", "content": response[-1].content})

    if st.button("🗑 Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()
    
