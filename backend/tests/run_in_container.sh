#!/bin/bash
# Script to run the Phase 2.5 tests inside the Docker container
# This ensures consistent environment for testing

echo "========================================"
echo "RUNNING TESTS INSIDE DOCKER CONTAINER"
echo "========================================"

# Run the memory tests inside the container
echo
echo "MEMORY API TESTS:"
docker compose exec backend python /app/tests/quick_memory_test.py

# Run the LLM integration tests inside the container
echo
echo "LLM INTEGRATION TESTS:"
docker compose exec backend python /app/tests/quick_llm_test.py

echo
echo "========================================"
echo "TEST COMPLETE"
echo "========================================"
