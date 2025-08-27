"""Add trust system tables

Revision ID: 001_trust_system
Revises: 
Create Date: 2025-08-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_trust_system'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create trust event type enum
    op.execute("CREATE TYPE trusteventtype AS ENUM ('disclosure', 'interaction', 'conflict', 'alignment', 'divergence', 'resonance')")
    
    # Create appeal status enum
    op.execute("CREATE TYPE appealstatus AS ENUM ('pending', 'reviewing', 'resolved', 'withdrawn', 'escalated')")
    
    # Create trust level enum
    op.execute("CREATE TYPE trustlevel AS ENUM ('awareness', 'recognition', 'familiarity', 'shared_memory', 'deep_trust')")
    
    # Create appeals table first (since trust_events references it)
    op.create_table('appeals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trust_event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('appellant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('pending', 'reviewing', 'resolved', 'withdrawn', 'escalated', name='appealstatus'), nullable=False),
        sa.Column('appeal_reason', sa.Text(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('evidence', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('witness_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('review_board_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('review_deadline', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['appellant_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create trust_events table
    op.create_table('trust_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.Enum('disclosure', 'interaction', 'conflict', 'alignment', 'divergence', 'resonance', name='trusteventtype'), nullable=False),
        sa.Column('trust_delta', sa.Float(), nullable=True),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolver_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('appeal_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('policy_version', sa.String(length=20), nullable=True),
        sa.Column('visibility_scope', sa.String(length=20), nullable=True),
        sa.Column('user_consent', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['appeal_id'], ['appeals.id'], ),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['resolver_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key from appeals back to trust_events
    op.create_foreign_key(None, 'appeals', 'trust_events', ['trust_event_id'], ['id'])
    
    # Create trust_relationships table
    op.create_table('trust_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_a_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_b_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trust_level', sa.Enum('awareness', 'recognition', 'familiarity', 'shared_memory', 'deep_trust', name='trustlevel'), nullable=True),
        sa.Column('trust_score', sa.Float(), nullable=True),
        sa.Column('resonance_score', sa.Float(), nullable=True),
        sa.Column('disclosure_level_a', sa.Integer(), nullable=True),
        sa.Column('disclosure_level_b', sa.Integer(), nullable=True),
        sa.Column('reciprocity_balance', sa.Float(), nullable=True),
        sa.Column('interaction_count', sa.Integer(), nullable=True),
        sa.Column('last_interaction', sa.DateTime(), nullable=True),
        sa.Column('first_interaction', sa.DateTime(), nullable=True),
        sa.Column('decay_rate', sa.Float(), nullable=True),
        sa.Column('recovery_rate', sa.Float(), nullable=True),
        sa.Column('shared_context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_a_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_b_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create consciousness_maps table (opt-in only)
    op.create_table('consciousness_maps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('opted_in', sa.Boolean(), nullable=False),
        sa.Column('opt_in_date', sa.DateTime(), nullable=True),
        sa.Column('opt_out_date', sa.DateTime(), nullable=True),
        sa.Column('patterns', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('pattern_history', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('observation_count', sa.Integer(), nullable=True),
        sa.Column('user_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_observed', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('ix_trust_events_actor_id', 'trust_events', ['actor_id'])
    op.create_index('ix_trust_events_subject_id', 'trust_events', ['subject_id'])
    op.create_index('ix_trust_events_created_at', 'trust_events', ['created_at'])
    op.create_index('ix_appeals_status', 'appeals', ['status'])
    op.create_index('ix_appeals_appellant_id', 'appeals', ['appellant_id'])
    op.create_index('ix_trust_relationships_users', 'trust_relationships', ['user_a_id', 'user_b_id'], unique=True)
    op.create_index('ix_consciousness_maps_user_id', 'consciousness_maps', ['user_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_consciousness_maps_user_id', 'consciousness_maps')
    op.drop_index('ix_trust_relationships_users', 'trust_relationships')
    op.drop_index('ix_appeals_appellant_id', 'appeals')
    op.drop_index('ix_appeals_status', 'appeals')
    op.drop_index('ix_trust_events_created_at', 'trust_events')
    op.drop_index('ix_trust_events_subject_id', 'trust_events')
    op.drop_index('ix_trust_events_actor_id', 'trust_events')
    
    # Drop tables
    op.drop_table('consciousness_maps')
    op.drop_table('trust_relationships')
    op.drop_table('trust_events')
    op.drop_table('appeals')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS trustlevel")
    op.execute("DROP TYPE IF EXISTS appealstatus")
    op.execute("DROP TYPE IF EXISTS trusteventtype")