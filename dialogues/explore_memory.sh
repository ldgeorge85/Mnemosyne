#!/bin/bash
# Script to run the memory explorer CLI tool in the Docker container

echo "Starting Philosophical Debate Memory Explorer..."
docker compose run --rm debate-system python -m src.cli.memory_explorer "$@"
