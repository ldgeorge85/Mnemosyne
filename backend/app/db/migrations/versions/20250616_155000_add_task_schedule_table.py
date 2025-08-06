"""
Add task schedule table migration.

Revision ID: 20250616_155000
Revises: 20250616_135000
Create Date: 2025-06-16 15:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250616_155000'
down_revision = '20250616_135000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create task_schedules table."""
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table('task_schedules'):
        op.create_table(
            'task_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('due_time', sa.DateTime(), nullable=False),
        sa.Column('timezone', sa.String(), nullable=False, server_default='UTC'),
        sa.Column('is_all_day', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('recurrence_pattern', sa.String(), nullable=True),
        sa.Column('recurrence_count', sa.Integer(), nullable=True),
        sa.Column('recurrence_end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
        # Create indexes for performance only if the table was created
        op.create_index(op.f('ix_task_schedules_task_id'), 'task_schedules', ['task_id'], unique=True)
        op.create_index(op.f('ix_task_schedules_due_time'), 'task_schedules', ['due_time'], unique=False)
        op.create_index(op.f('ix_task_schedules_start_time'), 'task_schedules', ['start_time'], unique=False)
    else:
        print("Table 'task_schedules' already exists, skipping creation and index creation.")


def downgrade() -> None:
    """Drop task_schedules table."""
    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table('task_schedules'):
        # Attempt to drop indexes, op.f() generates consistent names
        # Assuming op.drop_index is safe if index doesn't exist or use try-except
        try:
            op.drop_index(op.f('ix_task_schedules_start_time'), table_name='task_schedules')
            op.drop_index(op.f('ix_task_schedules_due_time'), table_name='task_schedules')
            op.drop_index(op.f('ix_task_schedules_task_id'), table_name='task_schedules')
        except Exception as e:
            print(f"Skipping index dropping for task_schedules due to: {e}")
        op.drop_table('task_schedules')
    else:
        print("Table 'task_schedules' does not exist, skipping drop.")
