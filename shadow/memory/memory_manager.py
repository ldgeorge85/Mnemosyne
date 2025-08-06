"""
Memory Manager for the Shadow platform.

This module provides a unified interface to the various memory systems
in the Shadow AI platform, coordinating between vector storage, document storage,
and relational storage.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
import json

from memory.memory_base import MemoryItem, MemorySystem, SearchableMemorySystem, VectorMemorySystem
from memory.vector_memory import InMemoryVectorStore, EmbeddingService
from memory.document_store import DocumentItem, InMemoryDocumentStore, FileSystemDocumentStore
from memory.relational_store import RelationalItem, InMemoryRelationalStore, SQLiteRelationalStore

# Configure logging
logger = logging.getLogger("shadow.memory")


class MemoryManager:
    """
    Central memory manager for the Shadow AI system.
    
    Provides a unified interface for storing and retrieving memory items
    across different memory storage types.
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorMemorySystem] = None,
        document_store: Optional[SearchableMemorySystem] = None,
        relational_store: Optional[MemorySystem] = None,
        embedding_service: Optional[EmbeddingService] = None
    ):
        """
        Initialize the memory manager.
        
        Args:
            vector_store: Vector memory system for semantic search
            document_store: Document memory system for text storage
            relational_store: Relational memory system for structured data
            embedding_service: Service for creating embeddings
        """
        # Initialize memory systems with defaults if not provided
        self.vector_store = vector_store or InMemoryVectorStore()
        self.document_store = document_store or InMemoryDocumentStore()
        self.relational_store = relational_store or InMemoryRelationalStore()
        # Use OpenAI embeddings by default for real testing
        self.embedding_service = embedding_service or EmbeddingService("openai")
        
        logger.info("Initialized Shadow Memory Manager")
    
    def store_memory(self, item: MemoryItem, memory_type: str = "vector") -> str:
        """
        Store a memory item in the appropriate storage system.
        
        Args:
            item: The memory item to store
            memory_type: Type of memory storage to use ("vector", "document", "relational")
            
        Returns:
            ID of the stored item
        """
        if memory_type == "vector":
            # Generate embedding and store in vector store
            embedding = self.embedding_service.get_embedding(item.content)
            return self.vector_store.store_with_embedding(item, embedding)
            
        elif memory_type == "document":
            # Store as document
            return self.document_store.store(item)
            
        elif memory_type == "relational":
            # Store as relational item
            return self.relational_store.store(item)
            
        else:
            logger.warning(f"Unknown memory type: {memory_type}, defaulting to vector")
            embedding = self.embedding_service.get_embedding(item.content)
            return self.vector_store.store_with_embedding(item, embedding)
    
    def retrieve_memory(self, item_id: str, memory_type: str = None) -> Optional[MemoryItem]:
        """
        Retrieve a memory item by ID.
        
        Args:
            item_id: ID of the memory item to retrieve
            memory_type: Optional type of memory storage to search
            
        Returns:
            The retrieved memory item or None if not found
        """
        if memory_type == "vector":
            return self.vector_store.retrieve(item_id)
            
        elif memory_type == "document":
            return self.document_store.retrieve(item_id)
            
        elif memory_type == "relational":
            return self.relational_store.retrieve(item_id)
            
        else:
            # Try all storage types
            item = self.vector_store.retrieve(item_id)
            if item:
                return item
                
            item = self.document_store.retrieve(item_id)
            if item:
                return item
                
            item = self.relational_store.retrieve(item_id)
            return item
    
    def search_memories(self, query: str, limit: int = 5) -> Dict[str, List[MemoryItem]]:
        """
        Search for memory items across all storage systems.
        
        Args:
            query: The search query
            limit: Maximum number of items to return per storage type
            
        Returns:
            Dictionary of storage type to list of matching items
        """
        results = {}
        
        # Search document store
        doc_results = self.document_store.search(query, limit)
        if doc_results:
            results["document"] = doc_results
        
        # Search vector store (semantic search)
        query_embedding = self.embedding_service.get_embedding(query)
        vector_results = self.vector_store.search_by_vector(query_embedding, limit)
        if vector_results:
            results["vector"] = [item for item, _ in vector_results]
        
        return results
    
    def store_conversation_memory(self, conversation: Dict[str, Any]) -> str:
        """
        Store a conversation in memory.
        
        Args:
            conversation: Dictionary containing conversation data
            
        Returns:
            ID of the stored conversation
        """
        content = json.dumps(conversation["messages"]) if "messages" in conversation else ""
        metadata = {
            "conversation_id": conversation.get("id", ""),
            "title": conversation.get("title", "Untitled Conversation"),
            "timestamp": conversation.get("timestamp", "")
        }
        
        item = DocumentItem(
            content=content,
            title=metadata["title"],
            doc_type="conversation",
            metadata=metadata
        )
        
        return self.store_memory(item, "document")
    
    def store_knowledge(self, title: str, content: str, source: str = None, tags: List[str] = None) -> Dict[str, str]:
        """
        Store knowledge in both vector and document stores.
        
        Args:
            title: Title of the knowledge item
            content: Content of the knowledge item
            source: Optional source of the knowledge
            tags: Optional list of tags for the knowledge
            
        Returns:
            Dictionary of storage type to ID of stored item
        """
        metadata = {
            "title": title,
            "source": source,
            "tags": tags or []
        }
        
        # Store in document store
        doc_item = DocumentItem(
            content=content,
            title=title,
            doc_type="knowledge",
            metadata=metadata
        )
        doc_id = self.document_store.store(doc_item)
        
        # Store in vector store for semantic search
        vector_item = MemoryItem(
            content=content,
            metadata=metadata
        )
        embedding = self.embedding_service.get_embedding(content)
        vector_id = self.vector_store.store_with_embedding(vector_item, embedding)
        
        return {
            "document": doc_id,
            "vector": vector_id
        }
    
    def store_entity(
        self, 
        name: str, 
        entity_type: str,
        description: str, 
        properties: Dict[str, Any] = None,
        relationships: Dict[str, List[str]] = None
    ) -> str:
        """
        Store an entity in the relational store.
        
        Args:
            name: Name of the entity
            entity_type: Type of entity
            description: Description of the entity
            properties: Entity properties
            relationships: Entity relationships
            
        Returns:
            ID of the stored entity
        """
        item = RelationalItem(
            content=description,
            entity_type=entity_type,
            properties=properties or {},
            relationships=relationships or {},
            metadata={"name": name}
        )
        
        return self.relational_store.store(item)
    
    def get_agent_context(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """
        Get context for agent processing based on a user query.
        
        Performs semantic search to find relevant information from all memory systems.
        
        Args:
            query: User query to find context for
            limit: Maximum number of items to include from each source
            
        Returns:
            Dictionary containing relevant context from memory
        """
        context = {
            "relevant_documents": [],
            "relevant_entities": [],
            "related_conversations": []
        }
        
        # Search for relevant knowledge
        search_results = self.search_memories(query, limit)
        
        # Process document results
        if "document" in search_results:
            for item in search_results["document"]:
                if item.metadata.get("doc_type") == "knowledge":
                    context["relevant_documents"].append({
                        "title": item.metadata.get("title", "Untitled"),
                        "content": item.content,
                        "source": item.metadata.get("source", "Unknown")
                    })
                elif item.metadata.get("doc_type") == "conversation":
                    context["related_conversations"].append({
                        "title": item.metadata.get("title", "Untitled Conversation"),
                        "content": item.content
                    })
        
        # Process vector results (may overlap with documents, but may provide different matches)
        if "vector" in search_results:
            for item in search_results["vector"]:
                if "title" in item.metadata:
                    # Check if this is a duplicate of a document already added
                    is_duplicate = False
                    for doc in context["relevant_documents"]:
                        if doc["title"] == item.metadata["title"]:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        context["relevant_documents"].append({
                            "title": item.metadata.get("title", "Untitled"),
                            "content": item.content,
                            "source": item.metadata.get("source", "Unknown")
                        })
        
        # Get relevant entities by performing a simple keyword match on entity names
        # In a more sophisticated implementation, we would use the embedding to find related entities
        from memory.relational_store import SQLiteRelationalStore
        if isinstance(self.relational_store, SQLiteRelationalStore):
            # For SQLite store, we need to query differently
            # This is simplified - in reality you'd want a more sophisticated query
            pass
        else:
            # For in-memory store, we can search directly
            if isinstance(self.relational_store, InMemoryRelationalStore):
                for entity in self.relational_store.entities.values():
                    entity_name = entity.metadata.get("name", "").lower()
                    if entity_name and (entity_name in query.lower() or 
                            any(word in entity_name for word in query.lower().split())):
                        context["relevant_entities"].append({
                            "name": entity_name,
                            "type": entity.entity_type,
                            "description": entity.content,
                            "properties": entity.properties
                        })
                        if len(context["relevant_entities"]) >= limit:
                            break
        
        return context


# Create default memory manager for easy import
default_memory_manager = MemoryManager()
