"""
Conversation Summarization Service

This module provides conversation summarization capabilities to help
manage context and create concise representations of long conversations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.conversation import Conversation, Message
from app.services.llm.llm_service_enhanced import EnhancedLLMService, EnhancedLLMConfig

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """
    Service for summarizing conversations to manage context and extract key points.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the summarizer.
        
        Args:
            db: Database session
        """
        self.db = db
        self.llm_config = EnhancedLLMConfig(
            temperature=0.3,  # Lower temperature for more focused summaries
            memory_enabled=False  # Don't use memory for summarization
        )
    
    async def summarize_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        max_messages: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary of a conversation.
        
        Args:
            conversation_id: ID of the conversation to summarize
            user_id: User ID for verification
            max_messages: Maximum number of recent messages to include
            
        Returns:
            Summary with key points and metadata
        """
        # Get conversation
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Get messages
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc())
        
        if max_messages:
            query = query.limit(max_messages)
            
        messages_result = await self.db.execute(query)
        messages = list(reversed(messages_result.scalars().all()))
        
        if not messages:
            return {
                "conversation_id": str(conversation_id),
                "summary": "No messages to summarize",
                "key_points": [],
                "message_count": 0
            }
        
        # Generate summary using LLM
        llm_service = EnhancedLLMService(config=self.llm_config, db=self.db)
        
        # Prepare messages for summarization
        conversation_text = self._format_messages_for_summary(messages)
        
        summary_prompt = [
            {
                "role": "system",
                "content": (
                    "You are a conversation summarizer. Create a concise summary "
                    "that captures the key points, decisions, and important information "
                    "from the conversation. Format your response as:\n\n"
                    "SUMMARY: A brief paragraph summarizing the conversation\n\n"
                    "KEY POINTS:\n"
                    "- First key point\n"
                    "- Second key point\n"
                    "- Additional key points as needed\n\n"
                    "TOPICS: Comma-separated list of main topics discussed"
                )
            },
            {
                "role": "user",
                "content": f"Please summarize this conversation:\n\n{conversation_text}"
            }
        ]
        
        # Generate summary
        summary_response = await llm_service.chat_completion(
            messages=summary_prompt,
            max_tokens=500
        )
        
        # Parse the response
        parsed_summary = self._parse_summary_response(summary_response)
        
        # Store summary metadata on conversation
        if not conversation.metadata:
            conversation.metadata = {}
            
        conversation.metadata["last_summary"] = {
            "created_at": datetime.utcnow().isoformat(),
            "message_count": len(messages),
            "summary": parsed_summary["summary"],
            "topics": parsed_summary["topics"]
        }
        
        await self.db.commit()
        
        return {
            "conversation_id": str(conversation_id),
            "summary": parsed_summary["summary"],
            "key_points": parsed_summary["key_points"],
            "topics": parsed_summary["topics"],
            "message_count": len(messages),
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_conversation_context(
        self,
        conversation_id: UUID,
        user_id: UUID,
        include_summary: bool = True,
        max_recent_messages: int = 10
    ) -> Dict[str, Any]:
        """
        Get conversation context including summary and recent messages.
        
        Args:
            conversation_id: ID of the conversation
            user_id: User ID for verification
            include_summary: Whether to include or generate summary
            max_recent_messages: Number of recent messages to include
            
        Returns:
            Context dictionary with summary and messages
        """
        # Get conversation
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        context = {
            "conversation_id": str(conversation_id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat()
        }
        
        # Get summary if requested
        if include_summary:
            # Check if we have a recent summary
            if (conversation.metadata and 
                "last_summary" in conversation.metadata and
                conversation.metadata["last_summary"].get("message_count", 0) > 5):
                context["summary"] = conversation.metadata["last_summary"]["summary"]
                context["summary_message_count"] = conversation.metadata["last_summary"]["message_count"]
            else:
                # Generate new summary
                summary_result = await self.summarize_conversation(
                    conversation_id, user_id
                )
                context["summary"] = summary_result["summary"]
                context["summary_message_count"] = summary_result["message_count"]
        
        # Get recent messages
        messages_result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_recent_messages)
        )
        
        recent_messages = []
        for msg in reversed(messages_result.scalars().all()):
            recent_messages.append({
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            })
        
        context["recent_messages"] = recent_messages
        context["recent_message_count"] = len(recent_messages)
        
        return context
    
    def _format_messages_for_summary(self, messages: List[Message]) -> str:
        """Format messages for summarization."""
        formatted = []
        
        for msg in messages:
            timestamp = msg.created_at.strftime("%H:%M")
            role = msg.role.capitalize()
            content = msg.content.strip()
            
            formatted.append(f"[{timestamp}] {role}: {content}")
        
        return "\n\n".join(formatted)
    
    def _parse_summary_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM's summary response."""
        lines = response.strip().split("\n")
        
        summary = ""
        key_points = []
        topics = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("SUMMARY:"):
                current_section = "summary"
                summary = line[8:].strip()
            elif line.startswith("KEY POINTS:"):
                current_section = "key_points"
            elif line.startswith("TOPICS:"):
                current_section = "topics"
                topics_str = line[7:].strip()
                topics = [t.strip() for t in topics_str.split(",") if t.strip()]
            elif line.startswith("- ") and current_section == "key_points":
                key_points.append(line[2:].strip())
            elif current_section == "summary" and line:
                summary += " " + line
            elif current_section == "topics" and line:
                # Additional topics on new line
                more_topics = [t.strip() for t in line.split(",") if t.strip()]
                topics.extend(more_topics)
        
        return {
            "summary": summary.strip(),
            "key_points": key_points,
            "topics": topics
        }