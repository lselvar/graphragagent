from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging
import os
import uuid
from pathlib import Path
from datetime import datetime

from backend.config import settings
from backend.models import (
    DocumentUpload,
    ChatRequest,
    ChatResponse,
    ChatMessage
)
from backend.graph_store import GraphStore
from backend.document_processor import DocumentProcessor
from backend.github_processor import GitHubProcessor
from backend.embeddings import embedding_service
from backend.gemini_agent import GeminiAgent
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="GraphRAG application with Gemini LLM",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
graph_store: GraphStore = None
document_processor: DocumentProcessor = None
github_processor: GitHubProcessor = None
gemini_agent: GeminiAgent = None


# Request models
class GitHubRepoRequest(BaseModel):
    repo_url: str


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global graph_store, document_processor, github_processor, gemini_agent
    
    logger.info("Starting up application...")
    
    try:
        # Initialize graph store
        graph_store = GraphStore()
        logger.info("Graph store initialized")
        
        # Initialize document processor
        document_processor = DocumentProcessor(graph_store)
        logger.info("Document processor initialized")
        
        # Initialize GitHub processor
        github_processor = GitHubProcessor(graph_store)
        logger.info("GitHub processor initialized")
        
        # Initialize Gemini agent with graph store for tool support
        gemini_agent = GeminiAgent(graph_store=graph_store)
        logger.info("Gemini agent initialized with tools")
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application...")
    if graph_store:
        graph_store.close()
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GraphRAG Agent API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/upload", response_model=DocumentUpload)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        # Validate file size
        contents = await file.read()
        if len(contents) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed types: {allowed_extensions}"
            )
        
        # Save file temporarily
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{file_id}_{file.filename}")
        
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        logger.info(f"Processing uploaded file: {file.filename}")
        
        # Process document
        result = await document_processor.process_document(file_path, file.filename)
        
        # Clean up temporary file
        os.remove(file_path)
        
        return DocumentUpload(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/github", response_model=DocumentUpload)
async def process_github_repo(request: GitHubRepoRequest):
    """Process a GitHub repository."""
    try:
        logger.info(f"Processing GitHub repository: {request.repo_url}")
        
        # Validate URL
        if not request.repo_url or not request.repo_url.strip():
            raise HTTPException(
                status_code=400,
                detail="Repository URL is required"
            )
        
        # Check if it's a GitHub URL
        if 'github.com' not in request.repo_url.lower():
            raise HTTPException(
                status_code=400,
                detail="Only GitHub repositories are supported"
            )
        
        # Process repository
        result = await github_processor.process_repository(request.repo_url)
        
        return DocumentUpload(**result)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing GitHub repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint for querying documents."""
    try:
        logger.info(f"Processing chat query: {request.message[:100]}...")
        
        # Generate query embedding
        query_embedding = embedding_service.embed_text(request.message)
        
        # Retrieve relevant chunks from graph
        retrieved_chunks = graph_store.vector_search(query_embedding, top_k=5)
        
        if not retrieved_chunks:
            return ChatResponse(
                response="I don't have any relevant information to answer your question. Please upload some documents first.",
                sources=[],
                timestamp=datetime.now()
            )
        
        # Generate response using Gemini ADK agent (with tool support)
        response_text = await gemini_agent.generate_response(
            query=request.message,
            retrieved_chunks=retrieved_chunks,
            conversation_history=request.conversation_history
        )
        
        # Format sources
        sources = [
            {
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "filename": chunk["filename"],
                "score": float(chunk["score"])
            }
            for chunk in retrieved_chunks
        ]
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def get_documents():
    """Get all uploaded documents."""
    try:
        documents = graph_store.get_all_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its chunks."""
    try:
        graph_store.delete_document(document_id)
        return {"message": "Document deleted successfully", "document_id": document_id}
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}/chunks")
async def get_document_chunks(document_id: str):
    """Get all chunks for a specific document."""
    try:
        chunks = graph_store.get_document_chunks(document_id)
        return {"chunks": chunks}
    except Exception as e:
        logger.error(f"Error retrieving document chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
