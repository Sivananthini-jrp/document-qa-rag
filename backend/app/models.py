from pydantic import BaseModel
from typing import List, Optional

class AskRequest(BaseModel):
    question: str
    allowed_sources: Optional[List[str]] = None  # If None, search all

class Source(BaseModel):
    source: str
    text: str
    score: float

class AskResponse(BaseModel):
    answer: str
    sources: List[Source]