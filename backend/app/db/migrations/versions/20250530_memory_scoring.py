"""
Memory scoring tables and updates.

Revision ID: 20250530_memory_scoring
Revises: 20250525_memory_system
Create Date: 2025-05-30

This migration adds the necessary database structure for the memory scoring system,
including tables for storing memory scores, relevance feedback, and score history.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import text
import uuid


# revision identifiers, used by Alembic
revision = '20250530_memory_scoring'
down_revision = '20250525_memory_system'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database schema to support memory scoring."""
    # Add importance_score to memories table
    op.add_column('memories', sa.Column('importance_score', sa.Float(), server_default='0.5', nullable=False))
    
    # Create index on importance_score for faster retrieval of important memories
    op.create_index(op.f('ix_memories_importance_score'), 'memories', ['importance_score'], unique=False)
    
    # Create memory_scores table for detailed scoring information
    op.create_table(
        'memory_scores',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('memory_id', UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('recency_score', sa.Float(), nullable=False),
        sa.Column('access_frequency_score', sa.Float(), nullable=False),
        sa.Column('recent_access_score', sa.Float(), nullable=False),
        sa.Column('explicit_importance_score', sa.Float(), nullable=False),
        sa.Column('semantic_relevance_score', sa.Float(), nullable=False),
        sa.Column('last_scored', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ondelete='CASCADE'),
    )
    
    # Create unique index on memory_id to enforce one score record per memory
    op.create_index(op.f('ix_memory_scores_memory_id'), 'memory_scores', ['memory_id'], unique=True)
    
    # Create memory_relevance_feedback table for user feedback on memory relevance
    op.create_table(
        'memory_relevance_feedback',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('memory_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_score', sa.Float(), nullable=False),
        sa.Column('query_context', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create index on memory_id and user_id for faster queries
    op.create_index(
        op.f('ix_memory_relevance_feedback_memory_id_user_id'),
        'memory_relevance_feedback',
        ['memory_id', 'user_id'],
        unique=False
    )
    
    # Create memory_score_history table to track score changes over time
    op.create_table(
        'memory_score_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('memory_id', UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('factor_scores', JSONB(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ondelete='CASCADE'),
    )
    
    # Create index on memory_id and created_at for faster historical queries
    op.create_index(
        op.f('ix_memory_score_history_memory_id_created_at'),
        'memory_score_history',
        ['memory_id', 'created_at'],
        unique=False
    )
    
    # Update existing memories with default importance_score
    op.execute("""
        UPDATE memories
        SET importance_score = 0.5
        WHERE importance_score IS NULL
    """)


def downgrade():
    """Downgrade database schema to remove memory scoring."""
    # Drop memory_score_history table
    op.drop_table('memory_score_history')
    
    # Drop memory_relevance_feedback table
    op.drop_table('memory_relevance_feedback')
    
    # Drop memory_scores table
    op.drop_table('memory_scores')
    
    # Remove importance_score from memories table
    op.drop_column('memories', 'importance_score')
