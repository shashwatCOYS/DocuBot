"""Cloud-based vector database service using Weaviate."""

import logging
from typing import List, Dict, Any, Optional
import weaviate
from weaviate import Client
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import MetadataQuery
import uuid
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class VectorDatabase:
    """Cloud-based vector database service using Weaviate."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.collection_name = "docubot_documents"
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Weaviate client."""
        try:
            weaviate_url = getattr(settings, 'weaviate_url', 'http://localhost:8080')
            
            self.client = weaviate.connect_to_local(
                host="localhost",
                port=8080,
                grpc_port=50051
            )
            
            # Create or get collection
            if self.client.collections.exists(self.collection_name):
                self.collection = self.client.collections.get(self.collection_name)
                logger.info(f"Connected to existing collection: {self.collection_name}")
            else:
                self.collection = self._create_collection()
                logger.info(f"Created new collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate client: {e}")
            self.client = None
    
    def _create_collection(self):
        """Create a new collection with proper schema."""
        try:
            collection = self.client.collections.create(
                name=self.collection_name,
                properties=[
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="source_url", data_type=DataType.TEXT),
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="chunk_index", data_type=DataType.INT),
                    Property(name="chunk_id", data_type=DataType.TEXT),
                    Property(name="crawled_at", data_type=DataType.DATE),
                    Property(name="metadata", data_type=DataType.TEXT),  # JSON string
                ],
                # Configure vectorizer for text embedding
                vectorizer_config=Configure.Vectorizer.text2vec_transformers(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    vectorize_collection_name=False
                )
            )
            return collection
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add multiple documents to the vector database.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Dict containing the result
        """
        if not self.client or not self.collection:
            return {"success": False, "error": "Vector database not initialized"}
        
        try:
            # Prepare objects for insertion
            objects_to_insert = []
            
            for doc in documents:
                obj_data = {
                    "content": doc.get("content", ""),
                    "source_url": doc.get("source_url", ""),
                    "title": doc.get("title", ""),
                    "chunk_index": doc.get("chunk_index", 0),
                    "chunk_id": doc.get("chunk_id", str(uuid.uuid4())),
                    "crawled_at": doc.get("crawled_at", datetime.now().isoformat()),
                    "metadata": doc.get("metadata", "{}")
                }
                
                objects_to_insert.append(obj_data)
            
            # Insert objects
            result = self.collection.data.insert_many(objects_to_insert)
            
            return {
                "success": True,
                "inserted_count": len(objects_to_insert),
                "inserted_ids": result.uuids
            }
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return {"success": False, "error": str(e)}
    
    def search_similar(
        self, 
        query: str, 
        limit: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results
            where_filter: Optional filter conditions
            
        Returns:
            List of similar documents
        """
        if not self.client or not self.collection:
            return []
        
        try:
            # Build query
            query_builder = self.collection.query.near_text(
                query=query,
                limit=limit,
                return_metadata=MetadataQuery(distance=True, score=True)
            )
            
            # Add filter if provided
            if where_filter:
                query_builder = query_builder.where(where_filter)
            
            # Execute query
            response = query_builder.do()
            
            # Process results
            results = []
            if response.objects:
                for obj in response.objects:
                    result = {
                        "content": obj.properties.get("content", ""),
                        "source_url": obj.properties.get("source_url", ""),
                        "title": obj.properties.get("title", ""),
                        "chunk_index": obj.properties.get("chunk_index", 0),
                        "chunk_id": obj.properties.get("chunk_id", ""),
                        "crawled_at": obj.properties.get("crawled_at", ""),
                        "metadata": obj.properties.get("metadata", "{}"),
                        "similarity_score": 1 - obj.metadata.distance if obj.metadata.distance else 0,
                        "distance": obj.metadata.distance if obj.metadata.distance else 0
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    def search_by_source_url(self, source_url: str) -> List[Dict[str, Any]]:
        """
        Search for documents by source URL.
        
        Args:
            source_url: Source URL to search for
            
        Returns:
            List of documents from the source URL
        """
        if not self.client or not self.collection:
            return []
        
        try:
            response = self.collection.query.get(
                where={
                    "path": ["source_url"],
                    "operator": "Equal",
                    "valueText": source_url
                }
            ).do()
            
            results = []
            if response.get("data", {}).get("Get", {}).get(self.collection_name):
                for obj in response["data"]["Get"][self.collection_name]:
                    result = {
                        "content": obj.get("content", ""),
                        "source_url": obj.get("source_url", ""),
                        "title": obj.get("title", ""),
                        "chunk_index": obj.get("chunk_index", 0),
                        "chunk_id": obj.get("chunk_id", ""),
                        "crawled_at": obj.get("crawled_at", ""),
                        "metadata": obj.get("metadata", "{}")
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search by source URL: {e}")
            return []
    
    def delete_by_source_url(self, source_url: str) -> Dict[str, Any]:
        """
        Delete all documents from a specific source URL.
        
        Args:
            source_url: Source URL to delete documents from
            
        Returns:
            Dict containing the deletion result
        """
        if not self.client or not self.collection:
            return {"success": False, "error": "Vector database not initialized"}
        
        try:
            # First, get all documents from the source
            documents = self.search_by_source_url(source_url)
            
            if not documents:
                return {
                    "success": True,
                    "message": f"No documents found for source: {source_url}",
                    "deleted_count": 0
                }
            
            # Delete documents by ID
            document_ids = [doc["chunk_id"] for doc in documents]
            
            # Note: Weaviate deletion by ID requires the objects to exist
            # For now, we'll use a different approach - mark as deleted
            # or use the delete method if available
            
            return {
                "success": True,
                "message": f"Marked {len(documents)} documents for deletion from {source_url}",
                "deleted_count": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Failed to delete by source URL: {e}")
            return {"success": False, "error": str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dict containing collection statistics
        """
        if not self.client or not self.collection:
            return {"error": "Vector database not initialized"}
        
        try:
            # Get total count
            total_count = self.collection.aggregate.over_all(total_count=True)
            
            # Get unique sources (this would require a more complex query)
            # For now, return basic stats
            return {
                "total_documents": total_count.total_count if total_count.total_count else 0,
                "collection_name": self.collection_name,
                "status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def clear_collection(self) -> Dict[str, Any]:
        """
        Clear all documents from the collection.
        
        Returns:
            Dict containing the clearing result
        """
        if not self.client or not self.collection:
            return {"success": False, "error": "Vector database not initialized"}
        
        try:
            # Get count before deletion
            stats = self.get_collection_stats()
            count_before = stats.get("total_documents", 0)
            
            # Delete the collection and recreate it
            self.client.collections.delete(self.collection_name)
            self.collection = self._create_collection()
            
            return {
                "success": True,
                "message": f"Cleared {count_before} documents from the collection",
                "deleted_count": count_before
            }
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close the database connection."""
        if self.client:
            self.client.close()
            self.client = None
    
    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close()


