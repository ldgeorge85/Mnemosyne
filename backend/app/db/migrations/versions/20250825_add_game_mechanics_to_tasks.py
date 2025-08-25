"""Add game mechanics and time awareness to tasks

Revision ID: add_game_mechanics
Revises: 20250811_114603
Create Date: 2025-08-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_game_mechanics'
down_revision = 'e2096a5ba4f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add game mechanics and time awareness fields to tasks table."""
    
    # Create the quest_type enum
    quest_type_enum = postgresql.ENUM(
        'TUTORIAL', 'DAILY', 'SOLO', 'PARTY', 'RAID', 'EPIC', 'CHALLENGE',
        name='questtype'
    )
    quest_type_enum.create(op.get_bind())
    
    # Add BLOCKED to task status enum
    op.execute("ALTER TYPE taskstatus ADD VALUE IF NOT EXISTS 'BLOCKED'")
    
    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('actual_duration_minutes', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('started_at', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('progress', sa.Float(), nullable=False, server_default='0.0'))
    
    # Game mechanics columns
    op.add_column('tasks', sa.Column('difficulty', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('tasks', sa.Column('quest_type', sa.Enum('TUTORIAL', 'DAILY', 'SOLO', 'PARTY', 'RAID', 'EPIC', 'CHALLENGE', name='questtype'), nullable=True))
    op.add_column('tasks', sa.Column('experience_points', sa.Integer(), nullable=False, server_default='0'))
    
    # Identity shaping columns
    op.add_column('tasks', sa.Column('value_impact', sa.JSON(), nullable=True, server_default='{}'))
    op.add_column('tasks', sa.Column('skill_development', sa.JSON(), nullable=True, server_default='{}'))
    
    # Privacy and sovereignty columns
    op.add_column('tasks', sa.Column('visibility_mask', sa.String(50), nullable=False, server_default='private'))
    op.add_column('tasks', sa.Column('encrypted_content', sa.Boolean(), nullable=False, server_default='false'))
    
    # Collaboration columns
    op.add_column('tasks', sa.Column('is_shared', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks', sa.Column('assignees', sa.JSON(), nullable=True, server_default='[]'))
    op.add_column('tasks', sa.Column('requires_all_complete', sa.Boolean(), nullable=False, server_default='false'))
    
    # Recurrence columns
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks', sa.Column('recurrence_rule', sa.String(255), nullable=True))
    op.add_column('tasks', sa.Column('recurring_parent_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Additional context
    op.add_column('tasks', sa.Column('context', sa.JSON(), nullable=True, server_default='{}'))
    
    # Create indexes for better query performance
    op.create_index('ix_tasks_status_user_id', 'tasks', ['status', 'user_id'])
    op.create_index('ix_tasks_quest_type', 'tasks', ['quest_type'])
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('ix_tasks_visibility_mask', 'tasks', ['visibility_mask'])
    

def downgrade() -> None:
    """Remove game mechanics and time awareness fields from tasks table."""
    
    # Drop indexes
    op.drop_index('ix_tasks_visibility_mask', table_name='tasks')
    op.drop_index('ix_tasks_due_date', table_name='tasks')
    op.drop_index('ix_tasks_quest_type', table_name='tasks')
    op.drop_index('ix_tasks_status_user_id', table_name='tasks')
    
    # Drop columns
    op.drop_column('tasks', 'context')
    op.drop_column('tasks', 'recurring_parent_id')
    op.drop_column('tasks', 'recurrence_rule')
    op.drop_column('tasks', 'is_recurring')
    op.drop_column('tasks', 'requires_all_complete')
    op.drop_column('tasks', 'assignees')
    op.drop_column('tasks', 'is_shared')
    op.drop_column('tasks', 'encrypted_content')
    op.drop_column('tasks', 'visibility_mask')
    op.drop_column('tasks', 'skill_development')
    op.drop_column('tasks', 'value_impact')
    op.drop_column('tasks', 'experience_points')
    op.drop_column('tasks', 'quest_type')
    op.drop_column('tasks', 'difficulty')
    op.drop_column('tasks', 'progress')
    op.drop_column('tasks', 'started_at')
    op.drop_column('tasks', 'actual_duration_minutes')
    op.drop_column('tasks', 'estimated_duration_minutes')
    
    # Drop the quest_type enum
    quest_type_enum = postgresql.ENUM(name='questtype')
    quest_type_enum.drop(op.get_bind())
    
    # Note: We can't easily remove BLOCKED from taskstatus enum in a downgrade
    # This would require recreating the enum and all columns that use it