"""RAG (Retrieval-Augmented Generation) system for document management."""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import settings
from .mcp_client import MCPClient, MCPClientError
# Cache service removed


class RAGSystem:
    """RAG system for document indexing and retrieval."""
    
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        self.collection_name = "documents"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Document embeddings for DocuBot"}
        )
        
        # Text splitter for chunking documents - optimized for more chunks
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Smaller chunks for better granularity
            chunk_overlap=100,  # Reduced overlap
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]  # More granular separators
        )
    
    async def crawl_and_index_url(self, url: str) -> Dict[str, Any]:
        """
        Crawl a URL and index its content.
        
        Args:
            url: The URL to crawl and index
            
        Returns:
            Dict containing the indexing result
        """
        try:
            extracted_text: Optional[str] = None

            # Prefer MCP Exa crawling when enabled
            if settings.use_mcp_for_crawling and settings.exa_mcp_base_url:
                try:
                    mcp_client = MCPClient(
                        base_url=settings.exa_mcp_base_url,
                        api_key=None,
                    )
                    # Attempt a crawl tool first; fall back to search if needed
                    tool_name = settings.exa_crawl_tool_name or settings.exa_search_tool_name
                    # Minimal arguments set; adapt based on your gateway's Exa schema
                    args: Dict[str, Any] = {"url": url}
                    mcp_result = await mcp_client.call_tool(tool_name=tool_name, arguments=args)

                    # Heuristics to pull text from common Exa-like responses
                    if isinstance(mcp_result, dict):
                        if "content" in mcp_result and isinstance(mcp_result["content"], str):
                            extracted_text = mcp_result["content"]
                        elif "text" in mcp_result and isinstance(mcp_result["text"], str):
                            extracted_text = mcp_result["text"]
                        elif "results" in mcp_result and isinstance(mcp_result["results"], list):
                            texts: List[str] = []
                            for item in mcp_result["results"]:
                                if isinstance(item, dict):
                                    if isinstance(item.get("content"), str):
                                        texts.append(item["content"])
                                    elif isinstance(item.get("text"), str):
                                        texts.append(item["text"])
                            if texts:
                                extracted_text = "\n\n".join(texts)
                except Exception:
                    # Fall back to local crawl on any MCP error
                    extracted_text = None

            # Local crawl fallback or if MCP is disabled
            if extracted_text is None:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        element.decompose()
                    
                    # Extract text from specific content areas first
                    content_selectors = [
                        'main', 'article', '.content', '.main-content', 
                        '.documentation', '.docs', '.post', '.entry'
                    ]
                    
                    extracted_text = ""
                    for selector in content_selectors:
                        content_elements = soup.select(selector)
                        if content_elements:
                            for element in content_elements:
                                extracted_text += element.get_text(separator='\n', strip=True) + '\n'
                    
                    # If no specific content found, extract all text
                    if not extracted_text.strip():
                        extracted_text = soup.get_text(separator='\n', strip=True)
                    
                    # Clean up the text
                    lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
                    extracted_text = '\n'.join(lines)

            if not extracted_text or not extracted_text.strip():
                return {"success": False, "error": "No text content found to index"}

            # Split text into chunks
            documents = self.text_splitter.split_text(extracted_text)
            
            if not documents:
                return {
                    "success": False,
                    "error": "No document chunks created"
                }
            
            # Generate IDs for each chunk
            chunk_ids = [str(uuid.uuid4()) for _ in documents]
            
            # Prepare metadata
            metadata = {
                "source_url": url,
                "indexed_at": datetime.now().isoformat(),
                "chunk_count": len(documents)
            }
            
            # Add documents to ChromaDB
            metadatas = [{**metadata, "chunk_id": chunk_id, "chunk_index": i} 
                       for i, chunk_id in enumerate(chunk_ids)]
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            # Caching disabled
            
            return {
                "success": True,
                "message": f"Successfully indexed {len(documents)} chunks from {url}",
                "chunk_count": len(documents),
                "url": url,
                "cached_chunks": len(chunk_ids)
            }
                
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code} - {e.response.text}"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error crawling URL: {str(e)}"
            }
    
    async def crawl_and_index_website(self, start_url: str, max_pages: int = None) -> Dict[str, Any]:
        """
        Crawl and index multiple pages from a website.
        
        Args:
            start_url: Starting URL for crawling
            max_pages: Maximum number of pages to crawl (uses config default if None)
            
        Returns:
            Dict containing the indexing results
        """
        try:
            from .web_crawler import WebCrawler
            
            max_pages = max_pages or settings.max_pages_per_domain
            
            # Initialize web crawler with context manager
            async with WebCrawler() as crawler:
                # Crawl the website
                crawl_results = await crawler.crawl_website_recursive(
                    start_url=start_url,
                    max_pages=max_pages,
                    max_depth=settings.max_crawl_depth
                )
            
            if not crawl_results:
                return {
                    "success": False,
                    "error": "No pages were crawled"
                }
            
            # Index each crawled page
            indexed_pages = []
            total_chunks = 0
            
            for page_result in crawl_results:
                if page_result.get("success") and page_result.get("content"):
                    # Index the page content with structured data
                    index_result = await self._index_text_content(
                        content=page_result["content"],
                        url=page_result["url"],
                        metadata=page_result.get("metadata", {}),
                        structured_content=page_result.get("structured_content", {})
                    )
                    
                    if index_result.get("success"):
                        indexed_pages.append({
                            "url": page_result["url"],
                            "chunks": index_result["chunk_count"],
                            "title": page_result.get("title", "")
                        })
                        total_chunks += index_result["chunk_count"]
            
            return {
                "success": True,
                "message": f"Successfully indexed {len(indexed_pages)} pages with {total_chunks} total chunks",
                "pages_indexed": len(indexed_pages),
                "total_chunks": total_chunks,
                "indexed_pages": indexed_pages,
                "start_url": start_url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error crawling website: {str(e)}"
            }
    
    async def _index_text_content(self, content: str, url: str, metadata: Dict[str, Any] = None, structured_content: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Index text content directly without crawling, including structured content with markdown.
        
        Args:
            content: Text content to index
            url: Source URL
            metadata: Additional metadata
            structured_content: Structured content data with markdown
            
        Returns:
            Dict containing the indexing result
        """
        try:
            if not content or not content.strip():
                return {"success": False, "error": "No content provided"}
            
            # Get markdown content if available
            markdown_content = ""
            if structured_content and isinstance(structured_content, dict):
                markdown_content = structured_content.get('markdown', '')
            
            # Split main text into chunks
            documents = self.text_splitter.split_text(content)
            
            # Split markdown content into chunks (prefer markdown for better formatting)
            markdown_documents = []
            if markdown_content:
                markdown_documents = self.text_splitter.split_text(markdown_content)
            
            # Use markdown content if available, otherwise use plain text
            final_documents = markdown_documents if markdown_documents else documents
            
            # Index structured content separately
            structured_chunks = []
            if structured_content:
                structured_chunks = await self._index_structured_content(structured_content, url, metadata)
            
            if not final_documents and not structured_chunks:
                return {
                    "success": False,
                    "error": "No document chunks created"
                }
            
            # Generate IDs for main content chunks
            chunk_ids = [str(uuid.uuid4()) for _ in final_documents]
            
            # Prepare metadata
            base_metadata = {
                "source_url": url,
                "indexed_at": datetime.now().isoformat(),
                "chunk_count": len(final_documents) + len(structured_chunks),
                "content_type": "main_content",
                "has_markdown": bool(markdown_documents)
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            # Add main content documents to ChromaDB
            if final_documents:
                metadatas = [{**base_metadata, "chunk_id": chunk_id, "chunk_index": i} 
                           for i, chunk_id in enumerate(chunk_ids)]
                
                self.collection.add(
                    documents=final_documents,
                    metadatas=metadatas,
                    ids=chunk_ids
                )
                
                # Caching disabled
            
            # Combine all chunks for reporting
            all_chunks = []
            for i, (chunk_id, document, metadata_item) in enumerate(zip(chunk_ids, final_documents, metadatas)):
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "content": document,
                    "metadata": metadata_item,
                    "chunk_index": i
                })
            
            # Add structured chunks
            all_chunks.extend(structured_chunks)
            
            total_chunks = len(final_documents) + len(structured_chunks)
            
            return {
                "success": True,
                "message": f"Successfully indexed {total_chunks} chunks ({len(final_documents)} main + {len(structured_chunks)} structured)",
                "chunk_count": total_chunks,
                "main_chunks": len(final_documents),
                "structured_chunks": len(structured_chunks),
                "has_markdown": bool(markdown_documents),
                "url": url,
                "cached_chunks": total_chunks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error indexing content: {str(e)}"
            }
    
    async def _index_structured_content(self, structured_content: Dict[str, Any], url: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Index structured content like lists, tables, and code blocks with markdown formatting.
        
        Args:
            structured_content: Structured content data with markdown
            url: Source URL
            metadata: Additional metadata
            
        Returns:
            List of indexed structured chunks
        """
        structured_chunks = []
        
        try:
            # Index headings with markdown
            if structured_content.get('headings'):
                for i, heading in enumerate(structured_content['headings']):
                    heading_text = heading.get('markdown', heading.get('text', ''))
                    if heading_text:
                        chunk_id = str(uuid.uuid4())
                        chunk_metadata = {
                            "source_url": url,
                            "indexed_at": datetime.now().isoformat(),
                            "content_type": "heading",
                            "heading_level": heading.get('level', 1),
                            "heading_index": i,
                            "chunk_index": 0,
                            "has_markdown": True
                        }
                        
                        if metadata:
                            chunk_metadata.update(metadata)
                        
                        self.collection.add(
                            documents=[heading_text],
                            metadatas=[chunk_metadata],
                            ids=[chunk_id]
                        )
                        
                        # Caching disabled
                        
                        structured_chunks.append({
                            "chunk_id": chunk_id,
                            "content": heading_text,
                            "metadata": chunk_metadata,
                            "chunk_index": 0
                        })
            
            # Index code blocks with markdown
            if structured_content.get('code_blocks'):
                for i, code_block in enumerate(structured_content['code_blocks']):
                    code_text = code_block.get('markdown', code_block.get('content', ''))
                    if code_text:
                        chunk_id = str(uuid.uuid4())
                        chunk_metadata = {
                            "source_url": url,
                            "indexed_at": datetime.now().isoformat(),
                            "content_type": "code_block",
                            "language": code_block.get('language', ''),
                            "code_index": i,
                            "chunk_index": 0,
                            "has_markdown": True
                        }
                        
                        if metadata:
                            chunk_metadata.update(metadata)
                        
                        self.collection.add(
                            documents=[code_text],
                            metadatas=[chunk_metadata],
                            ids=[chunk_id]
                        )
                        
                        # Caching disabled
                        
                        structured_chunks.append({
                            "chunk_id": chunk_id,
                            "content": code_text,
                            "metadata": chunk_metadata,
                            "chunk_index": 0
                        })
            
            # Index tables with markdown
            if structured_content.get('tables'):
                for i, table in enumerate(structured_content['tables']):
                    table_text = table.get('markdown', '')
                    if table_text:
                        chunk_id = str(uuid.uuid4())
                        chunk_metadata = {
                            "source_url": url,
                            "indexed_at": datetime.now().isoformat(),
                            "content_type": "table",
                            "table_index": i,
                            "chunk_index": 0,
                            "has_markdown": True
                        }
                        
                        if metadata:
                            chunk_metadata.update(metadata)
                        
                        self.collection.add(
                            documents=[table_text],
                            metadatas=[chunk_metadata],
                            ids=[chunk_id]
                        )
                        
                        # Caching disabled
                        
                        structured_chunks.append({
                            "chunk_id": chunk_id,
                            "content": table_text,
                            "metadata": chunk_metadata,
                            "chunk_index": 0
                        })
            
            # Index lists with markdown
            if structured_content.get('lists'):
                for i, list_data in enumerate(structured_content['lists']):
                    list_text = list_data.get('markdown', '')
                    if not list_text:
                        # Fallback to plain text format
                        list_text = f"List ({list_data['type']}):\n" + "\n".join([f"• {item}" for item in list_data.get('items', [])])
                    
                    if list_text:
                        chunk_id = str(uuid.uuid4())
                        chunk_metadata = {
                            "source_url": url,
                            "indexed_at": datetime.now().isoformat(),
                            "content_type": "list",
                            "list_type": list_data.get('type', 'ul'),
                            "list_index": i,
                            "chunk_index": 0,
                            "has_markdown": bool(list_data.get('markdown'))
                        }
                        
                        if metadata:
                            chunk_metadata.update(metadata)
                        
                        self.collection.add(
                            documents=[list_text],
                            metadatas=[chunk_metadata],
                            ids=[chunk_id]
                        )
                        
                        # Caching disabled
                        
                        structured_chunks.append({
                            "chunk_id": chunk_id,
                            "content": list_text,
                            "metadata": chunk_metadata,
                            "chunk_index": 0
                        })
            
            # Index paragraphs with markdown
            if structured_content.get('paragraphs'):
                for i, paragraph in enumerate(structured_content['paragraphs']):
                    paragraph_text = paragraph.get('markdown', paragraph.get('text', ''))
                    if len(paragraph_text) > 50:  # Only meaningful paragraphs
                        chunk_id = str(uuid.uuid4())
                        chunk_metadata = {
                            "source_url": url,
                            "indexed_at": datetime.now().isoformat(),
                            "content_type": "paragraph",
                            "paragraph_index": i,
                            "chunk_index": 0,
                            "has_markdown": bool(paragraph.get('markdown'))
                        }
                        
                        if metadata:
                            chunk_metadata.update(metadata)
                        
                        self.collection.add(
                            documents=[paragraph_text],
                            metadatas=[chunk_metadata],
                            ids=[chunk_id]
                        )
                        
                        # Caching disabled
                        
                        structured_chunks.append({
                            "chunk_id": chunk_id,
                            "content": paragraph_text,
                            "metadata": chunk_metadata,
                            "chunk_index": 0
                        })
            
            return structured_chunks
            
        except Exception as e:
            logger.error(f"Error indexing structured content: {e}")
            return []
    
    async def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: The search query
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results['documents'] or not results['documents'][0]:
                return []
            
            # Format results
            formatted_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                chunk_id = metadata.get("chunk_id")
                
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity_score": 1 - distance,  # Convert distance to similarity
                    "rank": i + 1,
                    "from_cache": False,
                    "chunk_id": chunk_id
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    # Cache methods removed
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the document collection.
        
        Returns:
            Dict containing collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get unique sources
            all_metadata = self.collection.get()["metadatas"]
            unique_sources = set()
            for metadata in all_metadata:
                if metadata and "source_url" in metadata:
                    unique_sources.add(metadata["source_url"])
            
            return {
                "total_chunks": count,
                "unique_sources": len(unique_sources),
                "sources": list(unique_sources)
            }
            
        except Exception as e:
            return {
                "error": f"Error getting collection stats: {str(e)}"
            }
    
    def delete_documents_by_source(self, source_url: str) -> Dict[str, Any]:
        """
        Delete all documents from a specific source URL.
        
        Args:
            source_url: The source URL to delete documents from
            
        Returns:
            Dict containing the deletion result
        """
        try:
            # Get all documents from the source
            results = self.collection.get(
                where={"source_url": source_url}
            )
            
            if not results["ids"]:
                return {
                    "success": True,
                    "message": f"No documents found for source: {source_url}",
                    "deleted_count": 0
                }
            
            # Delete the documents
            self.collection.delete(ids=results["ids"])
            
            return {
                "success": True,
                "message": f"Deleted {len(results['ids'])} documents from {source_url}",
                "deleted_count": len(results["ids"])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error deleting documents: {str(e)}"
            }
    
    def clear_all_documents(self) -> Dict[str, Any]:
        """
        Clear all documents from the collection.
        
        Returns:
            Dict containing the clearing result
        """
        try:
            # Get count before deletion
            count = self.collection.count()
            
            # Delete the collection and recreate it
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for DocuBot"}
            )
            
            return {
                "success": True,
                "message": f"Cleared {count} documents from the collection",
                "deleted_count": count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error clearing documents: {str(e)}"
            }
