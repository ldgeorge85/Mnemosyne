"""
Memory Integration Test for the Shadow System.

This script tests the integration of the memory system with the Shadow orchestrator
and the specialized agents.
"""

import logging
import sys
import os
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("shadow.test.memory")

# Import required components
from memory.memory_manager import MemoryManager
from memory.vector_memory import InMemoryVectorStore, EmbeddingService
from memory.document_store import InMemoryDocumentStore
from memory.relational_store import InMemoryRelationalStore

from orchestrator.shadow_agent import ShadowAgent
from orchestrator.memory_integration import OrchestratorMemory

from agents.engineer.agent import EngineerAgent
from agents.librarian.agent import LibrarianAgent
from agents.priest.agent import PriestAgent


def initialize_test_memory() -> MemoryManager:
    """
    Initialize the memory manager with test data.
    
    Returns:
        Initialized memory manager with test data
    """
    # Create memory components with simple in-memory implementations
    embedding_service = EmbeddingService(provider="mock")
    vector_store = InMemoryVectorStore()
    document_store = InMemoryDocumentStore()
    relational_store = InMemoryRelationalStore()
    
    # Create memory manager
    memory_manager = MemoryManager(
        vector_store=vector_store,
        document_store=document_store,
        relational_store=relational_store
    )
    
    # Set the embedding service
    memory_manager.embedding_service = embedding_service
    
    # Add test knowledge to memory
    memory_manager.store_knowledge(
        title="AI Ethics Principles",
        content="AI systems should be designed to be transparent, fair, and accountable. " +
                "They should respect privacy, provide security, and avoid harm. " +
                "Ethical AI frameworks typically emphasize human oversight and control.",
        source="Test Source: Ethics Guide"
    )
    
    memory_manager.store_knowledge(
        title="Modern Software Architecture Patterns",
        content="Microservices, event-driven architecture, and serverless computing " +
                "are common modern software architecture patterns. Each has benefits " +
                "and trade-offs in terms of scalability, maintenance, and complexity.",
        source="Test Source: Architecture Guide"
    )
    
    memory_manager.store_knowledge(
        title="Data Organization Best Practices",
        content="Effective data organization involves proper schema design, " +
                "normalization where appropriate, metadata management, and " +
                "clear documentation of data lineage and relationships.",
        source="Test Source: Data Guide"
    )
    
    # Add test entities to memory
    memory_manager.store_entity(
        "Utilitarianism", 
        "ethical_principle", 
        "An ethical philosophy that determines right action based on maximizing happiness " +
        "or well-being for the greatest number of individuals.",
        {"key_proponent": "John Stuart Mill"}
    )
    
    memory_manager.store_entity(
        "Microservice Architecture", 
        "technical_architecture", 
        "A software architecture pattern where an application is built as a collection " +
        "of small, independent services that communicate through well-defined APIs.",
        {"scalability": "high", "complexity": "medium to high"}
    )
    
    memory_manager.store_entity(
        "Vector Database", 
        "technology", 
        "A database optimized for storing and searching vector embeddings, " +
        "often used for semantic search and AI applications.",
        {"example_products": ["Pinecone", "Weaviate", "Milvus"]}
    )
    
    logger.info("Test memory initialized with sample data")
    return memory_manager


def test_memory_integration():
    """
    Test the integration of memory system with the Shadow orchestrator.
    """
    logger.info("Starting memory integration test")
    
    # Initialize test memory
    memory_manager = initialize_test_memory()
    
    # Create orchestrator memory
    orchestrator_memory = OrchestratorMemory(memory_manager)
    
    # Create specialized agents
    engineer = EngineerAgent()
    librarian = LibrarianAgent()
    priest = PriestAgent()
    
    # Create Shadow orchestrator with memory
    shadow = ShadowAgent(
        agents={
            "engineer": engineer,
            "librarian": librarian,
            "priest": priest
        },
        memory=orchestrator_memory
    )
    
    logger.info("Shadow system initialized with memory")
    
    # Test queries that should use memory context
    test_queries = [
        "What are some ethical considerations for AI systems?",
        "Can you explain microservice architecture?",
        "What's a good approach for organizing data?",
        "Is utilitarianism a good moral philosophy?",
        "How do vector databases work?"
    ]
    
    logger.info("Processing test queries")
    
    # Process each query and check if memory context is being used
    for i, query in enumerate(test_queries):
        logger.info(f"Query {i+1}: {query}")
        
        # Process the query
        response = shadow.process_request(query)
        
        # Log the response
        logger.info(f"Response length: {len(response)}")
        logger.info(f"Response snippet: {response[:100]}...")
        
        print(f"\n--- Query {i+1}: {query} ---")
        print(response[:500] + "..." if len(response) > 500 else response)
        print("-" * 50)
    
    logger.info("Memory integration test completed")


if __name__ == "__main__":
    test_memory_integration()
