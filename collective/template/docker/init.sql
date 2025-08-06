-- Initialize Chatter database schema

-- Create tables for structured data
CREATE TABLE IF NOT EXISTS ingestion_logs (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'started',
    items_processed INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_ingestion_source ON ingestion_logs(source_name);
CREATE INDEX idx_ingestion_status ON ingestion_logs(status);

-- Future: Task extraction table
CREATE TABLE IF NOT EXISTS extracted_tasks (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(255),
    source_type VARCHAR(100),
    task_description TEXT NOT NULL,
    priority VARCHAR(20),
    due_date DATE,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Future: Entity tracking
CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    entity_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    occurrences INTEGER DEFAULT 1,
    contexts JSONB
);

CREATE INDEX idx_entity_name ON entities(entity_name);
CREATE INDEX idx_entity_type ON entities(entity_type);