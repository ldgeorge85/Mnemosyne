#!/usr/bin/env python3
"""
Main entry point for the Philosophical Multi-Agent Debate System with dynamic agent loading.
Loads philosophical agents from individual definition files.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path if needed for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.orchestrator_dynamic import OrchestratorAgent


def main():
    """
    Run the philosophical debate system with dynamically loaded agents.
    """
    # Sample prompt if none is provided
    sample_prompt = "What is the nature of consciousness?"
    
    # Get user input or use sample
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Enter a philosophical prompt (or press Enter for sample): ")
        if not prompt:
            prompt = sample_prompt
    
    print(f"\nDebating: {prompt}\n")
    
    # Create orchestrator with dynamically loaded agents
    orchestrator = OrchestratorAgent(
        agent_definitions_dir=os.path.join(project_root, "agent_definitions")
    )
    
    # Load environment variables from .env file
    dotenv_path = os.path.join(project_root, ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        # Try loading from .env.example as fallback
        example_path = os.path.join(project_root, ".env.example")
        if os.path.exists(example_path):
            load_dotenv(example_path)
    
    # Get parallel processing setting from environment
    max_parallel = 1  # Default: sequential processing
    if os.environ.get("PARALLEL_AGENTS"):
        try:
            max_parallel = int(os.environ.get("PARALLEL_AGENTS"))
            print(f"Running with parallel processing: {max_parallel} agents at a time")
        except ValueError:
            print("Invalid PARALLEL_AGENTS setting, using sequential processing")
            pass

    # Run the debate with optional parallelism    
    orchestrator.run(prompt, max_parallel=max_parallel)


if __name__ == "__main__":
    main()
