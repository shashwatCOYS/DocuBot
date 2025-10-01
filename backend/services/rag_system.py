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
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
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
            # Fetch the webpage content
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract text content
                text = soup.get_text()
                
                # Clean up the text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                if not text.strip():
                    return {
                        "success": False,
                        "error": "No text content found on the webpage"
                    }
                
                # Split text into chunks
                documents = self.text_splitter.split_text(text)
                
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
                
                return {
                    "success": True,
                    "message": f"Successfully indexed {len(documents)} chunks from {url}",
                    "chunk_count": len(documents),
                    "url": url
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
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
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
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity_score": 1 - distance,  # Convert distance to similarity
                    "rank": i + 1
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []
    
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
