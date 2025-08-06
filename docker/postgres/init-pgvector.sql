-- Initialize pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create collective database
CREATE DATABASE mnemosyne_collective;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mnemosyne TO mnemosyne;
GRANT ALL PRIVILEGES ON DATABASE mnemosyne_collective TO mnemosyne;

-- Switch to mnemosyne_collective and add pgvector
\c mnemosyne_collective;
CREATE EXTENSION IF NOT EXISTS vector;