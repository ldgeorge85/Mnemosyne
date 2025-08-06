"""
Outline knowledge base connector.

Outline is a modern team knowledge base with a clean API.
This connector retrieves documents, collections, and search results.

AI Agents: This source provides:
- list_documents(): Get all documents
- get_document(id): Get specific document with full content
- search(query): Search across all documents
- list_collections(): Get document collections/categories
"""

import os
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

from ..base import BaseSource, SourceConfig, Collection


class OutlineSource(BaseSource):
    """
    Connects to Outline knowledge base.
    
    Example usage:
        source = OutlineSource(
            api_key=os.getenv("OUTLINE_API_KEY"),
            base_url=os.getenv("OUTLINE_URL")
        )
        docs = source.list_documents(limit=50)
        content = source.get_document(doc_id)
    """
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        Initialize Outline connection.
        
        Args:
            api_key: Outline API key (or from OUTLINE_API_KEY env var)
            base_url: Outline instance URL (or from OUTLINE_URL env var)
        """
        self.api_key = api_key or os.getenv("OUTLINE_API_KEY")
        self.base_url = (base_url or os.getenv("OUTLINE_URL", "")).rstrip("/")
        
        if not self.api_key or not self.base_url:
            raise ValueError("OUTLINE_API_KEY and OUTLINE_URL required")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.Client(headers=self.headers, timeout=30.0)
        
    def get_config(self) -> SourceConfig:
        return SourceConfig(
            name="outline",
            description="Team knowledge base and documentation",
            auth_type="api_key",
            required_env_vars=["OUTLINE_API_KEY", "OUTLINE_URL"]
        )
    
    def test_connection(self) -> bool:
        """Test connection to Outline API."""
        try:
            response = self.client.post(f"{self.base_url}/api/auth.info")
            return response.status_code == 200
        except Exception:
            return False
    
    def get_collections(self) -> List[Collection]:
        return [
            Collection(
                name="outline_documents",
                description="Knowledge base documents",
                embedding_fields=["title", "text"],
                metadata_fields=["id", "collection_id", "created_by", 
                                "updated_at", "url", "revision"]
            ),
            Collection(
                name="outline_collections", 
                description="Document collections/categories",
                embedding_fields=["name", "description"],
                metadata_fields=["id", "created_at"]
            )
        ]
    
    def list_documents(self, collection_id: str = None, limit: int = 100, 
                      offset: int = 0) -> List[Dict[str, Any]]:
        """
        List documents from Outline.
        
        Args:
            collection_id: Filter by collection (optional)
            limit: Maximum documents to return
            offset: Pagination offset
            
        Returns:
            List of documents with title, text preview, metadata
            
        Example:
            docs = source.list_documents(limit=50)
            for doc in docs:
                print(f"{doc['title']} - {doc['updated_at']}")
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if collection_id:
            params["collectionId"] = collection_id
            
        response = self.client.post(
            f"{self.base_url}/api/documents.list",
            json=params
        )
        response.raise_for_status()
        
        data = response.json()
        documents = []
        
        for doc in data.get("data", []):
            documents.append({
                "id": doc["id"],
                "title": doc["title"],
                "text": doc.get("text", "")[:500],  # Preview
                "collection_id": doc.get("collectionId"),
                "created_by": doc.get("createdBy", {}).get("name"),
                "updated_at": doc.get("updatedAt"),
                "url": doc.get("url"),
                "revision": doc.get("revision")
            })
            
        return documents
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get full document content.
        
        Args:
            document_id: Document ID or share ID
            
        Returns:
            Complete document with full text content
            
        Example:
            doc = source.get_document("doc_123")
            print(doc["text"])  # Full markdown content
        """
        response = self.client.post(
            f"{self.base_url}/api/documents.info",
            json={"id": document_id}
        )
        response.raise_for_status()
        
        doc = response.json()["data"]
        return {
            "id": doc["id"],
            "title": doc["title"],
            "text": doc["text"],  # Full content
            "collection_id": doc.get("collectionId"),
            "created_by": doc.get("createdBy", {}).get("name"),
            "updated_at": doc.get("updatedAt"),
            "url": doc.get("url"),
            "revision": doc.get("revision"),
            "collaborators": [c.get("name") for c in doc.get("collaborators", [])]
        }
    
    def search(self, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Search across all documents.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Search results with relevance context
            
        Example:
            results = source.search("deployment process")
            for result in results:
                print(f"{result['title']} - {result['context']}")
        """
        response = self.client.post(
            f"{self.base_url}/api/documents.search",
            json={"query": query, "limit": limit}
        )
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for result in data.get("data", []):
            doc = result["document"]
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "context": result.get("context", ""),  # Search snippet
                "text": doc.get("text", "")[:500],
                "url": doc.get("url"),
                "updated_at": doc.get("updatedAt")
            })
            
        return results
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all document collections/categories.
        
        Returns:
            List of collections with names and descriptions
            
        Example:
            collections = source.list_collections()
            for col in collections:
                print(f"{col['name']} ({col['document_count']} docs)")
        """
        response = self.client.post(f"{self.base_url}/api/collections.list")
        response.raise_for_status()
        
        data = response.json()
        collections = []
        
        for col in data.get("data", []):
            collections.append({
                "id": col["id"],
                "name": col["name"],
                "description": col.get("description", ""),
                "created_at": col.get("createdAt"),
                "document_count": col.get("documentStructure", [])
            })
            
        return collections