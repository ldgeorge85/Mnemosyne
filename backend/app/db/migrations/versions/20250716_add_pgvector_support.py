"""Add pgvector support for embeddings

Revision ID: add_pgvector_support
Revises: 
Create Date: 2025-07-16

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = 'add_pgvector_support'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add pgvector extension and vector columns."""
    # Create pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Add vector columns to memories table
    # Note: We already have ARRAY(Float) columns, but we'll add proper vector columns
    op.add_column('memories', 
        sa.Column('embedding_vector', Vector(1024), nullable=True)
    )
    
    # Add vector columns to memory_chunks table
    op.add_column('memory_chunks',
        sa.Column('embedding_vector', Vector(1024), nullable=True)
    )
    
    # Create indexes for vector similarity search
    # Using ivfflat index for better performance on large datasets
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_memories_embedding_vector 
        ON memories USING ivfflat (embedding_vector vector_cosine_ops)
        WITH (lists = 100)
    ''')
    
    op.execute('''
        CREATE INDEX IF NOT EXISTS idx_memory_chunks_embedding_vector 
        ON memory_chunks USING ivfflat (embedding_vector vector_cosine_ops)
        WITH (lists = 100)
    ''')
    
    # Add dimension column to track embedding size
    op.add_column('memories',
        sa.Column('embedding_dimension', sa.Integer(), nullable=True)
    )
    
    op.add_column('memory_chunks',
        sa.Column('embedding_dimension', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Remove pgvector support."""
    # Remove indexes
    op.execute('DROP INDEX IF EXISTS idx_memories_embedding_vector')
    op.execute('DROP INDEX IF EXISTS idx_memory_chunks_embedding_vector')
    
    # Remove columns
    op.drop_column('memories', 'embedding_vector')
    op.drop_column('memories', 'embedding_dimension')
    op.drop_column('memory_chunks', 'embedding_vector')
    op.drop_column('memory_chunks', 'embedding_dimension')
    
    # Note: We don't remove the extension as other tables might use it