# settings, env vars
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
from langchain_ollama import OllamaLLM


# Load .env file into environment
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
COLLECTION_NAME = "documents"
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
ollama_model = os.getenv("OLLAMA_MODEL")
ollama_base_url = os.getenv("OLLAMA_BASE_URL")

# Create MongoDB client
mongo_client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

# Qdrant client
qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
    timeout=30,  # optional: avoid hanging
)


ollama_llm = OllamaLLM(
    model=ollama_model,
    base_url=ollama_base_url,
    temperature=0.7
)