#!/bin/bash
# Script to migrate memory data to the new format
# Adds proper topic, date, and agent information to existing memory files

echo "Migrating memory data to new format..."
docker compose run --rm debate-system python -m src.utils.migrate_memory /app/memory

# Verify the results with memory explorer
echo -e "\nRunning memory explorer to verify migration..."
./explore_memory.sh
