"""
Test script for the streaming LLM connector.

This script tests the streaming functionality of the LLM connector
by making a direct call to the streaming connector.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path to allow imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.llm_connector import OpenAIConnector
from utils.streaming_llm_connector import StreamingOpenAIConnector


async def test_streaming():
    """Test the streaming LLM connector."""
    print("Testing streaming LLM connector...")
    
    # Create a base connector
    base_connector = OpenAIConnector()
    
    # Create a streaming connector
    streaming_connector = StreamingOpenAIConnector(base_connector)
    
    # Define a simple callback function
    def callback(chunk):
        print(f"Received chunk: {chunk}")
    
    # Test the streaming connector
    system_prompt = "You are a helpful assistant."
    user_input = "Write a short poem about AI."
    
    print("\nStreaming response:")
    async for chunk in streaming_connector.generate_text_stream(
        system_prompt=system_prompt,
        user_input=user_input,
        callback=callback
    ):
        # The callback will print each chunk
        pass
    
    print("\nStreaming test completed.")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_streaming())
