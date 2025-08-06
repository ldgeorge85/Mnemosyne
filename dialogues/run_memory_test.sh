#!/bin/bash
# Script to test the philosophical debate system with memory integration

# Create necessary directories
mkdir -p ./memory/agents ./memory/debates ./memory/indexes ./agent_definitions

# Build and run the container
docker compose build

# First, convert agent definitions if needed
#docker compose run --rm debate-system python -m src.utils.convert_agent_definitions

# Run a first debate
echo "Running first debate: Nature of Consciousness"
docker compose run --rm -e PARALLEL_AGENTS=2 debate-system python src/main_with_memory.py "What is the nature of consciousness?"

# Run a second debate on a related topic to test memory retrieval
echo ""
echo "Running second debate: Mind-Body problem (related to consciousness)"
docker compose run --rm -e PARALLEL_AGENTS=2 debate-system python src/main_with_memory.py "How should we understand the mind-body problem?"

echo ""
echo "Memory test complete. Check the memory directory for stored debates and agent memories."
