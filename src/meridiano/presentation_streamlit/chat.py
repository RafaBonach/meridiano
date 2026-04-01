import streamlit as st
from meridiano.service_streamlit.rag import LLMService
from meridiano import database

def show():
    st.header("💬 Chatbot")

    if "rag_service" not in st.session_state:
        st.session_state.rag_service = LLMService(effective_config=st.session_state.effective_config)


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Digite sua pergunta aqui..."):
        st.chat_message("user").write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                response = st.session_state.rag_service.answer_question(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("🗑 Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()
    
