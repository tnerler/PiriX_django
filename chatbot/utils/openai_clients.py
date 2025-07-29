from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt
from langchain_openai import OpenAIEmbeddings

load_dotenv()

@retry(wait=wait_random_exponential(min=1,max=30),stop=stop_after_attempt(5))
def _init_llm():
    return init_chat_model(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        top_p=0.9
    )

def get_llm():
    try:
        return _init_llm()
    except Exception as e:
        print(f"[!] LLM başlatılırken hata: {e}")
        raise

@retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(5))
def _init_embedding_model():
    """OpenAI Embeddings modelini başlatır."""
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=os.getenv("OPENAI_API_KEY")
    )

def get_embedding_model():
    try:
        return _init_embedding_model()
    except Exception as e:
        print(f"[!] Embedding modeli başlatılırken hata: {e}")
        raise