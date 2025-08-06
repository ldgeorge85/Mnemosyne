"""
Document Store Implementation for the Shadow platform.

This module provides document storage functionality for the Shadow AI system,
supporting storage and retrieval of longer texts, references, and structured data.
"""

import logging
import uuid
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

from memory.memory_base import MemoryItem, MemorySystem, SearchableMemorySystem

# Configure logging
logger = logging.getLogger("shadow.memory.document")


class DocumentItem(MemoryItem):
    """
    Extended memory item for document storage.
    
    Adds document-specific metadata and content handling.
    """
    
    def __init__(
        self,
        content: str,
        title: str,
        doc_type: str = "text",
        metadata: Dict[str, Any] = None,
        item_id: Optional[str] = None
    ):
        """
        Initialize a document item.
        
        Args:
            content: The document content
            title: Document title
            doc_type: Document type (e.g., 'text', 'reference', 'code', etc.)
            metadata: Optional metadata for the document
            item_id: Optional ID for the document
        """
        metadata = metadata or {}
        metadata["title"] = title
        metadata["doc_type"] = doc_type
        super().__init__(content, metadata, item_id)
    
    @property
    def title(self) -> str:
        """Get the document title."""
        return self.metadata.get("title", "Untitled Document")
    
    @property
    def doc_type(self) -> str:
        """Get the document type."""
        return self.metadata.get("doc_type", "text")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the document item to a dictionary.
        
        Returns:
            Dict representation of the document item
        """
        result = super().to_dict()
        return result


class InMemoryDocumentStore(SearchableMemorySystem):
    """
    In-memory implementation of a document store.
    
    This provides a simple document storage system using in-memory dictionaries,
    suitable for development and testing.
    """
    
    def __init__(self):
        """Initialize the in-memory document store."""
        super().__init__("InMemoryDocument")
        self.documents: Dict[str, DocumentItem] = {}
    
    def store(self, item: Union[DocumentItem, MemoryItem]) -> str:
        """
        Store a document item.
        
        Args:
            item: The document item to store
            
        Returns:
            ID of the stored document
        """
        # Convert to DocumentItem if necessary
        if not isinstance(item, DocumentItem):
            title = item.metadata.get("title", "Untitled Document")
            doc_type = item.metadata.get("doc_type", "text")
            item = DocumentItem(item.content, title, doc_type, item.metadata, item.item_id)
        
        # Generate an ID if one isn't provided
        if item.item_id is None:
            item.item_id = str(uuid.uuid4())
        
        # Store the document
        self.documents[item.item_id] = item
        logger.info(f"Stored document item with ID {item.item_id} and title '{item.title}'")
        return item.item_id
    
    def retrieve(self, item_id: str) -> Optional[DocumentItem]:
        """
        Retrieve a document item by ID.
        
        Args:
            item_id: ID of the document item to retrieve
            
        Returns:
            The retrieved document item or None if not found
        """
        return self.documents.get(item_id)
    
    def delete(self, item_id: str) -> bool:
        """
        Delete a document item.
        
        Args:
            item_id: ID of the document item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        if item_id in self.documents:
            del self.documents[item_id]
            logger.info(f"Deleted document item with ID {item_id}")
            return True
        
        logger.warning(f"Attempted to delete non-existent document item with ID {item_id}")
        return False
    
    def clear(self) -> bool:
        """
        Clear all document items.
        
        Returns:
            True if the documents were cleared, False otherwise
        """
        self.documents.clear()
        logger.info("Cleared all document items")
        return True
    
    def search(self, query: str, limit: int = 5) -> List[DocumentItem]:
        """
        Search for document items matching a query.
        
        Simple keyword-based search implementation.
        
        Args:
            query: The search query
            limit: Maximum number of items to return
            
        Returns:
            List of document items matching the query
        """
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in self.documents.items():
            # Search in content
            if query_lower in doc.content.lower():
                results.append(doc)
                if len(results) >= limit:
                    break
            
            # Search in title
            elif query_lower in doc.title.lower():
                results.append(doc)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_all_documents(self) -> List[DocumentItem]:
        """
        Get all stored documents.
        
        Returns:
            List of all document items
        """
        return list(self.documents.values())
    
    def get_documents_by_type(self, doc_type: str) -> List[DocumentItem]:
        """
        Get documents by type.
        
        Args:
            doc_type: The document type to filter by
            
        Returns:
            List of document items of the specified type
        """
        return [doc for doc in self.documents.values() if doc.doc_type == doc_type]


class FileSystemDocumentStore(InMemoryDocumentStore):
    """
    File system-based implementation of a document store.
    
    This provides persistent storage of documents on the file system, with in-memory 
    indexing for fast access.
    """
    
    def __init__(self, storage_dir: str = "document_store"):
        """
        Initialize the file system document store.
        
        Args:
            storage_dir: Directory for document storage
        """
        super().__init__()
        self.storage_dir = Path(storage_dir)
        self.name = "FileSystemDocument"
        
        # Create storage directory if it doesn't exist
        if not self.storage_dir.exists():
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing documents
        self._load_documents()
    
    def _load_documents(self):
        """Load documents from the file system."""
        if not self.storage_dir.exists():
            return
        
        # Load document index
        index_path = self.storage_dir / "index.json"
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    index_data = json.load(f)
                
                # Load each document
                for doc_id, doc_info in index_data.items():
                    doc_path = self.storage_dir / f"{doc_id}.txt"
                    if doc_path.exists():
                        with open(doc_path, 'r') as f:
                            content = f.read()
                        
                        # Create document item
                        title = doc_info.get("title", "Untitled Document")
                        doc_type = doc_info.get("doc_type", "text")
                        metadata = doc_info.get("metadata", {})
                        
                        # Add document to in-memory store
                        doc = DocumentItem(content, title, doc_type, metadata, doc_id)
                        self.documents[doc_id] = doc
                
                logger.info(f"Loaded {len(self.documents)} documents from file system")
            
            except Exception as e:
                logger.error(f"Error loading documents from file system: {str(e)}")
    
    def _save_index(self):
        """Save document index to file system."""
        index_data = {}
        for doc_id, doc in self.documents.items():
            index_data[doc_id] = {
                "title": doc.title,
                "doc_type": doc.doc_type,
                "metadata": doc.metadata,
                "created_at": doc.created_at
            }
        
        # Save index
        index_path = self.storage_dir / "index.json"
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def store(self, item: Union[DocumentItem, MemoryItem]) -> str:
        """
        Store a document item in the file system.
        
        Args:
            item: The document item to store
            
        Returns:
            ID of the stored document
        """
        # Use parent class to add to in-memory store first
        doc_id = super().store(item)
        doc = self.documents[doc_id]
        
        try:
            # Save document content
            doc_path = self.storage_dir / f"{doc_id}.txt"
            with open(doc_path, 'w') as f:
                f.write(doc.content)
            
            # Update index
            self._save_index()
            logger.info(f"Stored document '{doc.title}' to file system with ID {doc_id}")
        
        except Exception as e:
            logger.error(f"Error storing document to file system: {str(e)}")
        
        return doc_id
    
    def delete(self, item_id: str) -> bool:
        """
        Delete a document item from the file system.
        
        Args:
            item_id: ID of the document item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        # Check if document exists
        if item_id not in self.documents:
            return False
        
        try:
            # Delete document file
            doc_path = self.storage_dir / f"{item_id}.txt"
            if doc_path.exists():
                os.remove(doc_path)
            
            # Remove from in-memory store
            del self.documents[item_id]
            
            # Update index
            self._save_index()
            logger.info(f"Deleted document with ID {item_id} from file system")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting document from file system: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all document items from the file system.
        
        Returns:
            True if the documents were cleared, False otherwise
        """
        try:
            # Delete all document files
            for doc_id in list(self.documents.keys()):
                doc_path = self.storage_dir / f"{doc_id}.txt"
                if doc_path.exists():
                    os.remove(doc_path)
            
            # Clear in-memory store
            self.documents.clear()
            
            # Clear index
            index_path = self.storage_dir / "index.json"
            if index_path.exists():
                os.remove(index_path)
            
            logger.info("Cleared all documents from file system")
            return True
        
        except Exception as e:
            logger.error(f"Error clearing documents from file system: {str(e)}")
            return False
