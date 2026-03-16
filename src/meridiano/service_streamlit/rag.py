""" Vou pegar as URLs que fiz scraping do banco de dados e vou carregar através do WebBaseLoader.
    Depois, basta realizar o processo de chunking e criar os embeddings, para depois alimentar a base de dados de vetores."""

import os

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import AgentState, create_agent
from langchain_core.prompts import PromptTemplate
from langchain.agents.middleware import dynamic_prompt, ModelRequest

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

       self.prompt = None

       self.vector_store = None

       self.documents = []

       self.qa_chain = None

    @dynamic_prompt
    def prompt_with_context(self, request: ModelRequest, state: AgentState) -> str:
        """ Inject context into state messages """
        last_query = request.state["messages"][-1].text
        retrieved_docs = self.vector_store.similarity_search(last_query, k=5)

        # Format retrieved documents into a single string to inject into the prompt
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

        # Get the base prompt template and replace {feed_profile} if it exists
        system_message = self.prompt.replace("{context}", docs_content)

        return system_message


    # Carrega os parametros para dentro do nosso modelo de linguagem.
    def load_articles_feed(self, feed_profile, effective_config):
        """
        articles = database.get_all_articles(feed_profile=feed_profile)
        chat_prompt = getattr(effective_config, "PROMPT_CHATBOT_RESPONSE", config.PROMPT_CHATBOT_RESPONSE)
        chat_prompt = chat_prompt.replace("{feed_profile}", feed_profile) if "{feed_profile}" in chat_prompt else chat_prompt

        if not articles:
            print(f"No articles found for profile '{feed_profile}'.")
            return False

        # Preciso carregar várias urls para realizar o processo de chunking e criação de embeddings. O WebBaseLoader é a melhor opção para isso, pois ele é capaz de lidar com múltiplas URLs e extrair o conteúdo de forma eficiente.
        urls = [article['url'] for article in articles]
        loader = WebBaseLoader(web_paths=urls)
        documents = loader.load()
        """

        # Get articles *for check facts*
        articles = database.get_articles_for_briefing(config.BRIEFING_ARTICLE_LOOKBACK_HOURS, feed_profile)

        if not articles or len(articles) < config.MIN_ARTICLES_FOR_BRIEFING:
            print(
                f"Not enough recent articles ({len(articles)}) for profile '{feed_profile}'. "
                f"Min required: {config.MIN_ARTICLES_FOR_BRIEFING}."
            )
            return False
        
        # Prepare data for splitting and embedding
        article_ids = [a["id"] for a in articles]
        summaries = [a["processed_content"] for a in articles]
        embeddings = [json.loads(a["embedding"]) for a in articles if a["embedding"]]  # Load JSON string

        if len(embeddings) != len(articles):
            print("Warning: Some articles selected for briefing are missing embeddings. Proceeding with available ones.")
            # Filter articles, summaries, ids to match embeddings
            valid_indices = [i for i, a in enumerate(articles) if a["embedding"]]
            articles = [articles[i] for i in valid_indices]
            article_ids = [article_ids[i] for i in valid_indices]
            summaries = [summaries[i] for i in valid_indices]
            # embeddings are already filtered

        if len(embeddings) < config.MIN_ARTICLES_FOR_BRIEFING:
            print(
                f"Not enough articles ({len(embeddings)}) with embeddings to cluster. "
                f"Min required: {config.MIN_ARTICLES_FOR_BRIEFING}."
            )
            return False

        self.documents = [Document(page_content=s, metadata={"article_id": aid}) for s, aid in zip(summaries, article_ids)]

        # Split documents into chunks and create vector store
        texts = self.text_splitter.split_documents(documents=self.documents)

        # Carrying the texts splitted in a vector store
        self.vector_store = FAISS.from_documents(texts, self.embedding)

        # Now, we need to create the prompt template for the chatbot
        # 1. We take the base prompt and replace the {feed_profile} variable with the actual feed profile name
        self.prompt = getattr(effective_config, "PROMPT_CHATBOT_RESPONSE", config.PROMPT_CHATBOT_RESPONSE)

        
        # 2. Now we create the prompt with the variables input
        self.qa_chain = create_agent(self.llm, tools=[], middleware=[self.prompt_with_context], verbose=True)

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
