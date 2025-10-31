"""add_key_storage_and_signatures

Revision ID: 69c253fe9879
Revises: 007b16b7f352
Create Date: 2025-10-31 01:46:12.932261+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69c253fe9879'
down_revision: Union[str, None] = '007b16b7f352'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add key storage fields to users table
    op.add_column('users', sa.Column('public_key', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('encrypted_private_key', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('key_algorithm', sa.String(50), server_default='Ed25519', nullable=True))
    op.add_column('users', sa.Column('key_created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('key_rotation_count', sa.Integer(), server_default='0', nullable=True))

    # Add signature fields to negotiation_messages table
    op.add_column('negotiation_messages', sa.Column('signature_ed25519', sa.Text(), nullable=True))
    op.add_column('negotiation_messages', sa.Column('signature_verified', sa.Boolean(), server_default='false', nullable=True))

    # Add signature fields to receipts table
    op.add_column('receipts', sa.Column('signature', sa.Text(), nullable=True))
    op.add_column('receipts', sa.Column('signature_algorithm', sa.String(50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove signature fields from receipts
    op.drop_column('receipts', 'signature_algorithm')
    op.drop_column('receipts', 'signature')

    # Remove signature fields from negotiation_messages
    op.drop_column('negotiation_messages', 'signature_verified')
    op.drop_column('negotiation_messages', 'signature_ed25519')

    # Remove key storage fields from users
    op.drop_column('users', 'key_rotation_count')
    op.drop_column('users', 'key_created_at')
    op.drop_column('users', 'key_algorithm')
    op.drop_column('users', 'encrypted_private_key')
    op.drop_column('users', 'public_key')
