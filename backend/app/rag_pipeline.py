import os
import io
from typing import List, Dict
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from groq import Groq
from .config import settings
from .embeddings import get_embedder
from .retrieval import VectorStore

class RAGPipeline:
    def __init__(self):
        self.embedder = get_embedder()
        self.store = VectorStore(self.embedder)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        self.client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
        self.history: List[Dict] = []

    def ingest_pdfs(self, files: List[tuple]) -> Dict:
        """files: list of (filename, bytes)"""
        total_chunks = 0
        processed_files = []
        
        for name, content in files:
            # Optional: prevent exact duplicates from being added multiple times
            if name in self.store.list_sources():
                continue 

            reader = PdfReader(io.BytesIO(content))
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
            chunks = self.splitter.split_text(text)
            docs = [{"text": c, "source": name, "chunk_id": i} for i, c in enumerate(chunks)]
            self.store.add_documents(docs)
            total_chunks += len(docs)
            processed_files.append(name)
            
        return {"documents": len(processed_files), "chunks": total_chunks}

    def _build_prompt(self, question: str, contexts: List[Dict]) -> str:
        ctx = "\n\n".join(
            f"[{i+1}] Source: {c['source']}\n{c['text']}"
            for i, c in enumerate(contexts)
        )
        return f"""You are a document QA assistant. Answer ONLY from the context.
If the answer is not in the context, say "I don't have enough information in the provided documents."
Cite sources using [1], [2], etc.

Context:
{ctx}

Question: {question}

Answer:"""

    def answer(self, question: str, allowed_sources: List[str] = None) -> Dict:
        # Pass the filter down to the vector store
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
        answer = resp.choices[0].message.content
        return {
            "answer": answer,
            "sources": [
                {"source": c["source"], "text": c["text"][:400], "score": round(c["score"], 3)}
                for c in contexts
            ],
        }

pipeline = RAGPipeline()