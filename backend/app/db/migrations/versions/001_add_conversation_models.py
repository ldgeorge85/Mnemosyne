"""
Add conversation models

Revision ID: 001
Revises: 
Create Date: 2025-05-29

This migration adds the conversation and message models to the database.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade database schema to include conversation and message tables.
    """
    # Create conversation table
    op.create_table(
        'conversation',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create index on user_id for faster lookups
    op.create_index('ix_conversation_user_id', 'conversation', ['user_id'])
    
    # Create message table
    op.create_table(
        'message',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('conversation_id', sa.String(36), sa.ForeignKey('conversation.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('role', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create indexes for message table
    op.create_index('ix_message_conversation_id', 'message', ['conversation_id'])
    op.create_index('ix_message_role', 'message', ['role'])


def downgrade():
    """
    Downgrade database schema by removing conversation and message tables.
    """
    # Drop tables in reverse order
    op.drop_table('message')
    op.drop_table('conversation')
