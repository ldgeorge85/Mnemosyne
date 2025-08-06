"""
SQLAlchemy models for agents, agent links, agent logs, and memory reflection (Phase 3).
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import datetime

from app.db.base_model import BaseModel

class Agent(BaseModel):
    __tablename__ = 'agents'
    name = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='active')
    # Relationships
    links = relationship('AgentLink', back_populates='agent', foreign_keys='AgentLink.parent_id')
    logs = relationship('AgentLog', back_populates='agent')
    tasks = relationship('Task', back_populates='agent')

class AgentLink(BaseModel):
    __tablename__ = 'agent_links'
    parent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'))
    child_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'))
    agent = relationship('Agent', back_populates='links', foreign_keys=[parent_id])

class AgentLog(BaseModel):
    __tablename__ = 'agent_logs'
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'))
    log = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    agent = relationship('Agent', back_populates='logs')

class MemoryReflection(BaseModel):
    __tablename__ = 'memory_reflections'
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id'))
    reflection = Column(JSON, nullable=False)
    importance_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship to Agent
    agent = relationship("Agent")
