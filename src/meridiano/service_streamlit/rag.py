""" Vou pegar as URLs que fiz scraping do banco de dados e vou carregar através do WebBaseLoader.
    Depois, basta realizar o processo de chunking e criar os embeddings, para depois alimentar a base de dados de vetores."""

import os

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from langchain_community.chains import PebbloRetrievalQA
from langchain_classic.chains.qa_with_sources.base import BaseQAWithSourcesChain

from meridiano.run_briefing import get_deepseek_embedding
from meridiano import config_base as config  # Load base config first
from meridiano import database
from meridiano.models import Article, get_session

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

client = {
    "api_base": os.getenv("LLM_API_BASE_URL"),
}

"""
    Ajustar o processo de RAG para utilizar os artigos do banco de dados
    Verificar se a função load_articles_feed está funcionando corretamente.
"""

# Verificar porque o ollama não está conseguindo acessar o modelo de embedding
class RAGService:
    def __init__(self, embedding_model_name=config.EMBEDDING_MODEL, llm_model_name=config.LLM_CHAT_MODEL):
       self.embedding = OllamaEmbeddings(model=embedding_model_name.removeprefix("ollama/"))

       self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP
            )
       
       self.llm = OllamaLLM(model=llm_model_name.removeprefix("ollama/"))

       self.__prompt__ = None

       self.vector_store = None

       self.qa_chain = None

    # Carrega os parametros para dentro do nosso modelo de linguagem.
    def load_articles_feed(self, feed_profile, effective_config):
        articles = database.get_all_articles(feed_profile=feed_profile)
        chat_prompt = getattr(effective_config, "PROMPT_CHATBOT_RESPONSE", config.PROMPT_CHATBOT_RESPONSE)
        chat_prompt = chat_prompt.replace("{feed_profile}", feed_profile) if "{feed_profile}" in chat_prompt else chat_prompt

        if not articles:
            print(f"No articles found for feed profile '{feed_profile}'.")
            return False
        
        # Preciso carregar várias urls para realizar o processo de chunking e criação de embeddings. O WebBaseLoader é a melhor opção para isso, pois ele é capaz de lidar com múltiplas URLs e extrair o conteúdo de forma eficiente.
        urls = [article['url'] for article in articles]
        loader = WebBaseLoader(web_paths=urls)
        documents = loader.load()

        if not documents:
            print(f"No documents loaded from URLs for feed profile '{feed_profile}'.")
            return False
        
        texts = self.text_splitter.split_documents(documents)

        self.vector_store = FAISS.from_documents(texts, self.embedding)

        self.__prompt__ = PromptTemplate(
            template=chat_prompt,
            input_variables=["context", "user_question"]
        )

        self.qa_chain = BaseQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": self.__prompt__}
        )

        return True

    def answer_question(self, user_question):
        # Faz a pergunta para o modelo de linguagem
        if not self.qa_chain:
            print("QA chain not initialized. Please load articles feed first.")
            return "Desculpe, não posso responder a pergunta no momento. Carregue um feed primeiro"
        
        try:
            result = self.qa_chain.run(user_question)
            return result
        except Exception as e:
            print(f"Error during QA chain execution: {e}")
            return f"Erro ao processar a pergunta: {str(e)}"
