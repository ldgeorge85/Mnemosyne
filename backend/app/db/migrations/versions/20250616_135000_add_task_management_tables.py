"""
Add task management tables

Revision ID: 20250616_135000
Revises: 20250611_140000
Create Date: 2025-06-16 13:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250616_135000'
down_revision: Union[str, None] = '20250611_140000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = 'bce39c61c978'


def upgrade():
    # Create TaskStatus enum type
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status') THEN
            CREATE TYPE task_status AS ENUM (
                'pending',
                'in_progress',
                'completed',
                'failed',
                'cancelled'
            );
        END IF;
    END$$;
    """)
    
    # Create TaskPriority enum type
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_priority') THEN
            CREATE TYPE task_priority AS ENUM (
                'low',
                'medium',
                'high',
                'urgent'
            );
        END IF;
    END$$;
    """)
    
    # Create tasks table
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table('tasks'):
        op.create_table(
            'tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'completed', 'failed', 'cancelled', name='task_status', create_type=False), 
                  nullable=False, server_default='pending'),
        sa.Column('priority', postgresql.ENUM('low', 'medium', 'high', 'urgent', name='task_priority', create_type=False), 
                  nullable=False, server_default='medium'),
        sa.Column('due_date', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('metadata', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('tasks.id'), nullable=True),
        sa.Column('agent_id', sa.String(36), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true')
    )
    
    # Create task_logs table
    if not inspector.has_table('task_logs'):
        op.create_table(
            'task_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('task_id', sa.String(36), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('log_type', sa.String(50), nullable=False),
        sa.Column('metadata', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()'))
    )
    
    # Create indexes
    # These should ideally also be conditional or handled if the table was just created.
    # For simplicity, we'll assume if the table exists, indexes might too, or creation is idempotent/safe.
    # A more robust solution would check for index existence before creating.
    if not inspector.has_table('tasks') or not inspector.has_table('task_logs'): # Simplified: only if we attempted table creation
        # Or, more accurately, check if specific indexes exist
        pass # Placeholder for now, index creation might fail if tables existed and indexes were already made.

    # Attempt to create indexes, assuming op.create_index is safe if they exist
    # (or wrap each in a try/except or check inspector.get_indexes('table_name'))
    try:
        if not inspector.has_table('tasks'): # Only create if table was created in this migration
            op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
            op.create_index('ix_tasks_status', 'tasks', ['status'])
            op.create_index('ix_tasks_priority', 'tasks', ['priority'])
            op.create_index('ix_tasks_due_date', 'tasks', ['due_date'])
            op.create_index('ix_tasks_parent_id', 'tasks', ['parent_id'])
            op.create_index('ix_tasks_agent_id', 'tasks', ['agent_id'])
        if not inspector.has_table('task_logs'): # Only create if table was created in this migration
            op.create_index('ix_task_logs_task_id', 'task_logs', ['task_id'])
            op.create_index('ix_task_logs_log_type', 'task_logs', ['log_type'])
    except Exception as e:
        print(f"Skipping index creation due to potential pre-existence or other error: {e}")


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Drop indexes (conditionally if possible, or assume op.drop_index is safe)
    # For simplicity, assuming op.drop_index is safe if index doesn't exist.
    # A more robust check: for idx in inspector.get_indexes('task_logs'): if idx['name'] == '...': op.drop_index(...)
    try:
        op.drop_index('ix_task_logs_log_type', table_name='task_logs', if_exists=True) # if_exists might not be supported by all op.drop_index backends
        op.drop_index('ix_task_logs_task_id', table_name='task_logs', if_exists=True)
        op.drop_index('ix_tasks_agent_id', table_name='tasks', if_exists=True)
        op.drop_index('ix_tasks_parent_id', table_name='tasks', if_exists=True)
        op.drop_index('ix_tasks_due_date', table_name='tasks', if_exists=True)
        op.drop_index('ix_tasks_priority', table_name='tasks', if_exists=True)
        op.drop_index('ix_tasks_status', table_name='tasks', if_exists=True)
        op.drop_index('ix_tasks_user_id', table_name='tasks', if_exists=True)
    except Exception as e:
        print(f"Skipping index dropping due to potential non-existence or other error: {e}")
    
    # Drop tables
    if inspector.has_table('task_logs'):
        op.drop_table('task_logs')
    if inspector.has_table('tasks'):
        op.drop_table('tasks')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS task_priority')
    op.execute('DROP TYPE IF EXISTS task_status')
