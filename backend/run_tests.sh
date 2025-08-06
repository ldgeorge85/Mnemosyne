#!/bin/bash
# Test runner script for Mnemosyne backend
# This script provides a convenient way to run different types of tests inside Docker

set -e

# Default values
TEST_TYPE="all"
COVERAGE=false
VERBOSE=false
TEST_PATH="app/tests"
IN_DOCKER=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -t|--type)
      TEST_TYPE="$2"
      shift
      shift
      ;;
    -c|--coverage)
      COVERAGE=true
      shift
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -p|--path)
      TEST_PATH="$2"
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
      echo "  -t, --type TYPE     Test type: all, unit, integration, e2e (default: all)"
      echo "  -c, --coverage      Generate coverage report"
      echo "  -v, --verbose       Verbose output"
      echo "  -p, --path PATH     Specific test path to run"
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

# Set test directory based on test type
if [ "$TEST_PATH" == "app/tests" ]; then
  case $TEST_TYPE in
    unit)
      TEST_PATH="app/tests/unit"
      ;;
    integration)
      TEST_PATH="app/tests/integration"
      ;;
    e2e)
      TEST_PATH="app/tests/e2e"
      ;;
    all)
      TEST_PATH="app/tests"
      ;;
    *)
      echo "Invalid test type: $TEST_TYPE"
      exit 1
      ;;
  esac
fi

# Build the pytest command
PYTEST_CMD="python -m pytest $TEST_PATH"

# Add verbose flag if requested
if [ "$VERBOSE" = true ]; then
  PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
  # Check if pytest-cov is installed
  if [ "$IN_DOCKER" = true ]; then
    docker compose exec backend pip show pytest-cov >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=term --cov-report=html"
    else
      echo "Warning: pytest-cov is not installed in the Docker container. Skipping coverage."
      echo "To install it, run: docker compose exec backend pip install pytest-cov"
    fi
  else
    pip show pytest-cov >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=term --cov-report=html"
    else
      echo "Warning: pytest-cov is not installed. Skipping coverage."
      echo "To install it, run: pip install pytest-cov"
    fi
  fi
fi

# Determine whether to run in Docker or locally
if [ "$IN_DOCKER" = true ]; then
  # Check if backend container is running
  if ! docker compose ps | grep -q "mnemosyne-backend.*Up"; then
    echo "Backend container is not running. Please start it with 'docker compose up -d backend'"
    exit 1
  fi
  
  # Create test database if it doesn't exist
  echo "Ensuring test database exists..."
  docker compose exec postgres psql -U postgres -c "CREATE DATABASE mnemosyne_test;" || true
  
  # Run the tests in the Docker container
  CMD="docker compose exec backend $PYTEST_CMD"
  echo "Running tests in Docker container: $PYTEST_CMD"
else
  # Run the tests locally
  CMD="$PYTEST_CMD"
  echo "Running tests locally: $PYTEST_CMD"
fi

# Run the tests
eval $CMD

# If coverage was generated, show the report location
if [ "$COVERAGE" = true ]; then
  if [ "$IN_DOCKER" = true ]; then
    echo "Coverage report generated in Docker container: htmlcov/index.html"
    echo "To view it, you can copy it from the container with:"
    echo "docker compose cp backend:/app/htmlcov ./htmlcov"
  else
    echo "Coverage report generated in htmlcov/index.html"
  fi
fi
