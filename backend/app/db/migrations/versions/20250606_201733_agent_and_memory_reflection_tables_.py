"""agent and memory reflection tables (Phase 3)

Revision ID: bce39c61c978
Revises: f9075d69670e
Create Date: 2025-06-06 20:17:33.837864+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bce39c61c978'
down_revision: Union[str, None] = 'f9075d69670e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Agents tables
    op.create_table('agents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('agent_links',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_agent_id', sa.String(length=36), nullable=False),
        sa.Column('target_agent_id', sa.String(length=36), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['source_agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['target_agent_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('agent_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('agent_id', sa.String(length=36), nullable=False),
        sa.Column('log_message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Memory Reflections table
    op.create_table('memory_reflections',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('memory_id', sa.String(length=36), nullable=False),
        sa.Column('agent_id', sa.String(length=36), nullable=False),
        sa.Column('reflection_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['memory_id'], ['memories.id'], ),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('memory_reflections')
    op.drop_table('agent_logs')
    op.drop_table('agent_links')
    op.drop_table('agents')
