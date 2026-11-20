from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from .config import settings

@lru_cache(maxsize=1)
def get_embedder():
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )