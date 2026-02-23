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
from sqlmodel import select

from meridiano import config_base as config
from meridiano import database
from meridiano.utils import format_datetime, scrape_single_article_details

def index():
    """Index page content."""


def main():
    """Main Streamlit application."""
    st.title("Meridiano - Monitoramento de Desinformação")
    st.markdown(
        """
        Bem-vindo ao Meridiano, um sistema de monitoramento de desinformação que utiliza inteligência artificial para analisar e classificar notícias. 
        Este projeto é uma iniciativa acadêmica e tem como objetivo fornecer insights sobre a qualidade da informação disponível na internet, ajudando a identificar notícias falsas e enganosas.
        """
    )
    


if __name__ == "__main__":
    database.init_db()
    main()
