"""
Test script for the Shadow AI Agent System.

This script tests the end-to-end functionality of the Shadow system,
including the orchestrator, classifier, and mock agents.
"""

import sys
import logging
from pprint import pprint

# Import Shadow components
from orchestrator.shadow_agent import ShadowAgent
from orchestrator.classifier import default_classifier
from agents.engineer.agent import default_engineer
from agents.librarian.agent import default_librarian
from agents.priest.agent import default_priest

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("shadow.test")


def init_shadow_system():
    """
    Initialize the Shadow system with all agents.
    
    Returns:
        Initialized ShadowAgent instance
    """
    logger.info("Initializing Shadow system for testing")
    
    # Create Shadow orchestrator
    shadow = ShadowAgent()
    
    # Register agents
    shadow.register_agent("engineer", default_engineer)
    shadow.register_agent("librarian", default_librarian)
    shadow.register_agent("priest", default_priest)
    
    logger.info("Shadow system initialized successfully")
    return shadow


def test_classification():
    """Test the input classifier."""
    logger.info("Testing input classifier...")
    
    test_inputs = [
        "How do I build a bridge?",
        "Can you find information about quantum physics?",
        "Is it ethical to use AI for surveillance?",
        "What's the capital of France?",
        "Design a system to optimize energy consumption in a smart home."
    ]
    
    for input_text in test_inputs:
        agents = default_classifier.classify_task(input_text)
        print(f"Input: '{input_text}'\nClassified agents: {agents}\n")
    
    logger.info("Classification testing complete")


def test_agent_responses():
    """Test individual agent responses."""
    logger.info("Testing individual agent responses...")
    
    test_input = "How do systems work together?"
    
    print("Engineer response:")
    print(default_engineer.process_request(test_input))
    print("\nLibrarian response:")
    print(default_librarian.process_request(test_input))
    print("\nPriest response:")
    print(default_priest.process_request(test_input))
    
    logger.info("Agent response testing complete")


def test_orchestration():
    """Test the full orchestration process."""
    logger.info("Testing orchestration...")
    
    shadow = init_shadow_system()
    
    test_inputs = [
        "How do I build a bridge?",
        "Can you find information about quantum physics?",
        "Is it ethical to use AI for surveillance?",
        "Design a system to optimize energy consumption in a smart home."
    ]
    
    for input_text in test_inputs:
        print(f"\n--- Testing input: '{input_text}' ---\n")
        response = shadow.process_request(input_text)
        print("Shadow Response:")
        print(response)
        print("\n--- End test ---\n")
    
    logger.info("Orchestration testing complete")


def main():
    """Run all tests."""
    print("\n=== SHADOW AI AGENT SYSTEM TESTS ===\n")
    
    print("\n--- CLASSIFICATION TESTS ---\n")
    test_classification()
    
    print("\n--- AGENT RESPONSE TESTS ---\n")
    test_agent_responses()
    
    print("\n--- ORCHESTRATION TESTS ---\n")
    test_orchestration()
    
    print("\n=== ALL TESTS COMPLETED ===\n")


if __name__ == "__main__":
    main()
