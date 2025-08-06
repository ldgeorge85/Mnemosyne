"""
Add User Authentication Tables

Revision ID: 20250611_140000
Revises: 20250606_154252_initial_db_schema_with_all_models
Create Date: 2025-06-11 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250611_140000'
down_revision: Union[str, None] = 'f9075d69670e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create user authentication tables:
    - users: User accounts for authentication
    - api_keys: API keys for service authentication
    - user_sessions: User sessions for refresh tokens
    """
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('key_hash', sa.String(), nullable=False),
        sa.Column('prefix', sa.String(8), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_token_hash', sa.String(), nullable=False),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    
    # Add foreign key to memories table for user_id if it exists
    # This is to associate memories with users
    tables = sa.inspect(op.get_bind()).get_table_names()
    if 'memories' in tables:
        # Check if user_id column already exists
        columns = [col['name'] for col in sa.inspect(op.get_bind()).get_columns('memories')]
        if 'user_id' not in columns:
            op.add_column('memories', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
            op.create_foreign_key(
                'fk_memories_user_id', 'memories', 'users',
                ['user_id'], ['id']
            )


def downgrade() -> None:
    """
    Drop user authentication tables in reverse order.
    """
    # Remove foreign key from memories table if it exists
    tables = sa.inspect(op.get_bind()).get_table_names()
    if 'memories' in tables:
        # Check if user_id column exists
        columns = [col['name'] for col in sa.inspect(op.get_bind()).get_columns('memories')]
        if 'user_id' in columns:
            op.drop_constraint('fk_memories_user_id', 'memories', type_='foreignkey')
            op.drop_column('memories', 'user_id')
    
    # Drop tables in reverse order
    op.drop_table('user_sessions')
    op.drop_table('api_keys')
    op.drop_table('users')
