# embeddings.py
import os
from typing import List
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_PATH = "./all-MiniLM-L6-v2"


def ensure_model_downloaded(model_name: str, model_path: str):
    """
    Ensure that the embedding model is downloaded locally.
    If not found, it downloads and saves the model.
    """
    if not os.path.exists(model_path):
        print(f"📥 Downloading model '{model_name}' to '{model_path}' ...")
        model = SentenceTransformer(model_name)
        model.save(model_path)
        print("✅ Model downloaded and saved locally.")
    else:
        print("✅ Model already exists locally.")


# Ensure model availability
ensure_model_downloaded(MODEL_NAME, MODEL_PATH)

# Load model always from local path
embedding_model = SentenceTransformer(MODEL_PATH)


# def get_embedding(text: str) -> List[float]:

#     """
#     Generate embedding for a single text string.
#     """
#     embedding = embedding_model.encode([text])[0]
#     return embedding.tolist()


# def get_embeddings(texts: List[str]) -> List[List[float]]:
#     """
#     Generate embeddings for a list of text strings.
#     """
#     embeddings = embedding_model.encode(texts)
#     return embeddings.tolist()
