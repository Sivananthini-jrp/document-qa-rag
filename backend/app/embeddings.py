import os
from google import genai
from google.genai import types
from functools import lru_cache

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@lru_cache(maxsize=1)
def get_embedder():
    if not client:
        raise ValueError("GEMINI_API_KEY not configured")
        
    class GeminiEmbedder:
        def embed_documents(self, texts):
            prepared_texts = [f"title: none | text: {t}" for t in texts]
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=prepared_texts,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=768
                )
            )
            return [e.values for e in response.embeddings]

        def embed_query(self, text):
            prepared_text = f"task: question answering | query: {text}"
            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=prepared_text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                    output_dimensionality=768
                )
            )
            return response.embeddings[0].values

    return GeminiEmbedder()