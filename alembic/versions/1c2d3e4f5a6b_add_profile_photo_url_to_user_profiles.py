"""add profile_photo_url to user_profiles

Revision ID: 1c2d3e4f5a6b
Revises: 9e90accb8222
Create Date: 2026-01-10

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "1c2d3e4f5a6b"
down_revision = "9e90accb8222"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("profile_photo_url", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "profile_photo_url")
