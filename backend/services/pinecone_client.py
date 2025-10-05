"""Direct Pinecone client for vector storage and retrieval."""

import logging
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import uuid

from config import settings

logger = logging.getLogger(__name__)

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone client not installed. Install with: pip install pinecone")


class PineconeClient:
    """Direct client for interacting with Pinecone."""
    
    def __init__(self):
        self.pc = None
        self.index = None
        self.index_name = settings.pinecone_index_name
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize direct Pinecone client."""
        try:
            if settings.use_pinecone and PINECONE_AVAILABLE and settings.pinecone_api_key:
                # Initialize Pinecone client with new API
                self.pc = pinecone.Pinecone(api_key=settings.pinecone_api_key)
                logger.info("Pinecone client initialized successfully")
                
                # Initialize or connect to index
                self._initialize_index()
            else:
                logger.warning("Pinecone not configured or not available")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            self.pc = None
    
    def _initialize_index(self):
        """Initialize or connect to Pinecone index."""
        try:
            # List existing indexes
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name in existing_indexes:
                # Connect to existing index
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to existing Pinecone index: {self.index_name}")
            else:
                logger.info(f"Index {self.index_name} not found. Will be created when needed.")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {e}")
            self.index = None
    
    async def create_index(self, dimension: int = 1536, metric: str = "cosine") -> Dict[str, Any]:
        """
        Create a Pinecone index.
        
        Args:
            dimension: Vector dimension
            metric: Distance metric
            
        Returns:
            Dict containing operation result
        """
        if not self.pc:
            return {"success": False, "error": "Pinecone client not initialized"}
        
        try:
            # Check if index already exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name in existing_indexes:
                self.index = self.pc.Index(self.index_name)
                return {
                    "success": True,
                    "message": f"Index '{self.index_name}' already exists"
                }
            
            # Create new index with new API format
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec={
                    "serverless": {
                        "cloud": "aws",
                        "region": "us-east-1"
                    }
                }
            )
            
            # Connect to the new index
            self.index = self.pc.Index(self.index_name)
            
            return {
                "success": True,
                "message": f"Index '{self.index_name}' created successfully"
            }
        except Exception as e:
            logger.error(f"Failed to create Pinecone index: {e}")
            return {"success": False, "error": str(e)}
    
    async def upsert_vectors(
        self, 
        vectors: List[Dict[str, Any]], 
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone index.
        
        Args:
            vectors: List of vectors to upsert
            namespace: Pinecone namespace
            
        Returns:
            Dict containing operation result
        """
        if not self.index:
            return {"success": False, "error": "Pinecone index not initialized"}
        
        try:
            # Ensure index exists
            if not self.index:
                await self.create_index()
            
            # Upsert vectors
            self.index.upsert(
                vectors=vectors,
                namespace=namespace
            )
            
            return {
                "success": True,
                "message": f"Upserted {len(vectors)} vectors to namespace '{namespace}'"
            }
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_vectors(
        self, 
        vector: List[float], 
        top_k: int = 5, 
        namespace: str = "default",
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query vectors from Pinecone index.
        
        Args:
            vector: Query vector
            top_k: Number of results to return
            namespace: Pinecone namespace
            filter_metadata: Metadata filter
            
        Returns:
            Dict containing query results
        """
        if not self.index:
            return {"success": False, "error": "Pinecone index not initialized"}
        
        try:
            # Query vectors
            query_result = self.index.query(
                vector=vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter_metadata,
                include_metadata=True
            )
            
            return {
                "success": True,
                "result": query_result,
                "message": f"Queried {top_k} vectors from namespace '{namespace}'"
            }
        except Exception as e:
            logger.error(f"Failed to query vectors: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_vectors(
        self, 
        ids: List[str], 
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Delete vectors from Pinecone index.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Pinecone namespace
            
        Returns:
            Dict containing operation result
        """
        if not self.index:
            return {"success": False, "error": "Pinecone index not initialized"}
        
        try:
            # Delete vectors
            self.index.delete(
                ids=ids,
                namespace=namespace
            )
            
            return {
                "success": True,
                "message": f"Deleted {len(ids)} vectors from namespace '{namespace}'"
            }
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        Get Pinecone index statistics.
        
        Returns:
            Dict containing index statistics
        """
        if not self.pc:
            return {"success": False, "error": "Pinecone client not initialized"}
        
        try:
            # Get index description
            index_description = self.pc.describe_index(self.index_name)
            
            # Get index stats if index exists
            index_stats = None
            if self.index:
                index_stats = self.index.describe_index_stats()
            
            return {
                "success": True,
                "index_description": index_description,
                "index_stats": index_stats,
                "message": f"Retrieved stats for index '{self.index_name}'"
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Pinecone.
        
        Returns:
            Dict containing connection status
        """
        try:
            if not self.pc:
                return {"success": False, "error": "Pinecone client not initialized"}
            
            # List indexes as a connection test
            indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            return {
                "success": True,
                "message": "Pinecone connection test completed",
                "index_name": self.index_name,
                "available_indexes": index_names,
                "index_exists": self.index_name in index_names
            }
        except Exception as e:
            logger.error(f"Pinecone connection test failed: {e}")
            return {"success": False, "error": str(e)}
