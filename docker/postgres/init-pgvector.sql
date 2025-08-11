-- Create user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'mnemosyne') THEN
        CREATE USER mnemosyne WITH PASSWORD 'mnemosyne_pass';
    END IF;
END
$$;

-- Initialize pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create collective database if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mnemosyne_collective') THEN
        CREATE DATABASE mnemosyne_collective;
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mnemosyne TO mnemosyne;
GRANT ALL PRIVILEGES ON DATABASE mnemosyne_collective TO mnemosyne;

-- Switch to mnemosyne_collective and add pgvector
\c mnemosyne_collective;
CREATE EXTENSION IF NOT EXISTS vector;