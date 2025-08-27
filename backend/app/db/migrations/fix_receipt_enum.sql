-- Manual migration to update receipt type enum with aliases
-- Run this to add the missing enum values to the database

-- Add new values to the enum type if they don't exist
ALTER TYPE receipttype ADD VALUE IF NOT EXISTS 'memory_created';
ALTER TYPE receipttype ADD VALUE IF NOT EXISTS 'memory_updated';
ALTER TYPE receipttype ADD VALUE IF NOT EXISTS 'memory_deleted';
ALTER TYPE receipttype ADD VALUE IF NOT EXISTS 'task_created';
ALTER TYPE receipttype ADD VALUE IF NOT EXISTS 'task_updated';
ALTER TYPE receipttype ADD VALUE IF NOT EXISTS 'task_completed';
ALTER TYPE receipttype ADD VALUE IF NOT EXISTS 'task_deleted';