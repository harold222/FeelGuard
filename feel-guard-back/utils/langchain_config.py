import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAI

load_dotenv()

# Configuración centralizada para LangChain
class LangChainConfig:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def get_chat_model(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7) -> ChatOpenAI:
        """Obtiene un modelo de chat configurado"""
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=self.openai_api_key,
            max_tokens=200
        )
    
# Instancia global de configuración
langchain_config = LangChainConfig() 