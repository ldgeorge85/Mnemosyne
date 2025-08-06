"""Merge pgvector and uuid branches

Revision ID: df5a833da6b9
Revises: ebd64975b648, add_pgvector_support
Create Date: 2025-07-18 18:44:59.009260+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df5a833da6b9'
down_revision: Union[str, None] = ('ebd64975b648', 'add_pgvector_support')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
