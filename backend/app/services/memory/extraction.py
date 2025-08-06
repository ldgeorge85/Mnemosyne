"""
Memory Extraction Service

This module implements aggressive memory extraction from conversations,
extracting entities, facts, preferences, and action items to build
a comprehensive understanding of the user.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """
    Extracts memories from conversations with aggressive depth.
    
    This service is designed to "KNOW you" - extracting all personal details,
    preferences, opinions, habits, patterns, goals, and plans. Privacy is
    handled by self-hosting, not by limiting extraction.
    """
    
    def __init__(self):
        """Initialize the memory extractor with NLP models."""
        self.spacy_model = None
        self._load_models()
    
    def _load_models(self):
        """Load NLP models for entity extraction."""
        try:
            import spacy
            # Try to load the model, download if not available
            try:
                self.spacy_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, falling back to regex extraction")
                # We'll use regex patterns as fallback
        except ImportError:
            logger.warning("spaCy not available, using regex extraction only")
    
    async def extract_memories(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all types of memories from a conversation.
        
        Args:
            conversation: Conversation data including messages
            
        Returns:
            Dictionary containing extracted entities, facts, preferences, and action items
        """
        # Combine all messages into text for analysis
        messages = conversation.get("messages", [])
        user_messages = [m for m in messages if m.get("role") == "user"]
        assistant_messages = [m for m in messages if m.get("role") == "assistant"]
        
        # Extract from user messages (what they tell us)
        user_text = " ".join([m.get("content", "") for m in user_messages])
        
        # Extract from assistant messages (what we discussed)
        assistant_text = " ".join([m.get("content", "") for m in assistant_messages])
        
        # Full conversation text
        full_text = " ".join([m.get("content", "") for m in messages])
        
        # Extract different types of information
        entities = await self.extract_entities(full_text)
        facts = await self.extract_facts(user_text, assistant_text)
        preferences = await self.extract_preferences(user_text)
        action_items = await self.extract_action_items(full_text)
        
        # Extract personal information with high detail
        personal_info = await self.extract_personal_information(user_text)
        
        # Extract relationships and social connections
        relationships = await self.extract_relationships(full_text)
        
        # Extract goals and aspirations
        goals = await self.extract_goals(user_text)
        
        # Extract habits and patterns
        habits = await self.extract_habits(user_text)
        
        return {
            "entities": entities,
            "facts": facts,
            "preferences": preferences,
            "action_items": action_items,
            "personal_info": personal_info,
            "relationships": relationships,
            "goals": goals,
            "habits": habits,
            "extraction_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "message_count": len(messages),
                "user_message_count": len(user_messages),
                "extraction_version": "1.0"
            }
        }
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            List of entities with type and confidence scores
        """
        entities = []
        
        if self.spacy_model:
            # Use spaCy for entity extraction
            doc = self.spacy_model(text)
            for ent in doc.ents:
                entity_type = self._map_spacy_entity_type(ent.label_)
                if entity_type:
                    entities.append({
                        "text": ent.text,
                        "type": entity_type,
                        "spacy_label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.85  # spaCy doesn't provide confidence scores
                    })
        
        # Always run regex patterns for additional extraction
        regex_entities = self._extract_entities_regex(text)
        
        # Merge and deduplicate
        seen = set()
        merged_entities = []
        for entity in entities + regex_entities:
            key = (entity["text"].lower(), entity["type"])
            if key not in seen:
                seen.add(key)
                merged_entities.append(entity)
        
        return merged_entities
    
    def _map_spacy_entity_type(self, label: str) -> Optional[str]:
        """Map spaCy entity labels to our types."""
        mapping = {
            "PERSON": "person",
            "ORG": "organization",
            "GPE": "location",  # Geopolitical entities
            "LOC": "location",
            "DATE": "date",
            "TIME": "time",
            "MONEY": "money",
            "PRODUCT": "product",
            "EVENT": "event",
            "FAC": "facility",
            "LANGUAGE": "language"
        }
        return mapping.get(label)
    
    def _extract_entities_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using regex patterns."""
        entities = []
        
        # Date patterns
        date_patterns = [
            (r'\b(tomorrow|today|yesterday)\b', 'relative_date'),
            (r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', 'weekday'),
            (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b', 'date'),
            (r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', 'date'),
            (r'\b\d{4}-\d{2}-\d{2}\b', 'date')
        ]
        
        for pattern, entity_type in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({
                    "text": match.group(),
                    "type": entity_type,
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.9
                })
        
        # Time patterns
        time_pattern = r'\b\d{1,2}:\d{2}\s*(am|pm|AM|PM)?\b'
        for match in re.finditer(time_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "time",
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.95
            })
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "email",
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.98
            })
        
        # Phone patterns
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
        for match in re.finditer(phone_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "phone",
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.85
            })
        
        # Money patterns
        money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?|\b\d+\s*(?:dollars|cents|bucks|USD)\b'
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            entities.append({
                "text": match.group(),
                "type": "money",
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.9
            })
        
        return entities
    
    async def extract_facts(self, user_text: str, assistant_text: str) -> List[Dict[str, Any]]:
        """
        Extract factual statements from the conversation.
        
        Args:
            user_text: Text from user messages
            assistant_text: Text from assistant messages
            
        Returns:
            List of extracted facts with confidence scores
        """
        facts = []
        
        # Patterns for factual statements
        fact_patterns = [
            # "I am/have/do" statements
            (r"I\s+(?:am|'m)\s+([^.!?]+)", "personal_attribute"),
            (r"I\s+have\s+([^.!?]+)", "possession"),
            (r"I\s+(?:work|worked)\s+(?:at|for|in)\s+([^.!?]+)", "employment"),
            (r"I\s+live\s+(?:in|at)\s+([^.!?]+)", "residence"),
            (r"I\s+(?:study|studied)\s+([^.!?]+)", "education"),
            (r"My\s+(\w+)\s+is\s+([^.!?]+)", "personal_detail"),
            
            # Health-related
            (r"I\s+(?:have|had|suffer from|diagnosed with)\s+([^.!?]+)", "health"),
            (r"I\s+take\s+([^.!?]+)\s+(?:for|medication)", "medication"),
            
            # Family/relationships
            (r"My\s+(?:wife|husband|partner|spouse)\s+([^.!?]+)", "relationship"),
            (r"My\s+(?:son|daughter|child|kid)\s+([^.!?]+)", "family"),
            (r"My\s+(?:mother|father|mom|dad|parent)\s+([^.!?]+)", "family"),
            
            # Preferences stated as facts
            (r"I\s+(?:always|never|usually|often)\s+([^.!?]+)", "habit"),
            (r"I\s+(?:love|hate|like|dislike)\s+([^.!?]+)", "preference"),
        ]
        
        for pattern, fact_type in fact_patterns:
            for match in re.finditer(pattern, user_text, re.IGNORECASE):
                facts.append({
                    "statement": match.group(),
                    "extracted_info": match.group(1).strip(),
                    "type": fact_type,
                    "source": "user",
                    "confidence": 0.9
                })
        
        # Extract facts from things we learned in conversation
        if "you mentioned" in assistant_text or "you said" in assistant_text:
            mentioned_pattern = r"you\s+(?:mentioned|said|told me)\s+(?:that\s+)?([^.!?]+)"
            for match in re.finditer(mentioned_pattern, assistant_text, re.IGNORECASE):
                facts.append({
                    "statement": match.group(1).strip(),
                    "type": "confirmed_fact",
                    "source": "assistant_confirmation",
                    "confidence": 0.85
                })
        
        return facts
    
    async def extract_preferences(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract user preferences and opinions.
        
        Args:
            text: Text to extract preferences from
            
        Returns:
            List of preferences with sentiment and confidence
        """
        preferences = []
        
        # Preference patterns
        preference_patterns = [
            # Positive preferences
            (r"I\s+(?:love|enjoy|like|prefer|favor)\s+([^.!?]+)", "positive"),
            (r"I\s+(?:am|'m)\s+(?:a\s+)?(?:big\s+)?fan\s+of\s+([^.!?]+)", "positive"),
            (r"([^.!?]+)\s+is\s+(?:my\s+)?favorite", "positive"),
            (r"I\s+(?:always|usually)\s+(?:choose|pick|go with)\s+([^.!?]+)", "positive"),
            
            # Negative preferences
            (r"I\s+(?:hate|dislike|can't stand|avoid)\s+([^.!?]+)", "negative"),
            (r"I\s+(?:don't|do not)\s+like\s+([^.!?]+)", "negative"),
            (r"I\s+(?:never|rarely)\s+([^.!?]+)", "negative"),
            
            # Neutral/conditional preferences
            (r"I\s+(?:sometimes|occasionally)\s+([^.!?]+)", "neutral"),
            (r"I\s+(?:might|may|could)\s+([^.!?]+)", "conditional"),
            
            # Dietary preferences
            (r"I\s+(?:am|'m)\s+(?:a\s+)?(?:vegetarian|vegan|pescatarian|gluten-free)", "dietary"),
            (r"I\s+(?:don't|do not|can't)\s+eat\s+([^.!?]+)", "dietary_restriction"),
        ]
        
        for pattern, sentiment in preference_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                preferences.append({
                    "statement": match.group(),
                    "subject": match.group(1).strip() if len(match.groups()) > 0 else match.group(),
                    "sentiment": sentiment,
                    "confidence": 0.85
                })
        
        return preferences
    
    async def extract_action_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract action items and tasks from the conversation.
        
        Args:
            text: Full conversation text
            
        Returns:
            List of action items with deadlines if mentioned
        """
        action_items = []
        
        # Action item patterns
        action_patterns = [
            # Future intentions
            (r"I\s+(?:will|'ll|am going to|plan to|need to|have to|must|should)\s+([^.!?]+)", "todo"),
            (r"I\s+(?:want|would like)\s+to\s+([^.!?]+)", "goal"),
            (r"(?:Don't|Do not)\s+forget\s+to\s+([^.!?]+)", "reminder"),
            (r"(?:Remember|Remind me)\s+to\s+([^.!?]+)", "reminder"),
            
            # Scheduled items
            (r"I\s+have\s+(?:a|an)\s+([^.!?]+)\s+(?:tomorrow|today|next week|on \w+)", "scheduled"),
            (r"(?:Meeting|Appointment|Call)\s+(?:with|at)\s+([^.!?]+)", "meeting"),
            
            # Deadlines
            (r"([^.!?]+)\s+(?:by|before|until)\s+([^.!?]+)", "deadline"),
            (r"([^.!?]+)\s+is\s+due\s+([^.!?]+)", "deadline"),
        ]
        
        for pattern, item_type in action_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                action_item = {
                    "statement": match.group(),
                    "action": match.group(1).strip(),
                    "type": item_type,
                    "confidence": 0.8
                }
                
                # Try to extract deadline from the same statement
                if item_type == "deadline" and len(match.groups()) > 1:
                    action_item["deadline"] = match.group(2).strip()
                
                action_items.append(action_item)
        
        return action_items
    
    async def extract_personal_information(self, text: str) -> Dict[str, Any]:
        """
        Extract personal information with aggressive depth.
        
        Args:
            text: User text to analyze
            
        Returns:
            Dictionary of personal information categories
        """
        personal_info = {
            "health": [],
            "finance": [],
            "occupation": [],
            "education": [],
            "location": [],
            "demographics": []
        }
        
        # Health information
        health_patterns = [
            r"I\s+(?:have|had|was diagnosed with|suffer from)\s+([^.!?]+)",
            r"I\s+take\s+([^.!?]+)\s+(?:for|medication|medicine)",
            r"I\s+(?:am|'m)\s+allergic\s+to\s+([^.!?]+)",
            r"My\s+(?:doctor|physician|therapist)\s+([^.!?]+)",
            r"I\s+(?:feel|felt|am feeling)\s+([^.!?]+)",
        ]
        
        for pattern in health_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                personal_info["health"].append({
                    "text": match.group(),
                    "detail": match.group(1).strip(),
                    "confidence": 0.85
                })
        
        # Financial information
        finance_patterns = [
            r"I\s+(?:earn|make|salary|income)\s+([^.!?]+)",
            r"I\s+(?:spend|spent|paid)\s+([^.!?]+)",
            r"I\s+(?:save|saved|invest|invested)\s+([^.!?]+)",
            r"My\s+(?:budget|expenses|bills)\s+([^.!?]+)",
            r"I\s+(?:owe|debt|loan)\s+([^.!?]+)",
        ]
        
        for pattern in finance_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                personal_info["finance"].append({
                    "text": match.group(),
                    "detail": match.group(1).strip(),
                    "confidence": 0.8
                })
        
        # Occupation information
        occupation_patterns = [
            r"I\s+(?:work|worked)\s+(?:as|at|for|in)\s+([^.!?]+)",
            r"I\s+(?:am|'m)\s+a\s+([^.!?]+)",
            r"My\s+(?:job|position|role|title)\s+is\s+([^.!?]+)",
            r"I\s+(?:manage|lead|run)\s+([^.!?]+)",
        ]
        
        for pattern in occupation_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                personal_info["occupation"].append({
                    "text": match.group(),
                    "detail": match.group(1).strip(),
                    "confidence": 0.9
                })
        
        return personal_info
    
    async def extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract information about relationships and social connections.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of relationship information
        """
        relationships = []
        
        relationship_patterns = [
            (r"My\s+(\w+)\s+(?:is|are)\s+([^.!?]+)", "family"),
            (r"I\s+(?:have|had)\s+(?:a|an)?\s*(\w+)\s+(?:named|called)\s+(\w+)", "named_relation"),
            (r"(\w+)\s+is\s+my\s+(\w+)", "relation_definition"),
            (r"I\s+(?:met|know|knew)\s+(\w+)\s+(?:from|at|through)\s+([^.!?]+)", "acquaintance"),
            (r"My\s+(?:friend|colleague|neighbor)\s+(\w+)", "social"),
        ]
        
        for pattern, rel_type in relationship_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                relationships.append({
                    "text": match.group(),
                    "type": rel_type,
                    "details": [match.group(i).strip() for i in range(1, len(match.groups()) + 1)],
                    "confidence": 0.85
                })
        
        return relationships
    
    async def extract_goals(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract goals, aspirations, and future plans.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of goals and aspirations
        """
        goals = []
        
        goal_patterns = [
            (r"I\s+(?:want|would like|hope|plan)\s+to\s+([^.!?]+)", "aspiration"),
            (r"My\s+(?:goal|dream|ambition)\s+is\s+to\s+([^.!?]+)", "goal"),
            (r"I\s+(?:am|'m)\s+(?:working|trying)\s+to\s+([^.!?]+)", "active_goal"),
            (r"I\s+(?:will|'ll)\s+([^.!?]+)\s+(?:someday|eventually|in the future)", "future_plan"),
            (r"I\s+(?:need|have)\s+to\s+([^.!?]+)\s+by\s+([^.!?]+)", "deadline_goal"),
        ]
        
        for pattern, goal_type in goal_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                goal = {
                    "text": match.group(),
                    "type": goal_type,
                    "goal": match.group(1).strip(),
                    "confidence": 0.8
                }
                
                # Extract deadline if present
                if goal_type == "deadline_goal" and len(match.groups()) > 1:
                    goal["deadline"] = match.group(2).strip()
                
                goals.append(goal)
        
        return goals
    
    async def extract_habits(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract habits, routines, and behavioral patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of habits and patterns
        """
        habits = []
        
        habit_patterns = [
            (r"I\s+(?:always|usually|typically|normally)\s+([^.!?]+)", "regular_habit"),
            (r"I\s+(?:never|rarely|seldom)\s+([^.!?]+)", "avoidance"),
            (r"Every\s+(?:day|morning|evening|night|week|weekend)\s+I\s+([^.!?]+)", "routine"),
            (r"I\s+(?:tend|like)\s+to\s+([^.!?]+)", "tendency"),
            (r"(?:Before|After)\s+([^,]+),\s+I\s+([^.!?]+)", "conditional_habit"),
        ]
        
        for pattern, habit_type in habit_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                habit = {
                    "text": match.group(),
                    "type": habit_type,
                    "habit": match.group(1).strip() if len(match.groups()) >= 1 else match.group(),
                    "confidence": 0.85
                }
                
                # For conditional habits, extract both parts
                if habit_type == "conditional_habit" and len(match.groups()) > 1:
                    habit["condition"] = match.group(1).strip()
                    habit["habit"] = match.group(2).strip()
                
                habits.append(habit)
        
        return habits