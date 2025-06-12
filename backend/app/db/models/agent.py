"""
SQLAlchemy models for agents, agent links, agent logs, and memory reflection (Phase 3).
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Integer
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='active')
    # Relationships
    links = relationship('AgentLink', back_populates='agent')
    logs = relationship('AgentLog', back_populates='agent')

class AgentLink(Base):
    __tablename__ = 'agent_links'
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(String, ForeignKey('agents.id'))
    child_id = Column(String, ForeignKey('agents.id'))
    agent = relationship('Agent', back_populates='links', foreign_keys=[parent_id])

class AgentLog(Base):
    __tablename__ = 'agent_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey('agents.id'))
    log = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    agent = relationship('Agent', back_populates='logs')

class MemoryReflection(Base):
    __tablename__ = 'memory_reflections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, ForeignKey('agents.id'))
    reflection = Column(JSON, nullable=False)
    importance_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
