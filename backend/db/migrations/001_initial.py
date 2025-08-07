"""
Initial database migration for Mnemosyne Protocol
Creates all core tables with indexes and constraints
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

# Revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all initial tables"""
    
    # Create custom types/enums
    op.execute("CREATE EXTENSION IF NOT EXISTS 'uuid-ossp';")
    op.execute("CREATE EXTENSION IF NOT EXISTS 'vector';")
    
    # Create enum types
    op.execute("""
        CREATE TYPE initiation_level AS ENUM ('observer', 'fragmentor', 'agent', 'keeper');
        CREATE TYPE memory_type AS ENUM ('conversation', 'reflection', 'consolidation', 'external', 'system', 'ritual', 'signal');
        CREATE TYPE memory_status AS ENUM ('pending', 'processing', 'processed', 'consolidated', 'archived', 'failed');
        CREATE TYPE agent_type AS ENUM (
            'engineer', 'librarian', 'priest', 'mycelium',
            'stoic', 'sage', 'critic', 'trickster', 'builder', 'mystic',
            'guardian', 'healer', 'scholar', 'prophet',
            'matchmaker', 'gap_finder', 'synthesizer', 'arbitrator', 'curator', 'ritual_master'
        );
        CREATE TYPE reflection_type AS ENUM ('analysis', 'synthesis', 'pattern', 'insight', 'warning', 'question', 'connection', 'ritual');
        CREATE TYPE signal_visibility AS ENUM ('private', 'trusted', 'collective', 'public');
        CREATE TYPE trust_fragment_type AS ENUM ('glyphic', 'ritual', 'proof', 'reciprocal');
        CREATE TYPE sharing_depth AS ENUM ('summary', 'detailed', 'full');
        CREATE TYPE trust_stage AS ENUM ('signal_exchange', 'domain_revelation', 'capability_sharing', 'memory_glimpse', 'full_trust');
        CREATE TYPE ritual_type AS ENUM ('progressive', 'mirrored_dissonance', 'echo_drift', 'symbolic_proof');
    """)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Authentication
        sa.Column('username', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        
        # Profile
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('bio', sa.String(500), nullable=True),
        sa.Column('sigil', sa.String(10), nullable=True),
        sa.Column('glyphs', sa.JSON, default=list),
        
        # Initiation
        sa.Column('initiation_level', postgresql.ENUM('observer', 'fragmentor', 'agent', 'keeper', name='initiation_level'), default='observer', nullable=False),
        sa.Column('initiated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trust_score', sa.Float, default=0.0, nullable=False),
        sa.Column('reputation', sa.Float, default=1.0, nullable=False),
        
        # Deep Signal
        sa.Column('signal_coherence', sa.Float, default=1.0, nullable=False),
        sa.Column('fracture_index', sa.Float, default=0.0, nullable=False),
        sa.Column('integration_level', sa.Float, default=0.5, nullable=False),
        sa.Column('last_signal_at', sa.DateTime(timezone=True), nullable=True),
        
        # Personality
        sa.Column('personality', postgresql.JSONB, default={}, nullable=False),
        sa.Column('domains', sa.JSON, default=list),
        sa.Column('stack', sa.JSON, default=list),
        
        # Activity tracking
        sa.Column('memory_count', sa.Integer, default=0, nullable=False),
        sa.Column('reflection_count', sa.Integer, default=0, nullable=False),
        sa.Column('ritual_count', sa.Integer, default=0, nullable=False),
        sa.Column('consolidation_count', sa.Integer, default=0, nullable=False),
        
        # Settings
        sa.Column('settings', postgresql.JSONB, default={}, nullable=False),
        
        # Status
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False, nullable=False),
        sa.Column('is_suspended', sa.Boolean, default=False, nullable=False),
        sa.Column('crisis_mode', sa.Boolean, default=False, nullable=False),
        sa.Column('intended_silence', sa.Boolean, default=False, nullable=False),
        
        # Auth tracking
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer, default=0, nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        
        # API keys
        sa.Column('api_key_hash', sa.String(255), nullable=True),
        sa.Column('refresh_token_hash', sa.String(255), nullable=True),
    )
    
    # Create indexes for users
    op.create_index('ix_users_initiation_level', 'users', ['initiation_level'])
    op.create_index('ix_users_trust_score', 'users', ['trust_score'])
    op.create_index('ix_users_last_login', 'users', ['last_login_at'])
    op.create_index('ix_users_signal_coherence', 'users', ['signal_coherence'])
    
    # Create memories table
    op.create_table(
        'memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        
        # User relationship
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Content
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        
        # Type and status
        sa.Column('memory_type', postgresql.ENUM('conversation', 'reflection', 'consolidation', 'external', 'system', 'ritual', 'signal', name='memory_type'), default='conversation', nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'processed', 'consolidated', 'archived', 'failed', name='memory_status'), default='pending', nullable=False),
        
        # Vector embeddings
        sa.Column('embedding_content', Vector(1536), nullable=True),
        sa.Column('embedding_semantic', Vector(768), nullable=True),
        sa.Column('embedding_contextual', Vector(384), nullable=True),
        
        # Scores
        sa.Column('importance', sa.Float, default=0.5, nullable=False),
        sa.Column('relevance', sa.Float, default=0.5, nullable=False),
        sa.Column('emotional_valence', sa.Float, default=0.0, nullable=False),
        sa.Column('confidence', sa.Float, default=0.8, nullable=False),
        
        # Consolidation
        sa.Column('consolidation_count', sa.Integer, default=0, nullable=False),
        sa.Column('consolidation_group_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('parent_memory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('memories.id', ondelete='SET NULL'), nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, default={}, nullable=False),
        sa.Column('tags', sa.JSON, default=list),
        sa.Column('domains', sa.JSON, default=list),
        sa.Column('entities', sa.JSON, default=list),
        
        # Source
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('source_url', sa.Text, nullable=True),
        sa.Column('source_metadata', postgresql.JSONB, default={}),
        
        # Temporal
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('access_count', sa.Integer, default=0, nullable=False),
        
        # Drift and decay
        sa.Column('drift_index', sa.Float, default=0.0, nullable=False),
        sa.Column('decay_rate', sa.Float, default=1.0, nullable=False),
        sa.Column('last_refreshed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Privacy
        sa.Column('is_private', sa.Boolean, default=True, nullable=False),
        sa.Column('sharing_level', sa.Integer, default=0, nullable=False),
        sa.Column('encrypted', sa.Boolean, default=False, nullable=False),
        sa.Column('encryption_key_id', sa.String(100), nullable=True),
    )
    
    # Create indexes for memories
    op.create_index('ix_memories_user_importance', 'memories', ['user_id', 'importance'])
    op.create_index('ix_memories_user_type', 'memories', ['user_id', 'memory_type'])
    op.create_index('ix_memories_user_occurred', 'memories', ['user_id', 'occurred_at'])
    op.create_index('ix_memories_drift', 'memories', ['drift_index'])
    
    # Vector indexes (using IVFFlat for performance)
    op.execute("CREATE INDEX ix_memories_embedding_content ON memories USING ivfflat (embedding_content vector_cosine_ops);")
    op.execute("CREATE INDEX ix_memories_embedding_semantic ON memories USING ivfflat (embedding_semantic vector_cosine_ops);")
    
    # Create reflections table
    op.create_table(
        'reflections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Relationships
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('memory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('memories.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Agent info
        sa.Column('agent_type', postgresql.ENUM(
            'engineer', 'librarian', 'priest', 'mycelium',
            'stoic', 'sage', 'critic', 'trickster', 'builder', 'mystic',
            'guardian', 'healer', 'scholar', 'prophet',
            'matchmaker', 'gap_finder', 'synthesizer', 'arbitrator', 'curator', 'ritual_master',
            name='agent_type'
        ), nullable=False),
        sa.Column('agent_id', sa.String(100), nullable=False),
        sa.Column('agent_symbol', sa.String(10), nullable=False),
        
        # Content
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('reflection_type', postgresql.ENUM('analysis', 'synthesis', 'pattern', 'insight', 'warning', 'question', 'connection', 'ritual', name='reflection_type'), default='analysis', nullable=False),
        
        # Embedding
        sa.Column('embedding', Vector(1536), nullable=True),
        
        # Scores
        sa.Column('confidence', sa.Float, default=0.7, nullable=False),
        sa.Column('relevance', sa.Float, default=0.5, nullable=False),
        sa.Column('coherence', sa.Float, default=0.8, nullable=False),
        sa.Column('drift_from_memory', sa.Float, default=0.0, nullable=False),
        
        # Sub-signal
        sa.Column('sub_signal', postgresql.JSONB, default={}, nullable=False),
        sa.Column('signal_modulation', sa.Float, default=0.0, nullable=False),
        
        # Insights
        sa.Column('patterns', sa.JSON, default=list),
        sa.Column('connections', sa.JSON, default=list),
        sa.Column('questions', sa.JSON, default=list),
        sa.Column('recommendations', sa.JSON, default=list),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, default={}, nullable=False),
        sa.Column('tags', sa.JSON, default=list),
        sa.Column('domains', sa.JSON, default=list),
        
        # Processing
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('prompt_tokens', sa.Integer, nullable=True),
        sa.Column('completion_tokens', sa.Integer, nullable=True),
        
        # Consolidation
        sa.Column('is_consolidated', sa.Boolean, default=False, nullable=False),
        sa.Column('consolidation_group_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('decay_rate', sa.Float, default=1.0, nullable=False),
        sa.Column('last_evaluated_at', sa.DateTime(timezone=True), nullable=True),
        
        # User feedback
        sa.Column('user_rating', sa.Float, nullable=True),
        sa.Column('user_feedback', sa.Text, nullable=True),
        sa.Column('was_helpful', sa.Boolean, nullable=True),
    )
    
    # Create indexes for reflections
    op.create_index('ix_reflections_user_agent', 'reflections', ['user_id', 'agent_type'])
    op.create_index('ix_reflections_memory_agent', 'reflections', ['memory_id', 'agent_type'])
    op.create_index('ix_reflections_confidence', 'reflections', ['confidence'])
    op.create_index('ix_reflections_drift', 'reflections', ['drift_from_memory'])
    op.execute("CREATE INDEX ix_reflections_embedding ON reflections USING ivfflat (embedding vector_cosine_ops);")
    
    # Create signals table
    op.create_table(
        'signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # User relationship
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Signal identity
        sa.Column('version', sa.String(10), default='3.1', nullable=False),
        sa.Column('signal_hash', sa.String(64), unique=True, nullable=False, index=True),
        
        # Symbolic identity
        sa.Column('sigil', sa.String(10), nullable=False),
        sa.Column('glyphs', sa.JSON, default=list),
        sa.Column('symbolic_role', sa.String(50), nullable=True),
        sa.Column('symbolic_glyph', sa.String(10), nullable=True),
        
        # Domains and capabilities
        sa.Column('domains', sa.JSON, default=list),
        sa.Column('stack', sa.JSON, default=list),
        sa.Column('capabilities', sa.JSON, default=list),
        
        # Personality
        sa.Column('personality', postgresql.JSONB, default={}),
        
        # Coherence
        sa.Column('coherence', sa.Float, default=1.0, nullable=False, index=True),
        sa.Column('fracture_index', sa.Float, default=0.0, nullable=False, index=True),
        sa.Column('integration_level', sa.Float, default=0.5, nullable=False),
        sa.Column('recovery_vectors', sa.JSON, default=list),
        
        # Status
        sa.Column('flags', postgresql.JSONB, default={}),
        
        # Visibility
        sa.Column('visibility', sa.Float, default=0.3, nullable=False),
        sa.Column('visibility_level', postgresql.ENUM('private', 'trusted', 'collective', 'public', name='signal_visibility'), default='collective', nullable=False),
        
        # Trust fragment
        sa.Column('trust_fragment_type', postgresql.ENUM('glyphic', 'ritual', 'proof', 'reciprocal', name='trust_fragment_type'), nullable=True),
        sa.Column('trust_fragment_depth', sa.String(20), nullable=True),
        sa.Column('trust_fragment_data', postgresql.JSONB, default={}),
        sa.Column('verified_by', sa.JSON, default=list),
        
        # Embedding
        sa.Column('embedding', Vector(1536), nullable=True),
        
        # Lifecycle
        sa.Column('entropy', sa.Float, default=1.0, nullable=False),
        sa.Column('decay_timer_days', sa.Integer, default=30, nullable=False),
        sa.Column('last_refreshed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('emission_count', sa.Integer, default=0, nullable=False),
        sa.Column('resonance_count', sa.Integer, default=0, nullable=False),
        
        # Drift
        sa.Column('local_drift_index', sa.Float, default=0.0, nullable=False),
        sa.Column('global_drift_index', sa.Float, default=0.0, nullable=False),
        sa.Column('drift_indicators', sa.JSON, default=list),
        
        # Kartouche
        sa.Column('kartouche_svg', sa.Text, nullable=True),
        sa.Column('kartouche_layers', postgresql.JSONB, default={}),
        sa.Column('symbolic_trail', sa.JSON, default=list),
        
        # Performance
        sa.Column('propagation_count', sa.Integer, default=0, nullable=False),
        sa.Column('match_count', sa.Integer, default=0, nullable=False),
        sa.Column('response_rate', sa.Float, default=0.0, nullable=False),
        
        # Crypto
        sa.Column('signature', sa.Text, nullable=False),
        sa.Column('public_key', sa.Text, nullable=True),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, default={}),
    )
    
    # Create indexes for signals
    op.create_index('ix_signals_user_coherence', 'signals', ['user_id', 'coherence'])
    op.create_index('ix_signals_visibility_level', 'signals', ['visibility_level'])
    op.create_index('ix_signals_fracture', 'signals', ['fracture_index'])
    op.create_index('ix_signals_entropy', 'signals', ['entropy'])
    op.execute("CREATE INDEX ix_signals_embedding ON signals USING ivfflat (embedding vector_cosine_ops);")
    
    # Create sharing_contracts table
    op.create_table(
        'sharing_contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # User and collective
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('collective_id', sa.String(100), nullable=False, index=True),
        sa.Column('collective_name', sa.String(255), nullable=True),
        
        # Sharing parameters
        sa.Column('domains', sa.JSON, default=list),
        sa.Column('depth', postgresql.ENUM('summary', 'detailed', 'full', name='sharing_depth'), default='summary', nullable=False),
        
        # Privacy
        sa.Column('k_anonymity', sa.Integer, default=3, nullable=False),
        sa.Column('anonymous', sa.Boolean, default=False, nullable=False),
        sa.Column('encrypted', sa.Boolean, default=False, nullable=False),
        
        # Time constraints
        sa.Column('start_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_days', sa.Integer, nullable=True),
        
        # Control
        sa.Column('revocable', sa.Boolean, default=True, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_revoked', sa.Boolean, default=False, nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        
        # Filters
        sa.Column('filters', postgresql.JSONB, default={}),
        
        # Usage
        sa.Column('share_count', sa.Integer, default=0, nullable=False),
        sa.Column('access_count', sa.Integer, default=0, nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Reciprocity
        sa.Column('reciprocal_contract_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sharing_contracts.id', ondelete='SET NULL'), nullable=True),
        sa.Column('has_reciprocity', sa.Boolean, default=False, nullable=False),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('notes', sa.Text, nullable=True),
    )
    
    # Create indexes for sharing_contracts
    op.create_index('ix_sharing_contracts_user_collective', 'sharing_contracts', ['user_id', 'collective_id'])
    op.create_index('ix_sharing_contracts_active', 'sharing_contracts', ['is_active'])
    op.create_index('ix_sharing_contracts_end_date', 'sharing_contracts', ['end_date'])
    
    # Create trust_relationships table
    op.create_table(
        'trust_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Users
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('trusted_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Trust parameters
        sa.Column('trust_stage', postgresql.ENUM('signal_exchange', 'domain_revelation', 'capability_sharing', 'memory_glimpse', 'full_trust', name='trust_stage'), default='signal_exchange', nullable=False),
        sa.Column('trust_score', sa.Float, default=0.0, nullable=False),
        sa.Column('trust_tier', sa.Integer, default=0, nullable=False),
        
        # Ritual
        sa.Column('ritual_type', postgresql.ENUM('progressive', 'mirrored_dissonance', 'echo_drift', 'symbolic_proof', name='ritual_type'), nullable=True),
        sa.Column('ritual_stage', sa.Integer, default=0, nullable=False),
        sa.Column('ritual_completed', sa.Boolean, default=False, nullable=False),
        sa.Column('ritual_data', postgresql.JSONB, default={}),
        
        # Interactions
        sa.Column('positive_interactions', sa.Integer, default=0, nullable=False),
        sa.Column('negative_interactions', sa.Integer, default=0, nullable=False),
        sa.Column('total_interactions', sa.Integer, default=0, nullable=False),
        sa.Column('last_interaction_at', sa.DateTime(timezone=True), nullable=True),
        
        # Resonance
        sa.Column('resonance_score', sa.Float, default=0.0, nullable=False),
        sa.Column('domain_overlap', sa.Float, default=0.0, nullable=False),
        sa.Column('symbolic_compatibility', sa.Float, default=0.0, nullable=False),
        
        # ZK proof
        sa.Column('zk_proof', sa.Text, nullable=True),
        sa.Column('zk_proof_verified', sa.Boolean, default=False, nullable=False),
        sa.Column('zk_proof_expires_at', sa.DateTime(timezone=True), nullable=True),
        
        # Shared context
        sa.Column('shared_memories_count', sa.Integer, default=0, nullable=False),
        sa.Column('shared_reflections_count', sa.Integer, default=0, nullable=False),
        sa.Column('shared_domains', sa.JSON, default=list),
        
        # Trust fragments
        sa.Column('trust_fragments', sa.JSON, default=list),
        sa.Column('fragment_count', sa.Integer, default=0, nullable=False),
        
        # Status
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_mutual', sa.Boolean, default=False, nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False, nullable=False),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB, default={}),
        sa.Column('notes', sa.Text, nullable=True),
        
        # Unique constraint
        sa.UniqueConstraint('user_id', 'trusted_user_id', name='uq_trust_relationships_users'),
    )
    
    # Create indexes for trust_relationships
    op.create_index('ix_trust_relationships_stage', 'trust_relationships', ['trust_stage'])
    op.create_index('ix_trust_relationships_score', 'trust_relationships', ['trust_score'])
    op.create_index('ix_trust_relationships_mutual', 'trust_relationships', ['is_mutual'])
    
    # Add check constraints
    op.execute("""
        ALTER TABLE memories ADD CONSTRAINT ck_memories_importance CHECK (importance >= 0 AND importance <= 1);
        ALTER TABLE memories ADD CONSTRAINT ck_memories_relevance CHECK (relevance >= 0 AND relevance <= 1);
        ALTER TABLE memories ADD CONSTRAINT ck_memories_valence CHECK (emotional_valence >= -1 AND emotional_valence <= 1);
        ALTER TABLE memories ADD CONSTRAINT ck_memories_confidence CHECK (confidence >= 0 AND confidence <= 1);
        ALTER TABLE memories ADD CONSTRAINT ck_memories_drift CHECK (drift_index >= 0 AND drift_index <= 1);
        ALTER TABLE memories ADD CONSTRAINT ck_memories_sharing CHECK (sharing_level >= 0 AND sharing_level <= 5);
        
        ALTER TABLE reflections ADD CONSTRAINT ck_reflections_confidence CHECK (confidence >= 0 AND confidence <= 1);
        ALTER TABLE reflections ADD CONSTRAINT ck_reflections_relevance CHECK (relevance >= 0 AND relevance <= 1);
        ALTER TABLE reflections ADD CONSTRAINT ck_reflections_coherence CHECK (coherence >= 0 AND coherence <= 1);
        ALTER TABLE reflections ADD CONSTRAINT ck_reflections_drift CHECK (drift_from_memory >= 0 AND drift_from_memory <= 1);
        ALTER TABLE reflections ADD CONSTRAINT ck_reflections_modulation CHECK (signal_modulation >= -1 AND signal_modulation <= 1);
        
        ALTER TABLE signals ADD CONSTRAINT ck_signals_coherence CHECK (coherence >= 0 AND coherence <= 1);
        ALTER TABLE signals ADD CONSTRAINT ck_signals_fracture CHECK (fracture_index >= 0 AND fracture_index <= 1);
        ALTER TABLE signals ADD CONSTRAINT ck_signals_integration CHECK (integration_level >= 0 AND integration_level <= 1);
        ALTER TABLE signals ADD CONSTRAINT ck_signals_visibility CHECK (visibility >= 0 AND visibility <= 1);
        ALTER TABLE signals ADD CONSTRAINT ck_signals_entropy CHECK (entropy >= 0 AND entropy <= 1);
        ALTER TABLE signals ADD CONSTRAINT ck_signals_local_drift CHECK (local_drift_index >= 0 AND local_drift_index <= 1);
        ALTER TABLE signals ADD CONSTRAINT ck_signals_global_drift CHECK (global_drift_index >= 0 AND global_drift_index <= 1);
        
        ALTER TABLE sharing_contracts ADD CONSTRAINT ck_sharing_contracts_k_anonymity CHECK (k_anonymity >= 1);
        ALTER TABLE sharing_contracts ADD CONSTRAINT ck_sharing_contracts_duration CHECK (duration_days IS NULL OR duration_days > 0);
        
        ALTER TABLE trust_relationships ADD CONSTRAINT ck_trust_relationships_different_users CHECK (user_id != trusted_user_id);
        ALTER TABLE trust_relationships ADD CONSTRAINT ck_trust_relationships_score CHECK (trust_score >= 0 AND trust_score <= 1);
        ALTER TABLE trust_relationships ADD CONSTRAINT ck_trust_relationships_tier CHECK (trust_tier >= 0 AND trust_tier <= 3);
        ALTER TABLE trust_relationships ADD CONSTRAINT ck_trust_relationships_resonance CHECK (resonance_score >= 0 AND resonance_score <= 1);
    """)


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('trust_relationships')
    op.drop_table('sharing_contracts')
    op.drop_table('signals')
    op.drop_table('reflections')
    op.drop_table('memories')
    op.drop_table('users')
    
    # Drop enum types
    op.execute("""
        DROP TYPE IF EXISTS ritual_type;
        DROP TYPE IF EXISTS trust_stage;
        DROP TYPE IF EXISTS sharing_depth;
        DROP TYPE IF EXISTS trust_fragment_type;
        DROP TYPE IF EXISTS signal_visibility;
        DROP TYPE IF EXISTS reflection_type;
        DROP TYPE IF EXISTS agent_type;
        DROP TYPE IF EXISTS memory_status;
        DROP TYPE IF EXISTS memory_type;
        DROP TYPE IF EXISTS initiation_level;
    """)