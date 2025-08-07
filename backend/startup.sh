#!/bin/bash
# Backend startup script
# This script runs database initialization and starts the FastAPI application

set -e

# Ensure we're in the right directory and have the right Python path
cd /app
export PYTHONPATH=/app:$PYTHONPATH

# Activate virtual environment if it exists
if [ -f "/app/.venv/bin/activate" ]; then
    source /app/.venv/bin/activate
fi

echo "Running database initialization..."
python -m scripts.init_db || echo "Database initialization failed or already done"

echo "Starting FastAPI application..."

# Check if we're in development mode
if [ "$APP_ENV" = "development" ]; then
    echo "Running in DEVELOPMENT mode with hot reload enabled"
    # Convert log level to lowercase to avoid uvicorn errors
    LOG_LEVEL=$(echo "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')
    echo "Using log level: $LOG_LEVEL"
    # Use watchfiles for better file watching performance
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app --log-level "$LOG_LEVEL"
else
    echo "Running in PRODUCTION mode"
    LOG_LEVEL=$(echo "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level "$LOG_LEVEL"
fi
