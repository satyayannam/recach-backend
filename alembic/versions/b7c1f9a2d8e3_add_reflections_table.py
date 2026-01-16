"""add reflections table

Revision ID: b7c1f9a2d8e3
Revises: 9e90accb8222
Create Date: 2026-01-12

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7c1f9a2d8e3"
down_revision = "9e90accb8222"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reflections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_reflections_user_id", "reflections", ["user_id"])
    op.create_index("ix_reflections_created_at", "reflections", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_reflections_created_at", table_name="reflections")
    op.drop_index("ix_reflections_user_id", table_name="reflections")
    op.drop_table("reflections")
