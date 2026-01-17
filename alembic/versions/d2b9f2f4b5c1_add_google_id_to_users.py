"""add google id to users

Revision ID: d2b9f2f4b5c1
Revises: c1a6b7c0c2dd
Create Date: 2026-01-16

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d2b9f2f4b5c1"
down_revision = "c1a6b7c0c2dd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_id", sa.String(length=64), nullable=True))
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "google_id")
