""" Vou pegar as URLs que fiz scraping do banco de dados e vou carregar através do WebBaseLoader.
    Depois, basta realizar o processo de chunking e criar os embeddings, para depois alimentar a base de dados de vetores."""

import os
import json

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import AgentState, create_agent
from langchain.tools import tool

from meridiano.run_briefing import get_deepseek_embedding
from meridiano import config_base as config  # Load base config first
from meridiano import database
from meridiano.models import Article, get_session

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Peso usado no reranking de recuperação por veracidade.
# Banco: 1 = verdadeiro, 0 = falso.
VERACITY_WEIGHTS = {
    0: 1.25,
    1: 1.0,
}

client = {
    "api_base": os.getenv("LLM_API_BASE_URL"),
}

# Verificar porque o ollama não está conseguindo acessar o modelo de embedding
class RAGService:
    def __init__(self, embedding_model_name=config.EMBEDDING_MODEL, llm_model_name=config.LLM_CHAT_MODEL):
       self.embedding = OllamaEmbeddings(model=embedding_model_name.removeprefix("ollama/"))

       self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP
            )
       
       self.llm = ChatOllama(model=llm_model_name.removeprefix("ollama/"))

       self.prompt = None

       self.vector_store = None

       self.documents = []

       self.qa_chain = None

    @staticmethod
    def _normalize_veracity(value):
        try:
            if value is None:
                return None
            numeric = int(value)
            return numeric if numeric in (0, 1) else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _veracity_label(value):
        labels = {
            1: "verdadeiro",
            0: "falso",
            None: "desconhecido",
        }
        return labels.get(value, "desconhecido")

    @staticmethod
    def _veracity_weight(value):
        normalized = RAGService._normalize_veracity(value)
        return VERACITY_WEIGHTS.get(normalized, 1.0)

    # Carrega os parametros para dentro do nosso modelo de linguagem.
    def load_articles_feed(self, feed_profile, effective_config):

        # Get articles *for check facts*
        articles = database.get_unprocessed_articles(feed_profile, limit=1000)

        if not articles or len(articles) < config.MIN_ARTICLES_FOR_BRIEFING:
            print(
                f"Not enough recent articles ({len(articles)}) for profile '{feed_profile}'. "
                f"Min required: {config.MIN_ARTICLES_FOR_BRIEFING}."
            )
            return False
        
        # Prepare data for splitting and embedding
        for article in articles:
            if not article.get("raw_content"):
                continue
            
            #load the article content in a document
            document = Document(
                page_content=article["raw_content"],
                metadata={"article_id": article["id"], "veracity": article.get("veracity")},
            )
            self.documents.append(document)

            # Split documents into chunks and create vector store
            texts = self.text_splitter.split_documents(documents=document)

            # Carrying the texts splitted in a vector store
            self.vector_store = FAISS.from_documents(texts, self.embedding)

            # Now, we need to save the vector store in the database.
            if not self.vector_store:
                print(f"Skipping article {article['id']} due to embedding error.")
                continue  # Or store article without embedding if desired

            database.update_article_processing(article["id"], article["raw_content"], self.vector_store)
        
        """ ---------------
        Próximo passo, temos que fazer uma busca de similiridade por embedding.
        O usuário fará uma pergunta e essa pergunta deverá ser convertida em embedding e comparada com os embeddings do banco de dados.
        O resultado dessa busca de similaridade será reordenado por um peso de veracidade, onde os artigos classificados como falsos terão um peso menor e os classificados como verdadeiros terão um peso maior.
        Finalmente, deve ser montado o contexto e elaborado o prompt para o modelo de linguagem.
            ---------------"""
        
        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str):
            """Retrieve information to help answer a query."""
            scored_docs = self.vector_store.similarity_search_with_score(query, k=20)
            reranked_docs = []

            for doc, distance in scored_docs:
                veracity_value = self._normalize_veracity(doc.metadata.get("veracity"))
                veracity_weight = self._veracity_weight(veracity_value)

                # Em FAISS, menor distância representa maior similaridade.
                similarity = 1.0 / (1.0 + float(distance))
                weighted_score = similarity * veracity_weight
                reranked_docs.append((weighted_score, doc))

            reranked_docs.sort(key=lambda item: item[0], reverse=True)
            retrieved_docs = [doc for _, doc in reranked_docs[:5]]

            serialized = "\n\n".join(
                (
                    f"Article ID: {doc.metadata['article_id']}\n"
                    f"Veracity: {self._veracity_label(self._normalize_veracity(doc.metadata.get('veracity')))}\n"
                    f"Content: {doc.page_content}"
                    for doc in retrieved_docs
                )
            )
            return serialized, retrieved_docs

        # Now, we need to create the prompt template for the chatbot
        # 1. We take the base prompt and replace the {feed_profile} variable with the actual feed profile name
        self.prompt = getattr(effective_config, "PROMPT_CHATBOT_RESPONSE", config.PROMPT_CHATBOT_RESPONSE)

        # 2. Now we create the prompt with the variables input
        self.qa_chain = create_agent(self.llm, tools=[retrieve_context], system_prompt=self.prompt)

        return True

    def answer_question(self, user_question):
        # Faz a pergunta para o modelo de linguagem
        if not self.qa_chain:
            print("QA chain not initialized. Please load articles feed first.")
            return "Desculpe, não posso responder a pergunta no momento. Carregue um feed primeiro"
        
        try:
            result = [step["messages"][-1] for step in self.qa_chain.stream(
                {"messages": [{"role": "user", "content": user_question}]},
                stream_mode="values",
            )]
            return result
        except Exception as e:
            print(f"Error during QA chain execution: {e}")
            return f"Erro ao processar a pergunta: {str(e)}"
