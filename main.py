from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import os
import uuid
import datetime
from qdrant_client.http import models

from services.embeddings import embedding_model
from services.ollama_service import ollama_response
from utils.util_module import extract_text_from_pdf, chunk_text, generate_suggestions
from models.pydantic_models import DocumentChunk, QuestionRequest, QuestionResponse, Reference
from config import COLLECTION_NAME, mongo_client, qdrant_client

router = APIRouter()

# Initialize clients
app = FastAPI(title="Conversational RAG Q&A System")

os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Test MongoDB connection
try:
    mongo_client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")

# Initialize database and collections
db = mongo_client.rag_system
documents_collection = db.documents
conversations_collection = db.conversations

# Create indexes for better performance
try:
    # Index for documents collection
    documents_collection.create_index("document_id", unique=True)
    documents_collection.create_index("filename")
    documents_collection.create_index("upload_timestamp")
    
    # Index for conversations collection  
    conversations_collection.create_index("user_id")
    conversations_collection.create_index("timestamp")
    conversations_collection.create_index([("user_id", 1), ("timestamp", -1)])
    
    print("✅ MongoDB indexes created successfully!")
except Exception as e:
    print(f"⚠️ Index creation warning: {e}")


# Create Qdrant collection if not exists
try:
    # Check if collection exists
    collections = qdrant_client.get_collections()
    collection_names = [col.name for col in collections.collections]
    
    if COLLECTION_NAME not in collection_names:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=384,  # all-MiniLM-L6-v2 embedding size
                distance=models.Distance.COSINE
            ),
        )
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' created successfully!")
    else:
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' already exists!")
        
    # Test connection by getting collection info
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)
    print(f"✅ Qdrant connection successful! Collection has {collection_info.points_count} points.")
    
except Exception as e:
    print(f"❌ Qdrant setup failed: {e}")
    print("Please check your Qdrant URL and API key configuration.")



# API Endpoints
@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process PDF or TXT documents"""
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    try:
        content = await file.read()
        document_id = str(uuid.uuid4())
        upload_time = datetime.datetime.utcnow()
        
        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            pages_text = extract_text_from_pdf(content)
            all_text_chunks = []
            
            for text, page_num in pages_text:
                chunks = chunk_text(text)
                for chunk in chunks:
                    chunk_id = str(uuid.uuid4())
                    doc_chunk = DocumentChunk(
                        document_id=document_id,
                        filename=file.filename,
                        chunk_id=chunk_id,
                        chunk_text=chunk,
                        page_number=page_num,
                        upload_timestamp=upload_time
                    )
                    all_text_chunks.append(doc_chunk)
        
        else:  # TXT file
            text = content.decode('utf-8')
            chunks = chunk_text(text)
            all_text_chunks = []
            
            for chunk in chunks:
                chunk_id = str(uuid.uuid4())
                doc_chunk = DocumentChunk(
                    document_id=document_id,
                    filename=file.filename,
                    chunk_id=chunk_id,
                    chunk_text=chunk,
                    page_number=None,
                    upload_timestamp=upload_time
                )
                all_text_chunks.append(doc_chunk)
        
        # Generate embeddings and store in Qdrant
        texts = [chunk.chunk_text for chunk in all_text_chunks]
       
        embeddings = embedding_model.encode(texts)
    

        # Prepare points for Qdrant
        points = []
        for i, chunk in enumerate(all_text_chunks):
            points.append(models.PointStruct(
                id=chunk.chunk_id,
                vector=embeddings[i].tolist(),
                payload={
                    "document_id": chunk.document_id,
                    "filename": chunk.filename,
                    "text": chunk.chunk_text,
                    "page_number": chunk.page_number,
                    "upload_timestamp": chunk.upload_timestamp.isoformat()
                }
            ))
        
        # Upload to Qdrant
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        
        # Store metadata in MongoDB
        document_metadata = {
            "document_id": document_id,
            "filename": file.filename,
            "upload_timestamp": upload_time,
            "chunk_count": len(all_text_chunks),
            "original_content": content.decode('utf-8') if file.filename.endswith('.txt') else "PDF content"
        }
        
        documents_collection.insert_one(document_metadata)
        
        return {
            "message": "Document uploaded successfully",
            "document_id": document_id,
            "filename": file.filename,
            "chunks_created": len(all_text_chunks)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question and get RAG-based answer (Ollama version)"""
    try:
        # 1. Get conversation history
        history = list(conversations_collection.find(
            {"user_id": request.user_id},
            {"_id": 0, "question": 1, "answer": 1}
        ).sort("timestamp", -1).limit(3))
        
        # 2. Generate query embedding
        query_embedding = embedding_model.encode([request.question])

        # 3. Search Qdrant for relevant chunks
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding[0].tolist(),
            limit=request.top_k
        )
        
        # 4. Prepare context (take only top 2 references)
        context_chunks, references = [], []
        for result in search_results[:2]:   # ✅ only top 2
            payload = result.payload
            context_chunks.append(payload["text"])
            references.append(Reference(
                document=payload["filename"],
                page=payload.get("page_number"),
                chunk_id=str(result.id),
                content_snippet=payload["text"][:400] + "..." if len(payload["text"]) > 400 else payload["text"]
            ))
        
        context_text = "\n\n".join(context_chunks)
        history_text = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in reversed(history)])
        
        # 5. Build RAG prompt
        system_prompt = """You are a helpful AI assistant that answers questions based on provided documents. 
        Use the document context to answer questions accurately. If you can't find the answer in the context, say so.
        Provide clear reasoning for your answers."""
        
        user_prompt = f"""Previous conversation:
{history_text}

Document context:
{context_text}

Current question: {request.question}

Please provide a detailed answer based on the document context. Explain your reasoning."""
        
        # 6. Get Ollama response
        answer = ollama_response(system_prompt, user_prompt)

        # 7. Generate reasoning separately
        reasoning_prompt = f"""Based on this question: "{request.question}" and the answer: "{answer}", 
        explain briefly how you arrived at this answer using the provided document context."""
        reasoning = ollama_response(system_prompt="Provide brief reasoning for the given answer.", user_prompt=reasoning_prompt)

        # 8. Generate suggestions
        suggestions = generate_suggestions(request.question, context_text)
        
        # 9. Save conversation in Mongo
        conversations_collection.insert_one({
            "user_id": request.user_id,
            "question": request.question,
            "answer": answer,
            "reasoning": reasoning,
            "timestamp": datetime.datetime.utcnow(),
            "references": [ref.dict() for ref in references]
        })
        
        # 10. Return response
        return QuestionResponse(
            answer=answer,
            reasoning=reasoning,
            references=references,
            suggestions=suggestions
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/history")
async def get_history(user_id: str):
    """Get user's conversation history"""
    try:
        history = list(conversations_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1))
        
        return {"history": history}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        documents = list(documents_collection.find({}, {"_id": 0}))
        return {"documents": documents}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.delete("/clear")
async def clear_system():
    """Clear all documents and conversations"""
    try:
        # Clear MongoDB collections
        documents_collection.delete_many({})
        conversations_collection.delete_many({})
        
        # Clear Qdrant collection
        qdrant_client.delete_collection(COLLECTION_NAME)
        
        # Recreate collection
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        
        return {"message": "System cleared successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing system: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)