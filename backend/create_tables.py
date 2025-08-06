#!/usr/bin/env python
"""
Create Database Tables Script

This script directly creates specific tables defined in SQLAlchemy models.
For development and testing purposes only.
"""

import asyncio
import logging
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateTable, Table

from app.core.config import settings
from app.db.session import Base
from app.db.base import *  # Import all models
from app.db.models.conversation import Conversation, Message

# Import the Base instance and all models
# This ensures all models are registered with the metadata

async def create_tables():
    """Create specific tables if they don't exist."""
    
    # Create async engine
    # Convert standard URI to async URI
    db_uri = settings.DATABASE_URI
    async_uri = db_uri.replace('postgresql://', 'postgresql+asyncpg://')
    
    engine = create_async_engine(
        async_uri,
        echo=True,
    )
    
    # Define PostgreSQL-specific SQL statements for creating our tables
    create_conversations_table = """
    CREATE TABLE IF NOT EXISTS conversations (
        id VARCHAR(36) PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        user_id VARCHAR(36) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    )
    """
    
    create_conversation_index = """
    CREATE INDEX IF NOT EXISTS ix_conversation_user_id ON conversations (user_id)
    """
    
    create_messages_table = """
    CREATE TABLE IF NOT EXISTS messages (
        id VARCHAR(36) PRIMARY KEY,
        conversation_id VARCHAR(36) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
        content TEXT NOT NULL,
        role VARCHAR(10) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    )
    """
    
    create_message_conversation_index = """
    CREATE INDEX IF NOT EXISTS ix_message_conversation_id ON messages (conversation_id)
    """
    
    create_message_role_index = """
    CREATE INDEX IF NOT EXISTS ix_message_role ON messages (role)
    """
    
    # Check if tables exist and create missing ones
    async with engine.begin() as conn:
        # Get list of existing tables
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        existing_tables = [row[0] for row in result.fetchall()]
        
        print(f"Existing tables: {existing_tables}")
        
        # Create conversations table and indexes if it doesn't exist
        if 'conversations' not in existing_tables:
            print(f"Creating missing table: conversations")
            try:
                await conn.execute(text(create_conversations_table))
                print("Created table: conversations")
                
                # Create index after table
                try:
                    await conn.execute(text(create_conversation_index))
                    print("Created index: ix_conversation_user_id")
                except Exception as e:
                    print(f"Error creating index ix_conversation_user_id: {e}")
            except Exception as e:
                print(f"Error creating table conversations: {e}")
        
        # Create messages table and indexes if it doesn't exist
        if 'messages' not in existing_tables:
            print(f"Creating missing table: messages")
            try:
                await conn.execute(text(create_messages_table))
                print("Created table: messages")
                
                # Create indexes after table
                try:
                    await conn.execute(text(create_message_conversation_index))
                    print("Created index: ix_message_conversation_id")
                except Exception as e:
                    print(f"Error creating index ix_message_conversation_id: {e}")
                    
                try:
                    await conn.execute(text(create_message_role_index))
                    print("Created index: ix_message_role")
                except Exception as e:
                    print(f"Error creating index ix_message_role: {e}")
            except Exception as e:
                print(f"Error creating table messages: {e}")
        
        print("Finished processing tables")

if __name__ == "__main__":
    asyncio.run(create_tables())
