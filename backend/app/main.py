from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import AskRequest, AskResponse
from .rag_pipeline import pipeline

app = FastAPI(title="Document QA RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/documents")
def list_documents():
    """List all unique uploaded document names."""
    return {"documents": pipeline.store.list_sources()}

@app.delete("/documents/{filename}")
def delete_document(filename: str):
    """Delete a document by filename and rebuild the index."""
    success = pipeline.store.delete_source(filename)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document": filename}

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    payload = []
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            continue
        payload.append((f.filename, await f.read()))
    return pipeline.ingest_pdfs(payload)

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    return pipeline.answer(req.question, req.allowed_sources)

@app.post("/reset")
def reset():
    pipeline.store.clear()
    pipeline.history.clear()
    return {"status": "reset"}