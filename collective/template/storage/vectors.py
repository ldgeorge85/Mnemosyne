"""
Vector storage implementation using Qdrant.

AI Agents: This handles all vector database operations.
Collections are automatically created based on source configurations.
"""

import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import structlog
from langchain.embeddings import OpenAIEmbeddings
import uuid

logger = structlog.get_logger()


class VectorStore:
    """
    Manages vector storage for knowledge base.
    
    AI Agents: Key methods:
    - add_documents(): Store new documents
    - search(): Semantic search
    - list_collections(): See what's stored
    """
    
    def __init__(self, url: str = None):
        """
        Initialize vector store connection.
        
        Args:
            url: Qdrant URL (defaults to QDRANT_URL env var)
        """
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.client = None
        self.embeddings = OpenAIEmbeddings()
        
    async def initialize(self):
        """Initialize connection to Qdrant."""
        try:
            self.client = QdrantClient(url=self.url)
            logger.info(f"Connected to Qdrant at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant", error=str(e))
            raise
            
    async def health_check(self) -> bool:
        """Check if vector store is healthy."""
        try:
            # Try to get collections
            self.client.get_collections()
            return True
        except:
            return False
    
    async def create_collection(self, name: str, vector_size: int = 1536):
        """
        Create a new collection if it doesn't exist.
        
        Args:
            name: Collection name
            vector_size: Embedding dimension (1536 for OpenAI)
        """
        try:
            collections = self.client.get_collections().collections
            if not any(col.name == name for col in collections):
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {name}")
        except Exception as e:
            logger.error(f"Error creating collection {name}", error=str(e))
            raise
    
    async def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        collection: str,
        embedding_fields: List[str] = ["text", "content", "summary"]
    ):
        """
        Add documents to vector store.
        
        Args:
            documents: List of documents with text and metadata
            collection: Target collection name
            embedding_fields: Fields to create embeddings from
            
        AI Agents: Documents should have structure like:
            {
                "text": "main content",
                "title": "document title",
                "id": "unique_id",
                ...other metadata...
            }
        """
        if not documents:
            return
            
        # Ensure collection exists
        await self.create_collection(collection)
        
        points = []
        for doc in documents:
            # Find text to embed
            text_to_embed = ""
            for field in embedding_fields:
                if field in doc:
                    text_to_embed += str(doc[field]) + " "
            
            if not text_to_embed.strip():
                logger.warning(f"No text to embed in document: {doc.get('id', 'unknown')}")
                continue
            
            # Generate embedding
            try:
                embedding = await self.embeddings.aembed_query(text_to_embed.strip())
            except Exception as e:
                logger.error(f"Embedding generation failed", error=str(e))
                continue
            
            # Create point
            point_id = str(uuid.uuid4())
            payload = {
                **doc,
                "_embedded_text": text_to_embed.strip()[:1000]  # Store what was embedded
            }
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )
        
        # Batch upsert
        if points:
            self.client.upsert(
                collection_name=collection,
                points=points
            )
            logger.info(f"Added {len(points)} documents to {collection}")
    
    async def search(
        self, 
        query: str, 
        collections: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search across collections.
        
        Args:
            query: Search query
            collections: Specific collections to search (None = all)
            limit: Maximum results per collection
            
        Returns:
            Combined search results with scores
        """
        # Generate query embedding
        try:
            query_embedding = await self.embeddings.aembed_query(query)
        except Exception as e:
            logger.error(f"Query embedding failed", error=str(e))
            raise
        
        # Get collections to search
        if not collections:
            all_collections = self.client.get_collections().collections
            collections = [col.name for col in all_collections]
        
        # Search each collection
        all_results = []
        for collection in collections:
            try:
                results = self.client.search(
                    collection_name=collection,
                    query_vector=query_embedding,
                    limit=limit
                )
                
                for result in results:
                    all_results.append({
                        "collection": collection,
                        "score": result.score,
                        "document": result.payload,
                        "id": result.id
                    })
                    
            except Exception as e:
                logger.warning(f"Search failed for collection {collection}", error=str(e))
                continue
        
        # Sort by score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        return all_results[:limit]
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections with statistics.
        
        AI Agents: Shows what knowledge is available.
        """
        collections = []
        
        for col in self.client.get_collections().collections:
            info = self.client.get_collection(col.name)
            collections.append({
                "name": col.name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "indexed_vectors_count": info.indexed_vectors_count
            })
        
        return collections
    
    async def delete_collection(self, name: str):
        """Delete a collection."""
        try:
            self.client.delete_collection(name)
            logger.info(f"Deleted collection: {name}")
        except Exception as e:
            logger.error(f"Error deleting collection {name}", error=str(e))
            raise