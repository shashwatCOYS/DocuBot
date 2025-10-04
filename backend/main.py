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
from services.enhanced_rag import EnhancedRAGSystem

# Initialize FastAPI app
app = FastAPI(
    title="DocuBot API",
    description="AI-powered documentation chatbot using Cerebras AI and Llama 3.1 8B",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
cerebras_client = CerebrasClient()
rag_system = RAGSystem()
enhanced_rag_system = EnhancedRAGSystem()


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


class CrawlRequest(BaseModel):
    urls: List[HttpUrl]
    context7_libraries: Optional[List[str]] = None


class CrawlResponse(BaseModel):
    success: bool
    message: str
    total_chunks: Optional[int] = None
    urls_processed: Optional[int] = None
    enhanced_with_context7: Optional[bool] = None
    error: Optional[str] = None


class DocumentationCrawlRequest(BaseModel):
    base_url: HttpUrl
    context7_libraries: Optional[List[str]] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    context7_libraries: Optional[List[str]] = None


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
    
    Uses enhanced RAG with Context7 integration to retrieve relevant documents 
    and generates responses using Cerebras AI with Llama 3.1 8B.
    """
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Search for relevant documents using enhanced RAG
        relevant_docs = await enhanced_rag_system.search_with_context7_enhancement(
            chat_message.message, 
            limit=5
        )
        
        # Fallback to original RAG if enhanced search fails
        if not relevant_docs:
            relevant_docs = await rag_system.search_documents(chat_message.message, n_results=3)
        
        # Prepare context documents
        context_documents = [doc["content"] for doc in relevant_docs]
        
        # System message for the AI
        system_message = """You are DocuBot, an AI assistant specialized in helping users understand technical documentation. 
You have access to indexed documentation enhanced with Context7 and should provide accurate, helpful answers based on the provided context.
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


@app.post("/documents/crawl-website")
async def crawl_website(document_request: DocumentRequest, max_pages: int = 50):
    """
    Crawl and index multiple pages from a website.
    """
    try:
        result = await rag_system.crawl_and_index_website(str(document_request.url), max_pages)
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": result["message"],
                "pages_indexed": result.get("pages_indexed"),
                "total_chunks": result.get("total_chunks"),
                "indexed_pages": result.get("indexed_pages")
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": "Failed to crawl website",
                "error": result.get("error")
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error crawling website: {str(e)}")


@app.post("/documents/deep-crawl")
async def deep_crawl_website(document_request: DocumentRequest, max_pages: int = 500):
    """
    Deep crawl and index all content from a website domain.
    """
    try:
        result = await rag_system.crawl_and_index_website(str(document_request.url), max_pages)
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": f"Deep crawl completed: {result['message']}",
                "pages_indexed": result.get("pages_indexed"),
                "total_chunks": result.get("total_chunks"),
                "indexed_pages": result.get("indexed_pages"),
                "crawl_type": "deep_recursive",
                "max_pages": max_pages
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": "Failed to deep crawl website",
                "error": result.get("error")
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deep crawling website: {str(e)}")


@app.get("/documents/stats")
async def get_document_stats():
    """Get statistics about indexed documents."""
    try:
        stats = rag_system.get_collection_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


# Cache endpoints removed


@app.get("/pinecone/test")
async def test_pinecone_connection():
    """Test Pinecone connection."""
    try:
        from services.pinecone_client import PineconeClient
        pinecone_client = PineconeClient()
        result = await pinecone_client.test_connection()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing Pinecone connection: {str(e)}")


@app.post("/pinecone/create-index")
async def create_pinecone_index(dimension: int = 1536, metric: str = "cosine"):
    """Create Pinecone index."""
    try:
        from services.pinecone_client import PineconeClient
        pinecone_client = PineconeClient()
        result = await pinecone_client.create_index(dimension, metric)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Pinecone index: {str(e)}")


@app.get("/pinecone/stats")
async def get_pinecone_stats():
    """Get Pinecone index statistics."""
    try:
        from services.pinecone_client import PineconeClient
        pinecone_client = PineconeClient()
        result = await pinecone_client.get_index_stats()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Pinecone stats: {str(e)}")


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
        
        results = await rag_system.search_documents(query, n_results=limit)
        return JSONResponse(content={
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@app.post("/crawl/enhanced", response_model=CrawlResponse)
async def crawl_urls_enhanced(crawl_request: CrawlRequest):
    """
    Crawl multiple URLs with Context7 enhancement.
    
    This endpoint uses the enhanced web crawler with MCP Gateway integration
    and Context7 documentation enhancement.
    """
    try:
        urls = [str(url) for url in crawl_request.urls]
        
        result = await enhanced_rag_system.crawl_and_index_with_context7(
            urls=urls,
            context7_libraries=crawl_request.context7_libraries
        )
        
        if result["success"]:
            return CrawlResponse(
                success=True,
                message=result["message"],
                total_chunks=result.get("total_chunks"),
                urls_processed=result.get("urls_processed"),
                enhanced_with_context7=result.get("enhanced_with_context7")
            )
        else:
            return CrawlResponse(
                success=False,
                message="Failed to crawl URLs",
                error=result["error"]
            )
            
    except Exception as e:
        return CrawlResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        )


@app.post("/crawl/documentation", response_model=CrawlResponse)
async def crawl_documentation_site(crawl_request: DocumentationCrawlRequest):
    """
    Crawl an entire documentation site with Context7 enhancement.
    
    This endpoint specializes in crawling documentation sites and can
    recursively crawl through documentation pages.
    """
    try:
        result = await enhanced_rag_system.crawl_documentation_site_with_context7(
            base_url=str(crawl_request.base_url),
            context7_libraries=crawl_request.context7_libraries
        )
        
        if result["success"]:
            return CrawlResponse(
                success=True,
                message=result["message"],
                total_chunks=result.get("total_chunks"),
                enhanced_with_context7=result.get("enhanced_with_context7")
            )
        else:
            return CrawlResponse(
                success=False,
                message="Failed to crawl documentation site",
                error=result["error"]
            )
            
    except Exception as e:
        return CrawlResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        )


@app.post("/search/enhanced")
async def search_enhanced(search_request: SearchRequest):
    """
    Enhanced search with Context7 integration.
    
    This endpoint provides semantic search with Context7 documentation
    enhancement for more accurate and context-aware results.
    """
    try:
        if not search_request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = await enhanced_rag_system.search_with_context7_enhancement(
            query=search_request.query,
            limit=search_request.limit,
            context7_libraries=search_request.context7_libraries
        )
        
        return JSONResponse(content={
            "query": search_request.query,
            "results": results,
            "count": len(results),
            "enhanced_with_context7": bool(search_request.context7_libraries)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@app.get("/context7/libraries")
async def get_available_context7_libraries():
    """
    Get available Context7 libraries for enhancement.
    
    This endpoint returns a list of commonly used Context7 library IDs
    that can be used for enhancing crawled content.
    """
    common_libraries = [
        "/upstash/context7",
        "/supabase/supabase",
        "/vercel/next.js",
        "/facebook/react",
        "/microsoft/vscode",
        "/tensorflow/tensorflow",
        "/pytorch/pytorch",
        "/fastapi/fastapi",
        "/pallets/flask",
        "/django/django"
    ]
    
    return JSONResponse(content={
        "available_libraries": common_libraries,
        "description": "Common Context7 libraries that can be used for content enhancement",
        "usage": "Include these library IDs in context7_libraries parameter when crawling or searching"
    })


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
