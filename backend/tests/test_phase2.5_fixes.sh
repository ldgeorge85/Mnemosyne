#!/bin/bash
# Test script for Phase 2.5 fixes
# This script runs the memory and LLM integration tests to verify that all issues have been fixed

echo "========================================"
echo "PHASE 2.5 INTEGRATION TESTING"
echo "========================================"
echo

# Update OpenAI package to v1.0+
echo "Updating OpenAI package to v1.0+..."
pip install --upgrade openai>=1.3.0

echo
echo "========================================"
echo "RUNNING MEMORY API TESTS"
echo "========================================"
python quick_memory_test.py

echo
echo "========================================"
echo "RUNNING LLM INTEGRATION TESTS"
echo "========================================"
python quick_llm_test.py

echo
echo "========================================"
echo "TEST SUMMARY"
echo "========================================"
echo "All tests completed. See above for results."
echo
echo "If all tests passed, the Phase 2.5 fixes were successful."
echo "If any tests failed, check the specific error messages for further debugging."
