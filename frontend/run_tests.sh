#!/bin/bash
# Test runner script for Mnemosyne frontend
# This script provides a convenient way to run different types of tests with Vitest inside Docker

set -e

# Default values
TEST_MODE="run"
COVERAGE=false
UI=false
COMPONENT_PATH=""
IN_DOCKER=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -m|--mode)
      TEST_MODE="$2"
      shift
      shift
      ;;
    -c|--coverage)
      COVERAGE=true
      shift
      ;;
    -u|--ui)
      UI=true
      shift
      ;;
    -p|--path)
      COMPONENT_PATH="$2"
      shift
      shift
      ;;
    -l|--local)
      IN_DOCKER=false
      shift
      ;;
    -h|--help)
      echo "Usage: ./run_tests.sh [options]"
      echo "Options:"
      echo "  -m, --mode MODE     Test mode: run, watch (default: run)"
      echo "  -c, --coverage      Generate coverage report"
      echo "  -u, --ui            Run tests with UI"
      echo "  -p, --path PATH     Specific test path or component to test"
      echo "  -l, --local         Run tests locally (not in Docker, default is to run in Docker)"
      echo "  -h, --help          Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Build the npm command
if [ "$UI" = true ]; then
  NPM_CMD="npm run test:ui"
elif [ "$TEST_MODE" = "watch" ]; then
  NPM_CMD="npm run test:watch"
elif [ "$COVERAGE" = true ]; then
  NPM_CMD="npm run test:coverage"
else
  NPM_CMD="npm run test"
fi

# Add component path if specified
if [ -n "$COMPONENT_PATH" ]; then
  NPM_CMD="$NPM_CMD -- $COMPONENT_PATH"
fi

# Determine whether to run in Docker or locally
if [ "$IN_DOCKER" = true ]; then
  # Check if frontend container is running
  if ! docker compose ps | grep -q "mnemosyne-frontend.*Up"; then
    echo "Frontend container is not running. Please start it with 'docker compose up -d frontend'"
    exit 1
  fi
  
  # Run the tests in the Docker container
  CMD="docker compose exec frontend $NPM_CMD"
  echo "Running tests in Docker container: $NPM_CMD"
else
  # Run the tests locally
  CMD="$NPM_CMD"
  echo "Running tests locally: $NPM_CMD"
fi

# Run the tests
eval $CMD

# If coverage was generated, show the report location
if [ "$COVERAGE" = true ]; then
  if [ "$IN_DOCKER" = true ]; then
    echo "Coverage report generated in Docker container: coverage/index.html"
    echo "To view it, you can copy it from the container with:"
    echo "docker compose cp frontend:/app/coverage ./coverage"
  else
    echo "Coverage report generated in coverage/index.html"
  fi
fi
