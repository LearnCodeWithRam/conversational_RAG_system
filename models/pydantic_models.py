from pydantic import BaseModel
from typing import List, Optional
import datetime
from dataclasses import dataclass

class QuestionRequest(BaseModel):
    user_id: str
    question: str
    top_k: Optional[int] = 4

class Reference(BaseModel):
    document: str
    page: Optional[int]
    chunk_id: str
    content_snippet: str

class QuestionResponse(BaseModel):
    answer: str
    reasoning: str
    references: List[Reference]
    suggestions: List[str]

@dataclass
class DocumentChunk:
    document_id: str
    filename: str
    chunk_id: str
    chunk_text: str
    page_number: Optional[int]
    upload_timestamp: datetime.datetime