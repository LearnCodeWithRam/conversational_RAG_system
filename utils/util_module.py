import PyPDF2
import io
import logging
from fastapi import  HTTPException
from typing import List, Optional
from services.ollama_service import ollama_response


# Utility functions
def extract_text_from_pdf(file_content: bytes) -> List[tuple]:
    """Extract text from PDF and return list of (text, page_number)"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        pages_text = []
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text = page.extract_text()
            pages_text.append((text, page_num))
        return pages_text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting PDF: {str(e)}")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks


def generate_suggestions(question: str, context: str) -> List[str]:
    """Generate follow-up question suggestions using Ollama"""
    try:
        # Build prompt
        system_prompt = "Generate 3 short follow-up questions based on the context and previous question. Return only the questions, one per line."
        user_prompt = f"Question: {question}\nContext: {context[:500]}"

        # Call Ollama
        text = ollama_response(system_prompt, user_prompt)
        
        # Split into lines and clean
        suggestions = text.strip().split("\n")
        return [s.strip("-•123. ").strip() for s in suggestions if s.strip()][:3]

    except Exception:
        return [
            "Can you provide more details?",
            "What are the implications?",
            "Are there any examples?"
        ]