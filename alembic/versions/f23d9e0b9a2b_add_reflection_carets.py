"""add reflection carets

Revision ID: f23d9e0b9a2b
Revises: 38467ee5a2ca
Create Date: 2026-01-15

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "f23d9e0b9a2b"
down_revision = "38467ee5a2ca"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    if "reflection_carets" not in tables:
        op.create_table(
            "reflection_carets",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reflection_id", sa.Integer(), sa.ForeignKey("reflections.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        )
    indexes = {idx["name"] for idx in inspector.get_indexes("reflection_carets")}
    if "ix_reflection_carets_reflection_id" not in indexes:
        op.create_index("ix_reflection_carets_reflection_id", "reflection_carets", ["reflection_id"])
    if "ix_reflection_carets_user_id" not in indexes:
        op.create_index("ix_reflection_carets_user_id", "reflection_carets", ["user_id"])
    constraints = {
        uc["name"]
        for uc in inspector.get_unique_constraints("reflection_carets")
    }
    if "uq_reflection_caret" not in constraints:
        op.create_unique_constraint(
            "uq_reflection_caret", "reflection_carets", ["reflection_id", "user_id"]
        )


def downgrade() -> None:
    op.drop_constraint("uq_reflection_caret", "reflection_carets", type_="unique")
    op.drop_index("ix_reflection_carets_user_id", table_name="reflection_carets")
    op.drop_index("ix_reflection_carets_reflection_id", table_name="reflection_carets")
    op.drop_table("reflection_carets")
