-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS mnemosyne;

-- Set search path
SET search_path TO mnemosyne, public;

-- Function to create an HNSW index if it doesn't exist
CREATE OR REPLACE FUNCTION create_hnsw_index(table_name text, column_name text, index_name text)
RETURNS void AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE indexname = index_name
    ) THEN
        EXECUTE format(
            'CREATE INDEX %I ON %I USING hnsw (%I vector_cosine_ops) WITH (m=16, ef_construction=64)',
            index_name,
            table_name,
            column_name
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Note: The actual tables and indexes will be created by the application's migration system (Alembic)
-- This script only ensures the extension is available and provides helper functions
