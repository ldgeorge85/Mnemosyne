"""change_base_model_id_to_uuid

Revision ID: ebd64975b648
Revises: abb0da5fc7a9
Create Date: 2025-06-17 00:36:06.034532+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "ebd64975b648"
down_revision: Union[str, None] = "abb0da5fc7a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
transactional = False


# Define the schema structure to manage dependencies
SCHEMA_RELATIONSHIPS = {
    'tables_with_uuid_pk': [
        "users", "tasks", "task_logs", "task_schedules", "conversations",
        "messages", "memories", "memory_chunks", "agents", "agent_links",
        "agent_logs", "memory_reflections",
    ],
    'foreign_keys': [
        {'table': 'tasks', 'column': 'user_id', 'ref_table': 'users', 'name': 'tasks_user_id_fkey'},
        {'table': 'tasks', 'column': 'parent_id', 'ref_table': 'tasks', 'name': 'tasks_parent_id_fkey'},
        {'table': 'tasks', 'column': 'agent_id', 'ref_table': 'agents', 'name': 'tasks_agent_id_fkey'},
        {'table': 'task_logs', 'column': 'task_id', 'ref_table': 'tasks', 'name': 'task_logs_task_id_fkey'},
        {'table': 'task_schedules', 'column': 'task_id', 'ref_table': 'tasks', 'name': 'task_schedules_task_id_fkey'},
        {'table': 'messages', 'column': 'conversation_id', 'ref_table': 'conversations', 'name': 'messages_conversation_id_fkey'},
        {'table': 'messages', 'column': 'user_id', 'ref_table': 'users', 'name': 'messages_user_id_fkey'},
        {'table': 'memory_chunks', 'column': 'memory_id', 'ref_table': 'memories', 'name': 'memory_chunks_memory_id_fkey'},
        {'table': 'agent_links', 'column': 'source_agent_id', 'ref_table': 'agents', 'name': 'agent_links_source_agent_id_fkey'},
        {'table': 'agent_links', 'column': 'target_agent_id', 'ref_table': 'agents', 'name': 'agent_links_target_agent_id_fkey'},
        {'table': 'agent_logs', 'column': 'agent_id', 'ref_table': 'agents', 'name': 'agent_logs_agent_id_fkey'},
        {'table': 'memory_reflections', 'column': 'memory_id', 'ref_table': 'memories', 'name': 'memory_reflections_memory_id_fkey'},
        {'table': 'memory_reflections', 'column': 'agent_id', 'ref_table': 'agents', 'name': 'memory_reflections_agent_id_fkey'},
    ]
}

def upgrade() -> None:
    """Upgrade schema by changing all ID fields from String to UUID."""
    # 1. Drop all foreign key constraints using raw SQL with IF EXISTS
    for fk in SCHEMA_RELATIONSHIPS['foreign_keys']:
        op.execute(f"ALTER TABLE {fk['table']} DROP CONSTRAINT IF EXISTS {fk['name']}")

    # 2. Alter all primary key 'id' columns
    for table_name in SCHEMA_RELATIONSHIPS['tables_with_uuid_pk']:
        op.alter_column(
            table_name, 'id',
            existing_type=sa.String(length=36),
            type_=postgresql.UUID(as_uuid=True),
            existing_nullable=False,
            postgresql_using='id::uuid',
            server_default=sa.text('gen_random_uuid()')
        )

    # 3. Alter all foreign key columns
    for fk in SCHEMA_RELATIONSHIPS['foreign_keys']:
        op.alter_column(
            fk['table'], fk['column'],
            existing_type=sa.String(length=36),
            type_=postgresql.UUID(as_uuid=True),
            postgresql_using=f"{fk['column']}::uuid"
        )

    # 4. Re-create all foreign key constraints
    for fk in SCHEMA_RELATIONSHIPS['foreign_keys']:
        op.create_foreign_key(
            fk['name'],
            fk['table'], fk['ref_table'],
            [fk['column']], ['id']
        )

def downgrade() -> None:
    """Downgrade schema by changing UUID fields back to String."""
    # 1. Drop all foreign key constraints using raw SQL with IF EXISTS
    for fk in SCHEMA_RELATIONSHIPS['foreign_keys']:
        op.execute(f"ALTER TABLE {fk['table']} DROP CONSTRAINT IF EXISTS {fk['name']}")

    # 2. Alter all foreign key columns back to String
    for fk in SCHEMA_RELATIONSHIPS['foreign_keys']:
        op.alter_column(
            fk['table'], fk['column'],
            existing_type=postgresql.UUID(as_uuid=True),
            type_=sa.String(length=36),
            postgresql_using=f"{fk['column']}::text"
        )

    # 3. Alter all primary key 'id' columns back to String
    for table_name in SCHEMA_RELATIONSHIPS['tables_with_uuid_pk']:
        op.alter_column(
            table_name, 'id',
            existing_type=postgresql.UUID(as_uuid=True),
            type_=sa.String(length=36),
            server_default=None
        )

    # 4. Re-create all foreign key constraints
    for fk in SCHEMA_RELATIONSHIPS['foreign_keys']:
        op.create_foreign_key(
            fk['name'],
            fk['table'], fk['ref_table'],
            [fk['column']], ['id']
        )

