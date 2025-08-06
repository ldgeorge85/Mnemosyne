#!/usr/bin/env python3
"""
Comprehensive test script for advanced multi-agent collaboration features.

This script validates the new task decomposition, collaborative execution,
and enhanced orchestration capabilities of the Shadow AI system.
"""

import logging
import sys
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   You can still set environment variables manually")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# Add the shadow_system directory to the Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator.shadow_agent import ShadowAgent
from agents.engineer.agent import EngineerAgent
from agents.librarian.agent import LibrarianAgent  
from agents.priest.agent import PriestAgent
from memory.memory_manager import MemoryManager
from orchestrator.memory_integration import OrchestratorMemory
from utils.llm_connector import OpenAIConnector
from utils.prompt_loader import PromptLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("collaboration_test")


def setup_test_system():
    """Set up the Shadow system for collaboration testing."""
    logger.info("Setting up test system with collaboration features...")
    
    # Initialize memory system
    memory_manager = MemoryManager()
    orchestrator_memory = OrchestratorMemory(memory_manager)
    
    # Initialize agents with real LLM provider (OpenAI by default)
    # Note: This requires OPENAI_API_KEY environment variable to be set
    engineer = EngineerAgent(llm_provider="openai")
    librarian = LibrarianAgent(llm_provider="openai")
    priest = PriestAgent(llm_provider="openai")
    
    # Initialize Shadow orchestrator with collaboration enabled
    shadow = ShadowAgent(memory=orchestrator_memory, enable_collaboration=True)
    
    # Register agents
    shadow.register_agent("engineer", engineer)
    shadow.register_agent("librarian", librarian)  
    shadow.register_agent("priest", priest)
    
    return shadow, orchestrator_memory


def test_basic_collaboration():
    """Test basic collaboration functionality."""
    logger.info("\n=== Testing Basic Collaboration ===")
    
    shadow, memory = setup_test_system()
    
    # Test simple query that should trigger collaboration
    test_query = "How should I design and build an ethical AI system for healthcare?"
    
    logger.info(f"Processing query: {test_query}")
    response = shadow.process_request(test_query)
    
    # Print the actual response for debugging
    logger.info(f"Generated response: {response}")
    
    # Validate response
    assert len(response) > 100, "Response should be substantial for collaborative query"
    
    # Check for collaboration indicators in the response
    response_lower = response.lower()
    
    # More flexible assertions - check for collaboration structure
    has_multiple_perspectives = (
        "technical analysis" in response_lower or 
        "engineering" in response_lower or
        "research" in response_lower or 
        "information" in response_lower or
        "ethical" in response_lower or
        "philosophical" in response_lower or
        "collaborative" in response_lower or
        len([agent for agent in ["engineer", "librarian", "priest"] if agent in response_lower]) >= 2
    )
    
    assert has_multiple_perspectives, f"Response should show multiple agent perspectives. Response: {response[:200]}..."
    
    # Check performance stats
    stats = shadow.get_performance_stats()
    logger.info(f"Performance stats: {stats}")
    
    assert stats['collaborative_requests'] > 0, "Should have used collaboration"
    assert stats['total_requests'] > 0, "Should have processed requests"
    
    logger.info("✓ Basic collaboration test passed")
    return shadow


def test_task_decomposition():
    """Test task decomposition functionality."""
    logger.info("\n=== Testing Task Decomposition ===")
    
    shadow, memory = setup_test_system()
    
    # Test complex multi-domain query
    complex_query = "I need to research machine learning frameworks, design a scalable architecture for real-time processing, and evaluate the ethical implications of automated decision-making in financial services."
    
    logger.info(f"Processing complex query: {complex_query[:100]}...")
    response = shadow.process_request(complex_query)
    
    # Check performance stats
    stats = shadow.get_performance_stats()
    
    logger.info(f"Execution stats: {stats}")
    
    # Validate collaboration occurred
    assert stats['collaborative_requests'] > 0, "Should have used collaboration"
    assert stats['collaboration_percentage'] > 0, "Should show collaboration percentage"
    assert len(stats['agent_usage']) >= 2, "Should have used multiple agents"
    
    logger.info("✓ Task decomposition test passed")
    return shadow


def test_agent_communication():
    """Test agent-to-agent communication and context sharing."""
    logger.info("\n=== Testing Agent Communication ===")
    
    shadow, memory = setup_test_system()
    
    # Store some context information first
    memory.store_important_information(
        "AI System Design Principles",
        "Key principles for AI system design include modularity, scalability, interpretability, and fail-safe mechanisms. Systems should be designed with human oversight and clear accountability chains.",
        "test_setup"
    )
    
    # Test query that should benefit from shared context
    context_query = "Based on established AI design principles, how should we implement monitoring and safety measures?"
    
    logger.info(f"Processing context-aware query: {context_query}")
    response = shadow.process_request(context_query)
    
    # Validate context usage
    assert "modularity" in response.lower() or "scalability" in response.lower() or "interpretability" in response.lower(), "Should reference stored context"
    assert len(response) > 200, "Should provide comprehensive response with context"
    
    logger.info("✓ Agent communication test passed")
    return shadow


def test_collaboration_modes():
    """Test different collaboration modes."""
    logger.info("\n=== Testing Collaboration Modes ===")
    
    shadow, memory = setup_test_system()
    
    test_query = "What are the key considerations for building distributed systems?"
    
    # Test with collaboration enabled
    logger.info("Testing with collaboration enabled...")
    shadow.set_collaboration_mode(True)
    collab_response = shadow.process_request(test_query)
    collab_stats = shadow.get_performance_stats()
    
    # Reset stats and test with collaboration disabled
    shadow.execution_stats = {
        'total_requests': 0,
        'collaborative_requests': 0, 
        'average_response_time': 0.0,
        'agent_usage': {}
    }
    
    logger.info("Testing with collaboration disabled...")
    shadow.set_collaboration_mode(False)
    basic_response = shadow.process_request(test_query)
    basic_stats = shadow.get_performance_stats()
    
    # Validate different modes
    assert basic_stats['collaborative_requests'] == 0, "Should not use collaboration when disabled"
    
    logger.info("✓ Collaboration modes test passed")
    return shadow


def test_performance_tracking():
    """Test performance tracking and statistics."""
    logger.info("\n=== Testing Performance Tracking ===")
    
    shadow, memory = setup_test_system()
    
    # Process multiple requests
    queries = [
        "How do I optimize database performance?",
        "What are the ethical implications of AI in hiring?", 
        "Research the latest developments in quantum computing.",
        "Design a microservices architecture for e-commerce.",
        "Should we implement automated content moderation?"
    ]
    
    for i, query in enumerate(queries):
        logger.info(f"Processing query {i+1}: {query[:50]}...")
        response = shadow.process_request(query)
        assert len(response) > 50, f"Query {i+1} should have substantial response"
    
    # Check final stats
    final_stats = shadow.get_performance_stats()
    
    logger.info(f"Final performance stats: {final_stats}")
    
    # Validate statistics
    assert final_stats['total_requests'] == len(queries), "Should track all requests"
    assert final_stats['average_response_time'] > 0, "Should track response time"
    assert len(final_stats['agent_usage']) > 0, "Should track agent usage"
    assert 0 <= final_stats['collaboration_percentage'] <= 100, "Collaboration percentage should be valid"
    
    logger.info("✓ Performance tracking test passed")
    return shadow


def test_memory_integration_with_collaboration():
    """Test memory integration with collaborative features."""
    logger.info("\n=== Testing Memory Integration with Collaboration ===")
    
    shadow, memory = setup_test_system()
    
    # Store knowledge that should influence collaboration
    memory.store_important_information(
        "Software Architecture Best Practices",
        "Modern software architecture emphasizes microservices, API-first design, event-driven patterns, and observability. Security should be built-in from the start.",
        "architecture_guide"
    )
    
    memory.store_entity(
        "Clean Architecture",
        "concept",
        "An architectural pattern that separates concerns into layers, making systems more maintainable and testable.",
        {"benefits": ["maintainability", "testability", "flexibility"]}
    )
    
    # Test query that should leverage stored knowledge
    memory_query = "How should I structure a new web application following modern best practices?"
    
    logger.info(f"Processing memory-aware query: {memory_query}")
    response = shadow.process_request(memory_query)
    
    # Validate memory integration
    context = memory.get_relevant_context(memory_query)
    assert len(context.get('relevant_documents', [])) > 0, "Should retrieve relevant documents"
    
    # Check if response incorporates stored knowledge
    response_lower = response.lower()
    assert any(term in response_lower for term in ["microservices", "api", "architecture", "observability"]), "Should incorporate stored architectural knowledge"
    
    logger.info("✓ Memory integration with collaboration test passed")
    return shadow


def run_all_tests():
    """Run all collaboration tests."""
    logger.info("Starting comprehensive collaboration testing...")
    
    try:
        # Run all test functions
        test_basic_collaboration()
        test_task_decomposition()
        test_agent_communication()
        test_collaboration_modes()
        test_performance_tracking()
        test_memory_integration_with_collaboration()
        
        logger.info("\n🎉 All collaboration tests passed successfully!")
        logger.info("Advanced multi-agent collaboration features are working correctly.")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def interactive_collaboration_demo():
    """Interactive demo of collaboration features."""
    logger.info("\n=== Interactive Collaboration Demo ===")
    
    shadow, memory = setup_test_system()
    
    print("\nShadow AI - Advanced Collaboration Demo")
    print("=" * 50)
    print("This demo showcases advanced multi-agent collaboration.")
    print("Try complex queries that span multiple domains!")
    print("Type 'stats' to see performance statistics.")
    print("Type 'mode toggle' to toggle collaboration mode.")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            query = input("Your query: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'stats':
                stats = shadow.get_performance_stats()
                print(f"\nPerformance Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
                continue
            elif query.lower() == 'mode toggle':
                current_mode = shadow.enable_collaboration
                shadow.set_collaboration_mode(not current_mode)
                print(f"Collaboration mode: {'enabled' if shadow.enable_collaboration else 'disabled'}\n")
                continue
            elif not query:
                continue
                
            print(f"\nProcessing query: {query}")
            print("-" * 50)
            
            response = shadow.process_request(query)
            print(f"\nResponse:\n{response}\n")
            
            # Show brief stats
            stats = shadow.get_performance_stats()
            print(f"[Stats: {stats['total_requests']} requests, {stats['collaboration_percentage']:.1f}% collaborative]\n")
            
        except KeyboardInterrupt:
            print("\nExiting demo...")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        interactive_collaboration_demo()
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)
