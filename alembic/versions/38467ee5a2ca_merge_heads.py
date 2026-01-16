"""merge heads

Revision ID: 38467ee5a2ca
Revises: 1c2d3e4f5a6b, b7c1f9a2d8e3
Create Date: 2026-01-15 18:14:48.965767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38467ee5a2ca'
down_revision: Union[str, Sequence[str], None] = ('1c2d3e4f5a6b', 'b7c1f9a2d8e3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
