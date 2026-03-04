# meridiano/app_streamlit.py
"""
    Desenvolver a pagina web do meridiano em streamlit
    Ele deve ter:
    * Uma pagina inicial que será o chatbot
        - O chatbot deverá utilizar os embeddings para seu treinamento.
    - Uma pagina de artigos com todos os artigos processados,
    - Uma pagina de adição de novos artigos a base de dados

    Essa pagina deve ser baseada no modelo flask desenvolvido em /home/rafael/Projetos/meridiano/src/meridiano/app.py
"""
import json
import math
from datetime import date, datetime, timedelta

import os
import markdown
import streamlit as st
from dotenv import load_dotenv

from meridiano import config_base as config
from meridiano import database
from meridiano.utils import format_datetime, scrape_single_article_details, str_to_parser

from meridiano.presentation_streamlit import articles

# --- Setup ---
load_dotenv()

"""
Desenvolver a pagina de scraping, onde o usuário poderá inserir uma URL e o sistema irá realizar o processo de scraping

"""

def main():
    """Main Streamlit application."""
    database.init_db()  # Ensure the database is initialized when the app starts
    arg, feed_profile_name, effective_config = str_to_parser(feed="fake_news", scrape=False, process=False, generate=False, rate=False)

    st.session_state.arg = arg
    st.session_state.feed_profile_name = feed_profile_name
    st.session_state.effective_config = effective_config

    st.set_page_config(page_title="Campus Multiplataforma", page_icon="📰", layout="wide")
    st.title("📰 Campus Multiplataforma - Monitoramento de Desinformação")
    
    with st.sidebar:
        st.header("Modulos")
        mode = st.radio("Selecione o módulo:", ("Chatbot", "Artigos"))

        st.divider()
        
        st.subheader("Configurações")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if mode == "Chatbot":
        if database.get_total_article_count() == 0:
            st.write("Nenhum artigo encontrado na base de dados. Por favor, adicione artigos para que o chatbot possa utilizá-los como base de conhecimento.")
        else:
            st.write("Módulo de Chatbot em desenvolvimento. Em breve, você poderá interagir com nosso assistente de IA para obter análises e insights sobre as notícias processadas.")
    elif mode == "Artigos":
        articles.show()
    



if __name__ == "__main__":
    main()
