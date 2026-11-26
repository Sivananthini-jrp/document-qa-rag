# Intelligent Document QA & Research System (RAG)

A full-stack, production-ready Retrieval-Augmented Generation (RAG) application. Upload PDF documents, select specific files, and ask questions to get accurate answers with grounded source citations.

**[Live Demo](https://document-qa-rag.onrender.com)** *(Replace with your actual frontend link)*

---

## Features

- **Multi-PDF Upload:** Drag and drop multiple PDFs for instant text extraction and indexing.
- **Document Isolation:** Select or deselect specific documents in the UI to restrict the AI's search context. 
- **Semantic Retrieval:** Uses Google's `gemini-embedding-001` and FAISS for lightning-fast vector similarity search.
- **Grounded Generation:** Answers are generated using Groq (LLaMA 3), strictly based on the provided context to prevent hallucinations.
- **Source Citations:** Every answer includes expandable citations showing the exact document and text chunk used.
- **Document Management:** Delete old or irrelevant documents directly from the UI, rebuilding the vector index on the fly.
- **Modern UI:** Beautiful, responsive, glassmorphism dark theme built with React and Vite.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React, Vite, Vanilla CSS |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **AI / LLM** | Groq API (LLaMA 3.1), Google Gemini (Embeddings) |
| **Vector Database** | FAISS (Facebook AI Similarity Search) |
| **Document Parsing** | PyPDF, LangChain Text Splitters |
| **Deployment** | Render (Docker for Backend, Static Site for Frontend) |

---

## Architecture & Workflow

1. **Ingestion:** User uploads PDFs → Text is extracted → Split into overlapping chunks.
2. **Embedding:** Chunks are sent to the Gemini API to generate 768-dimensional vector embeddings.
3. **Storage:** Vectors and text metadata are stored in an in-memory FAISS index.
4. **Retrieval:** User asks a question → Question is embedded → FAISS finds the most relevant chunks (filtered by user's selected documents).
5. **Generation:** Top chunks + User question are sent to Groq API → AI generates a cited answer.

---

## 🚀 Local Setup

### Prerequisites
- **Python 3.11** (Required! Python 3.12+ lacks pre-compiled wheels for some AI dependencies).
- **Node.js v20+**
- API Keys for [Groq](https://console.groq.com/keys) and [Google AI Studio](https://aistudio.google.com/apikey).

### 1. Backend Setup
```bash
cd backend
# Create and activate virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
