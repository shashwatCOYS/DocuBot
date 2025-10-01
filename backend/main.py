"""Main FastAPI application for DocuBot backend."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime

from config import settings
from services.cerebras_client import CerebrasClient
from services.rag_system import RAGSystem

# Initialize FastAPI app
app = FastAPI(
    title="DocuBot API",
    description="AI-powered documentation chatbot using Cerebras AI and Llama 3.1 8B",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
cerebras_client = CerebrasClient()
rag_system = RAGSystem()


# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    sources: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, Any]] = None


class DocumentRequest(BaseModel):
    url: HttpUrl


class DocumentResponse(BaseModel):
    success: bool
    message: str
    chunk_count: Optional[int] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    cerebras_connection: bool
    database_status: str
    available_models: Optional[List[str]] = None


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "DocuBot API is running",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    # Test Cerebras connection
    cerebras_status = await cerebras_client.test_connection()
    
    # Get database stats
    db_stats = rag_system.get_collection_stats()
    db_status = "healthy" if "error" not in db_stats else "error"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        cerebras_connection=cerebras_status["success"],
        database_status=db_status,
        available_models=cerebras_status.get("available_models")
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Chat endpoint for interacting with the AI assistant.
    
    Uses RAG to retrieve relevant documents and generates responses
    using Cerebras AI with Llama 3.1 8B.
    """
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Search for relevant documents
        relevant_docs = rag_system.search_documents(chat_message.message, n_results=3)
        
        # Prepare context documents
        context_documents = [doc["content"] for doc in relevant_docs]
        
        # System message for the AI
        system_message = """You are DocuBot, an AI assistant specialized in helping users understand technical documentation. 
You have access to indexed documentation and should provide accurate, helpful answers based on the provided context.
Always be polite, concise, and informative. If you cannot find relevant information in the context, 
let the user know and suggest they check the original documentation or add more relevant sources."""
        
        # Generate response using Cerebras AI
        result = await cerebras_client.generate_with_context(
            user_question=chat_message.message,
            context_documents=context_documents,
            system_message=system_message
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Prepare response
        response = ChatResponse(
            response=result["content"],
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            sources=relevant_docs if relevant_docs else None,
            usage=result.get("usage")
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/documents", response_model=DocumentResponse)
async def add_document(document_request: DocumentRequest):
    """
    Add a document by crawling and indexing its URL.
    """
    try:
        result = await rag_system.crawl_and_index_url(str(document_request.url))
        
        if result["success"]:
            return DocumentResponse(
                success=True,
                message=result["message"],
                chunk_count=result.get("chunk_count")
            )
        else:
            return DocumentResponse(
                success=False,
                message="Failed to index document",
                error=result["error"]
            )
            
    except Exception as e:
        return DocumentResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        )


@app.get("/documents/stats")
async def get_document_stats():
    """Get statistics about indexed documents."""
    try:
        stats = rag_system.get_collection_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.delete("/documents")
async def clear_all_documents():
    """Clear all indexed documents."""
    try:
        result = rag_system.clear_all_documents()
        
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")


@app.delete("/documents/{source_url:path}")
async def delete_documents_by_source(source_url: str):
    """Delete documents from a specific source URL."""
    try:
        result = rag_system.delete_documents_by_source(source_url)
        
        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")


@app.get("/search")
async def search_documents(query: str, limit: int = 5):
    """
    Search for documents without generating a chat response.
    Useful for debugging and exploring the knowledge base.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = rag_system.search_documents(query, n_results=limit)
        return JSONResponse(content={
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
