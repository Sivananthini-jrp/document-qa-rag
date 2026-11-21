import os
import io
from typing import List, Dict
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from groq import Groq
from google import genai
from google.genai import types
import faiss
import numpy as np
from .config import settings

class GeminiEmbedder:
    def __init__(self):
        # Uses GEMINI_API_KEY from environment
        from .config import settings
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY) 

    def embed_documents(self, texts):
        prepared_texts = [f"title: none | text: {t}" for t in texts]
        response = self.client.models.embed_content(
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
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=prepared_text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=768
            )
        )
        return response.embeddings[0].values

class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.index = None
        self.docs: List[Dict] = []
        self.doc_sources = set()

    def add_documents(self, chunks: List[Dict]):
        texts = [c["text"] for c in chunks]
        vectors = self.embedder.embed_documents(texts)
        vectors = np.array(vectors, dtype="float32")

        if self.index is None:
            self.index = faiss.IndexFlatIP(vectors.shape[1])
        
        for c in chunks:
            self.doc_sources.add(c["source"])

        self.index.add(vectors)
        self.docs.extend(chunks)

    def search(self, query: str, k: int = 4, allowed_sources: List[str] = None):
        if self.index is None or not self.docs:
            return []
            
        search_k = min(k * 10, len(self.docs)) if allowed_sources else k
        q = np.array([self.embedder.embed_query(query)], dtype="float32")
        scores, idxs = self.index.search(q, search_k)
        
        results = []
        for score, i in zip(scores[0], idxs[0]):
            if i == -1: continue
            doc = self.docs[i]
            if allowed_sources and doc["source"] not in allowed_sources:
                continue
            d = dict(doc)
            d["score"] = float(score)
            results.append(d)
            if len(results) >= k: break
        return results

    def delete_source(self, source_name: str):
        if source_name not in self.doc_sources: return False
        self.docs = [d for d in self.docs if d["source"] != source_name]
        self.doc_sources.remove(source_name)

        if not self.docs:
            self.index = None
        else:
            texts = [c["text"] for c in self.docs]
            vectors = np.array(self.embedder.embed_documents(texts), dtype="float32")
            self.index = faiss.IndexFlatIP(vectors.shape[1])
            self.index.add(vectors)
        return True

    def list_sources(self):
        return list(self.doc_sources)

    def clear(self):
        self.index = None
        self.docs.clear()
        self.doc_sources.clear()


class RAGPipeline:
    def __init__(self):
        self.embedder = GeminiEmbedder()
        self.store = VectorStore(self.embedder)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

    def ingest_pdfs(self, files: List[tuple]) -> Dict:
        total_chunks = 0
        processed_files = []
        
        for name, content in files:
            if name in self.store.list_sources(): continue 
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
            chunks = self.splitter.split_text(text)
            docs = [{"text": c, "source": name, "chunk_id": i} for i, c in enumerate(chunks)]
            self.store.add_documents(docs)
            total_chunks += len(docs)
            processed_files.append(name)
            
        return {"documents": len(processed_files), "chunks": total_chunks}

    def _build_prompt(self, question: str, contexts: List[Dict]) -> str:
        ctx = "\n\n".join(f"[{i+1}] Source: {c['source']}\n{c['text']}" for i, c in enumerate(contexts))
        return f"""You are a document QA assistant. Answer ONLY from the context.
If the answer is not in the context, say "I don't have enough information in the provided documents."
Cite sources using [1], [2], etc.

Context:
{ctx}

Question: {question}
Answer:"""

    def answer(self, question: str, allowed_sources: List[str] = None) -> Dict:
        contexts = self.store.search(question, k=settings.TOP_K, allowed_sources=allowed_sources)
        if not contexts:
            return {"answer": "I couldn't find anything in the selected documents.", "sources": []}
        if self.client is None:
            return {"answer": "GROQ_API_KEY not configured.", "sources": contexts}

        prompt = self._build_prompt(question, contexts)
        resp = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600,
        )
        return {
            "answer": resp.choices[0].message.content,
            "sources": [{"source": c["source"], "text": c["text"][:400], "score": round(c["score"], 3)} for c in contexts]
        }

pipeline = RAGPipeline()