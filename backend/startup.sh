#!/bin/bash
# Backend startup script
# This script runs database initialization and starts the FastAPI application

set -e

echo "Running database initialization..."
python -m app.db.init_db

echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
