""" Vou pegar as URLs que fiz scraping do banco de dados e vou carregar através do WebBaseLoader.
    Depois, basta realizar o processo de chunking e criar os embeddings, para depois alimentar a base de dados de vetores."""

import os
import time

import litellm

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import create_agent
from langchain.tools import tool

from meridiano import config_base as config  # Load base config first
from meridiano import database

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

embedding_client = {
    "api_base": os.getenv("EMBEDDING_API_BASE_URL"),
}

class LLMService:
    def __init__(self, effective_config):
        self.eff_conf = effective_config
        self.chat_model = getattr(effective_config, "LLM_CHAT_MODEL", "deepseek/deepseek-chat")
        self.prompt_template = getattr(effective_config, "PROMPT_BY_CATEGORY", config.PROMPT_BY_CATEGORY)
        self.prompt_template = self.prompt_template["zero-shot"] if isinstance(self.prompt_template, dict) else self.prompt_template

    def call_llm_chat(self, prompt, model=config.LLM_CHAT_MODEL, system_prompt=None):
        """Calls the LLM API (Deepseek, Ollama, etc)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        completion_kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7,
        }

        # Only pass api_base if it's set and we are NOT using Ollama (which has its own default/env var)
        # or if we want to support a custom OLLAMA_API_BASE env var handled by litellm.
        # If the model is 'ollama/...', litellm looks for OLLAMA_API_BASE or defaults to localhost:11434.
        # We don't want to pass the DeepSeek/OpenAI API base URL to Ollama.
        if not str(model).startswith("ollama"):
            if client["api_base"]:
                completion_kwargs["api_base"] = client["api_base"]
        else:
            # Explicitly pass OLLAMA_API_BASE if set, to ensure litellm uses it
            ollama_base = os.getenv("OLLAMA_API_BASE")
            if ollama_base:
                completion_kwargs["api_base"] = ollama_base
                # print(f"DEBUG: Using Ollama API Base: {ollama_base}")

        try:
            response = litellm.completion(**completion_kwargs)
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error calling Deepseek Chat API: {e}")
            # Implement retry logic or better error handling here if needed
            time.sleep(1)  # Basic backoff
            return None
    
    def answer_question(self, user_question):
        #1. Format the potentially profile-specific message prompt
        prompt = self.prompt_template.format(
            message=user_question
        )
        answer = self.call_llm_chat(prompt, model=self.chat_model)

        if not answer:
            print(f"Skipping message due to answer error.")
            return "Descupe, parece que houve um erro ao tentar processa a sua mensagem."
        
        return answer
        