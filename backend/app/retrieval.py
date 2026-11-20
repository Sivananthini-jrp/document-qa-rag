import faiss
import numpy as np
from typing import List, Dict

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
        
        # Track unique filenames
        for c in chunks:
            self.doc_sources.add(c["source"])

        self.index.add(vectors)
        self.docs.extend(chunks)

    def search(self, query: str, k: int = 4, allowed_sources: List[str] = None):
        if self.index is None or not self.docs:
            return []
            
        # Search more results than requested, then filter (since FAISS doesn't do metadata filtering natively)
        search_k = min(k * 10, len(self.docs)) if allowed_sources else k
        
        q = np.array([self.embedder.embed_query(query)], dtype="float32")
        scores, idxs = self.index.search(q, search_k)
        
        results = []
        for score, i in zip(scores[0], idxs[0]):
            if i == -1:
                continue
            doc = self.docs[i]
            # If allowed_sources is provided, skip documents not in the list
            if allowed_sources and doc["source"] not in allowed_sources:
                continue
                
            d = dict(doc)
            d["score"] = float(score)
            results.append(d)
            
            if len(results) >= k:
                break
                
        return results

    def delete_source(self, source_name: str):
        """Removes a specific file and rebuilds the index."""
        if source_name not in self.doc_sources:
            return False

        # Filter out the deleted document
        self.docs = [d for d in self.docs if d["source"] != source_name]
        self.doc_sources.remove(source_name)

        # Rebuild FAISS index
        if not self.docs:
            self.index = None
        else:
            texts = [c["text"] for c in self.docs]
            vectors = np.array(self.embedder.embed_documents(texts), dtype="float32")
            self.index = faiss.IndexFlatIP(vectors.shape[1])
            self.index.add(vectors)
        return True

    def list_sources(self):
        """Returns a list of all uploaded filenames."""
        return list(self.doc_sources)

    def clear(self):
        self.index = None
        self.docs.clear()
        self.doc_sources.clear()