"""merge_agent_task_auth_branches

Revision ID: abb0da5fc7a9
Revises: bce39c61c978, 20250616_165000
Create Date: 2025-06-17 00:36:02.721938+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "abb0da5fc7a9"
down_revision: Union[str, None] = ("bce39c61c978", "20250616_165000")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
