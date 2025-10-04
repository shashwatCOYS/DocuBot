"""Enhanced RAG system with Context7 integration and cloud vector database."""

import logging
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import uuid

from .web_crawler import WebCrawler
from .vector_db import VectorDatabase
from .mcp_client import MCPClient, MCPClientError
from config import settings

logger = logging.getLogger(__name__)


class EnhancedRAGSystem:
    """Enhanced RAG system with Context7 integration and robust web crawling."""
    
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.context7_client = None
        self._initialize_context7()
    
    def _initialize_context7(self):
        """Initialize Context7 MCP client."""
        try:
            if hasattr(settings, 'context7_api_key') and settings.context7_api_key:
                self.context7_client = MCPClient(
                    base_url="http://context7-mcp:7777",  # Docker service name
                    api_key=settings.context7_api_key,
                    timeout_s=60.0
                )
                logger.info("Context7 client initialized successfully")
            else:
                logger.warning("Context7 API key not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Context7 client: {e}")
            self.context7_client = None
    
    async def crawl_and_index_with_context7(
        self, 
        urls: List[str], 
        context7_libraries: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Crawl URLs and index them with Context7-enhanced context.
        
        Args:
            urls: List of URLs to crawl
            context7_libraries: Optional list of Context7 library IDs to enhance context
            
        Returns:
            Dict containing the indexing result
        """
        try:
            crawled_documents = []
            
            async with WebCrawler() as crawler:
                for url in urls:
                    logger.info(f"Crawling URL: {url}")
                    
                    # Crawl the URL
                    crawl_result = await crawler.crawl_single_url(url)
                    
                    if crawl_result["success"]:
                        # Enhance with Context7 if available
                        enhanced_content = await self._enhance_with_context7(
                            crawl_result["content"],
                            context7_libraries
                        )
                        
                        # Split content into chunks
                        chunks = self._split_content_into_chunks(enhanced_content)
                        
                        # Prepare documents for indexing
                        for i, chunk in enumerate(chunks):
                            doc = {
                                "content": chunk,
                                "source_url": url,
                                "title": self._extract_title_from_content(chunk),
                                "chunk_index": i,
                                "chunk_id": str(uuid.uuid4()),
                                "crawled_at": datetime.now().isoformat(),
                                "metadata": json.dumps({
                                    "original_content": crawl_result["content"][:500],  # First 500 chars
                                    "enhanced_with_context7": bool(enhanced_content != crawl_result["content"]),
                                    "context7_libraries": context7_libraries or []
                                })
                            }
                            crawled_documents.append(doc)
            
            # Index documents in vector database
            if crawled_documents:
                index_result = self.vector_db.add_documents(crawled_documents)
                
                if index_result["success"]:
                    return {
                        "success": True,
                        "message": f"Successfully indexed {len(crawled_documents)} chunks from {len(urls)} URLs",
                        "total_chunks": len(crawled_documents),
                        "urls_processed": len(urls),
                        "enhanced_with_context7": bool(context7_libraries)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to index documents: {index_result.get('error', 'Unknown error')}"
                    }
            else:
                return {
                    "success": False,
                    "error": "No documents were successfully crawled"
                }
                
        except Exception as e:
            logger.error(f"Error in crawl_and_index_with_context7: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def crawl_documentation_site_with_context7(
        self, 
        base_url: str, 
        context7_libraries: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Crawl an entire documentation site with Context7 enhancement.
        
        Args:
            base_url: Base URL of the documentation site
            context7_libraries: Optional list of Context7 library IDs
            
        Returns:
            Dict containing the crawling and indexing result
        """
        try:
            crawled_documents = []
            
            async with WebCrawler() as crawler:
                # Crawl the documentation site
                crawl_results = await crawler.crawl_documentation_site(base_url)
                
                logger.info(f"Crawled {len(crawl_results)} pages from {base_url}")
                
                for result in crawl_results:
                    if result["success"]:
                        # Enhance with Context7 if available
                        enhanced_content = await self._enhance_with_context7(
                            result["content"],
                            context7_libraries
                        )
                        
                        # Split content into chunks
                        chunks = self._split_content_into_chunks(enhanced_content)
                        
                        # Prepare documents for indexing
                        for i, chunk in enumerate(chunks):
                            doc = {
                                "content": chunk,
                                "source_url": result["url"],
                                "title": self._extract_title_from_content(chunk),
                                "chunk_index": i,
                                "chunk_id": str(uuid.uuid4()),
                                "crawled_at": datetime.now().isoformat(),
                                "metadata": json.dumps({
                                    "crawl_method": result.get("method", "unknown"),
                                    "enhanced_with_context7": bool(enhanced_content != result["content"]),
                                    "context7_libraries": context7_libraries or []
                                })
                            }
                            crawled_documents.append(doc)
            
            # Index documents in vector database
            if crawled_documents:
                index_result = self.vector_db.add_documents(crawled_documents)
                
                if index_result["success"]:
                    return {
                        "success": True,
                        "message": f"Successfully indexed documentation site: {base_url}",
                        "total_chunks": len(crawled_documents),
                        "pages_crawled": len(crawl_results),
                        "enhanced_with_context7": bool(context7_libraries)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to index documents: {index_result.get('error', 'Unknown error')}"
                    }
            else:
                return {
                    "success": False,
                    "error": "No documentation pages were successfully crawled"
                }
                
        except Exception as e:
            logger.error(f"Error in crawl_documentation_site_with_context7: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_with_context7_enhancement(
        self, 
        query: str, 
        limit: int = 5,
        context7_libraries: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents with Context7 enhancement.
        
        Args:
            query: Search query
            limit: Maximum number of results
            context7_libraries: Optional Context7 libraries to enhance the query
            
        Returns:
            List of relevant documents with Context7 context
        """
        try:
            # Enhance query with Context7 if available
            enhanced_query = await self._enhance_query_with_context7(query, context7_libraries)
            
            # Search in vector database
            results = self.vector_db.search_similar(enhanced_query, limit=limit)
            
            # Enhance results with Context7 context if available
            if self.context7_client and context7_libraries:
                for result in results:
                    enhanced_context = await self._get_context7_context_for_result(
                        result, context7_libraries
                    )
                    if enhanced_context:
                        result["context7_enhancement"] = enhanced_context
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search_with_context7_enhancement: {e}")
            return []
    
    async def _enhance_with_context7(
        self, 
        content: str, 
        context7_libraries: Optional[List[str]]
    ) -> str:
        """
        Enhance content with Context7 documentation.
        
        Args:
            content: Original content
            context7_libraries: List of Context7 library IDs
            
        Returns:
            Enhanced content
        """
        if not self.context7_client or not context7_libraries:
            return content
        
        try:
            enhanced_content = content
            
            for library_id in context7_libraries:
                try:
                    # Get documentation for the library
                    docs_result = await self.context7_client.call_tool(
                        tool_name="get-library-docs",
                        arguments={
                            "context7CompatibleLibraryID": library_id,
                            "tokens": 1000
                        }
                    )
                    
                    if isinstance(docs_result, dict) and "content" in docs_result:
                        # Add relevant documentation context
                        enhanced_content += f"\n\n--- Context7 Documentation for {library_id} ---\n"
                        enhanced_content += docs_result["content"]
                        
                except Exception as e:
                    logger.warning(f"Failed to enhance with Context7 library {library_id}: {e}")
                    continue
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Error enhancing content with Context7: {e}")
            return content
    
    async def _enhance_query_with_context7(
        self, 
        query: str, 
        context7_libraries: Optional[List[str]]
    ) -> str:
        """
        Enhance search query with Context7 context.
        
        Args:
            query: Original query
            context7_libraries: List of Context7 library IDs
            
        Returns:
            Enhanced query
        """
        if not self.context7_client or not context7_libraries:
            return query
        
        try:
            enhanced_query = query
            
            # Add Context7 context to the query
            for library_id in context7_libraries:
                enhanced_query += f" {library_id} documentation context"
            
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Error enhancing query with Context7: {e}")
            return query
    
    async def _get_context7_context_for_result(
        self, 
        result: Dict[str, Any], 
        context7_libraries: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get Context7 context for a specific search result.
        
        Args:
            result: Search result
            context7_libraries: List of Context7 library IDs
            
        Returns:
            Context7 enhancement data or None
        """
        if not self.context7_client:
            return None
        
        try:
            # Extract key terms from the result content
            content = result.get("content", "")
            source_url = result.get("source_url", "")
            
            # Try to get relevant Context7 documentation
            for library_id in context7_libraries:
                try:
                    docs_result = await self.context7_client.call_tool(
                        tool_name="get-library-docs",
                        arguments={
                            "context7CompatibleLibraryID": library_id,
                            "tokens": 500
                        }
                    )
                    
                    if isinstance(docs_result, dict):
                        return {
                            "library_id": library_id,
                            "documentation": docs_result.get("content", ""),
                            "enhanced_at": datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    logger.warning(f"Failed to get Context7 context for {library_id}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Context7 context for result: {e}")
            return None
    
    def _split_content_into_chunks(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split content into overlapping chunks.
        
        Args:
            content: Content to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of content chunks
        """
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Try to break at sentence or paragraph boundary
            if end < len(content):
                # Look for sentence endings
                for break_char in ['. ', '\n\n', '\n']:
                    break_pos = content.rfind(break_char, start, end)
                    if break_pos > start:
                        end = break_pos + len(break_char)
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(content):
                break
        
        return chunks
    
    def _extract_title_from_content(self, content: str) -> str:
        """
        Extract a title from content.
        
        Args:
            content: Content to extract title from
            
        Returns:
            Extracted title or default title
        """
        # Try to find the first line that looks like a title
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 100 and not line.startswith(('http', 'www')):
                return line
        
        # Fallback to first 50 characters
        return content[:50].strip() + "..." if len(content) > 50 else content.strip()
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        return self.vector_db.get_collection_stats()
    
    def delete_documents_by_source(self, source_url: str) -> Dict[str, Any]:
        """Delete all documents from a specific source URL."""
        return self.vector_db.delete_by_source_url(source_url)
    
    def clear_all_documents(self) -> Dict[str, Any]:
        """Clear all documents from the collection."""
        return self.vector_db.clear_collection()
    
    def close(self):
        """Close all connections."""
        if self.vector_db:
            self.vector_db.close()

