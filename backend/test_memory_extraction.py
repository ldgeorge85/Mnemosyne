#!/usr/bin/env python3
"""
Test script for memory extraction functionality.

This script tests the memory extraction service with sample conversations.
"""

import asyncio
import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models.user import User
from app.db.models.conversation import Conversation, Message
from app.services.memory.memory_service_enhanced import MemoryService


async def create_test_conversation(session: AsyncSession, user_id: str):
    """Create a test conversation with rich content for extraction."""
    # Create conversation
    conversation = Conversation(
        id=uuid4(),
        user_id=user_id,
        title="Health and Work Discussion",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    
    # Create messages with rich extractable content
    messages = [
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="I've been having headaches lately, especially after long days at the office. I work as a software engineer at TechCorp in San Francisco.",
            created_at=datetime.utcnow()
        ),
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content="I'm sorry to hear about your headaches. Working long hours in front of a computer can definitely contribute to tension headaches. Have you considered taking regular breaks?",
            created_at=datetime.utcnow()
        ),
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="Yes, I should do that more often. I usually work from 9 AM to 7 PM. My doctor prescribed me ibuprofen for the headaches. I also love hiking on weekends to relax - it really helps. My wife Sarah and I often go to Mount Tamalpais.",
            created_at=datetime.utcnow()
        ),
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content="Those are long work days! It's great that you mentioned hiking helps you relax. Mount Tamalpais is beautiful. Regular outdoor activities like hiking can be excellent for managing stress and preventing tension headaches.",
            created_at=datetime.utcnow()
        ),
        Message(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content="Absolutely! I need to schedule my annual review with my manager next week. Also, I'm planning to take a vacation in Hawaii next month. I can't eat seafood though - I'm allergic to shellfish.",
            created_at=datetime.utcnow()
        )
    ]
    
    for msg in messages:
        session.add(msg)
    
    await session.commit()
    return conversation.id


async def test_memory_extraction():
    """Test the memory extraction service."""
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URI,
        echo=True,  # Enable SQL logging
        future=True
    )
    
    # Create async session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        # Create or get a test user
        test_user_id = str(uuid4())
        
        # Create test conversation
        print("\n🔵 Creating test conversation...")
        conversation_id = await create_test_conversation(session, test_user_id)
        print(f"✅ Created conversation: {conversation_id}")
        
        # Initialize memory service
        memory_service = MemoryService(session)
        
        # Process conversation
        print("\n🔵 Extracting memories from conversation...")
        result = await memory_service.process_conversation(
            conversation_id=conversation_id,
            user_id=test_user_id
        )
        
        print("\n✅ Memory extraction complete!")
        print(json.dumps(result, indent=2))
        
        # Test memory search
        print("\n🔵 Testing memory search...")
        queries = [
            "headaches",
            "work",
            "hiking",
            "allergic",
            "vacation"
        ]
        
        for query in queries:
            print(f"\n🔍 Searching for: '{query}'")
            search_results = await memory_service.search_memories(
                user_id=test_user_id,
                query=query,
                limit=5,
                threshold=0.6
            )
            
            for idx, memory in enumerate(search_results, 1):
                print(f"  {idx}. {memory['title']} (similarity: {memory['similarity']:.3f})")
                print(f"     Content: {memory['content'][:100]}...")
                print(f"     Importance: {memory['importance']:.2f}")
        
        # Get statistics
        print("\n🔵 Getting memory statistics...")
        stats = await memory_service.get_memory_statistics(test_user_id)
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    print("🧠 Mnemosyne Memory Extraction Test")
    print("=" * 50)
    asyncio.run(test_memory_extraction())