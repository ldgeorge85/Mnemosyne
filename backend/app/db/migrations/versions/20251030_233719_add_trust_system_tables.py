"""add_trust_system_tables

Revision ID: 007b16b7f352
Revises: e5641d2d08e0
Create Date: 2025-10-30 23:37:19.603241+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007b16b7f352'
down_revision: Union[str, None] = 'e5641d2d08e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enums - checkfirst will prevent creation if they already exist
    sa.Enum('AWARENESS', 'RECOGNITION', 'FAMILIARITY', 'SHARED_MEMORY', 'DEEP_TRUST', name='trustlevel').create(op.get_bind(), checkfirst=True)
    sa.Enum('DISCLOSURE', 'INTERACTION', 'CONFLICT', 'ALIGNMENT', 'DIVERGENCE', 'RESONANCE', name='trusteventtype').create(op.get_bind(), checkfirst=True)
    sa.Enum('PENDING', 'REVIEWING', 'RESOLVED', 'WITHDRAWN', 'ESCALATED', name='appealstatus').create(op.get_bind(), checkfirst=True)

    # Create trust_events table
    op.create_table(
        'trust_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('event_type', postgresql.ENUM('DISCLOSURE', 'INTERACTION', 'CONFLICT', 'ALIGNMENT', 'DIVERGENCE', 'RESONANCE', name='trusteventtype', create_type=False), nullable=False),
        sa.Column('trust_delta', sa.Float()),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('resolver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('appeal_id', postgresql.UUID(as_uuid=True)),
        sa.Column('policy_version', sa.String(20), server_default='v1'),
        sa.Column('visibility_scope', sa.String(20), server_default='private'),
        sa.Column('user_consent', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('content_hash', sa.String(64)),
        sa.Column('previous_hash', sa.String(64))
    )

    # Create appeals table
    op.create_table(
        'appeals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('trust_event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trust_events.id'), nullable=False),
        sa.Column('appellant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'REVIEWING', 'RESOLVED', 'WITHDRAWN', 'ESCALATED', name='appealstatus', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('appeal_reason', sa.Text()),
        sa.Column('resolution', sa.Text()),
        sa.Column('evidence', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('witness_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('review_board_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('submitted_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('review_deadline', sa.DateTime()),
        sa.Column('appeal_metadata', postgresql.JSON(astext_type=sa.Text()))
    )

    # Add foreign key from trust_events to appeals (circular reference)
    op.create_foreign_key(
        'fk_trust_events_appeal_id',
        'trust_events', 'appeals',
        ['appeal_id'], ['id']
    )

    # Create trust_relationships table
    op.create_table(
        'trust_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_a_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('user_b_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('trust_level', postgresql.ENUM('AWARENESS', 'RECOGNITION', 'FAMILIARITY', 'SHARED_MEMORY', 'DEEP_TRUST', name='trustlevel', create_type=False), server_default='AWARENESS'),
        sa.Column('trust_score', sa.Float(), server_default='0.0'),
        sa.Column('resonance_score', sa.Float(), server_default='0.0'),
        sa.Column('disclosure_level_a', sa.Integer(), server_default='0'),
        sa.Column('disclosure_level_b', sa.Integer(), server_default='0'),
        sa.Column('reciprocity_balance', sa.Float(), server_default='0.0'),
        sa.Column('interaction_count', sa.Integer(), server_default='0'),
        sa.Column('last_interaction', sa.DateTime()),
        sa.Column('first_interaction', sa.DateTime()),
        sa.Column('decay_rate', sa.Float(), server_default='0.95'),
        sa.Column('recovery_rate', sa.Float(), server_default='1.1'),
        sa.Column('shared_context', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('relationship_metadata', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'))
    )

    # Create consciousness_maps table
    op.create_table(
        'consciousness_maps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('opted_in', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('opt_in_date', sa.DateTime()),
        sa.Column('opt_out_date', sa.DateTime()),
        sa.Column('patterns', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('pattern_history', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('observation_count', sa.Integer(), server_default='0'),
        sa.Column('user_values', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('user_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('last_observed', sa.DateTime())
    )

    # Create indexes for performance
    op.create_index('ix_trust_events_actor_id', 'trust_events', ['actor_id'])
    op.create_index('ix_trust_events_subject_id', 'trust_events', ['subject_id'])
    op.create_index('ix_trust_events_reporter_id', 'trust_events', ['reporter_id'])
    op.create_index('ix_trust_events_created_at', 'trust_events', ['created_at'])

    op.create_index('ix_appeals_trust_event_id', 'appeals', ['trust_event_id'])
    op.create_index('ix_appeals_appellant_id', 'appeals', ['appellant_id'])
    op.create_index('ix_appeals_status', 'appeals', ['status'])
    op.create_index('ix_appeals_submitted_at', 'appeals', ['submitted_at'])

    op.create_index('ix_trust_relationships_user_a_id', 'trust_relationships', ['user_a_id'])
    op.create_index('ix_trust_relationships_user_b_id', 'trust_relationships', ['user_b_id'])
    op.create_index('ix_trust_relationships_user_a_b', 'trust_relationships', ['user_a_id', 'user_b_id'], unique=True)

    op.create_index('ix_consciousness_maps_user_id', 'consciousness_maps', ['user_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_consciousness_maps_user_id', 'consciousness_maps')
    op.drop_index('ix_trust_relationships_user_a_b', 'trust_relationships')
    op.drop_index('ix_trust_relationships_user_b_id', 'trust_relationships')
    op.drop_index('ix_trust_relationships_user_a_id', 'trust_relationships')
    op.drop_index('ix_appeals_submitted_at', 'appeals')
    op.drop_index('ix_appeals_status', 'appeals')
    op.drop_index('ix_appeals_appellant_id', 'appeals')
    op.drop_index('ix_appeals_trust_event_id', 'appeals')
    op.drop_index('ix_trust_events_created_at', 'trust_events')
    op.drop_index('ix_trust_events_reporter_id', 'trust_events')
    op.drop_index('ix_trust_events_subject_id', 'trust_events')
    op.drop_index('ix_trust_events_actor_id', 'trust_events')

    # Drop tables
    op.drop_table('consciousness_maps')
    op.drop_table('trust_relationships')

    # Drop foreign key from trust_events to appeals
    op.drop_constraint('fk_trust_events_appeal_id', 'trust_events', type_='foreignkey')

    op.drop_table('appeals')
    op.drop_table('trust_events')

    # Drop enums
    sa.Enum(name='appealstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='trusteventtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='trustlevel').drop(op.get_bind(), checkfirst=True)
