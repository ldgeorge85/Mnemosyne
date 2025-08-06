"""
Rename metadata columns to avoid SQLAlchemy reserved keyword conflict

Revision ID: 20250616_165000
Revises: 20250616_155000
Create Date: 2025-06-16 16:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250616_165000'
down_revision = '20250616_155000'
branch_labels = None
depends_on = None


def upgrade():
    # Rename metadata column in tasks table to task_metadata
    op.alter_column('tasks', 'metadata', new_column_name='task_metadata')
    
    # Rename metadata column in task_logs table to task_metadata
    op.alter_column('task_logs', 'metadata', new_column_name='task_metadata')


def downgrade():
    # Reverse the changes
    op.alter_column('tasks', 'task_metadata', new_column_name='metadata')
    op.alter_column('task_logs', 'task_metadata', new_column_name='metadata')
