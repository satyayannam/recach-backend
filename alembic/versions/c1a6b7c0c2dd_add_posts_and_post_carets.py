"""add posts and post carets

Revision ID: c1a6b7c0c2dd
Revises: f23d9e0b9a2b
Create Date: 2026-01-15

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "c1a6b7c0c2dd"
down_revision = "f23d9e0b9a2b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    if "posts" not in tables:
        op.create_table(
            "posts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("type", sa.String(length=32), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        )
    post_indexes = {idx["name"] for idx in inspector.get_indexes("posts")}
    if "ix_posts_user_id" not in post_indexes:
        op.create_index("ix_posts_user_id", "posts", ["user_id"])
    if "ix_posts_created_at" not in post_indexes:
        op.create_index("ix_posts_created_at", "posts", ["created_at"])

    if "post_carets" not in tables:
        op.create_table(
            "post_carets",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        )
    caret_indexes = {idx["name"] for idx in inspector.get_indexes("post_carets")}
    if "ix_post_carets_post_id" not in caret_indexes:
        op.create_index("ix_post_carets_post_id", "post_carets", ["post_id"])
    if "ix_post_carets_user_id" not in caret_indexes:
        op.create_index("ix_post_carets_user_id", "post_carets", ["user_id"])
    caret_constraints = {
        uc["name"]
        for uc in inspector.get_unique_constraints("post_carets")
    }
    if "uq_post_caret" not in caret_constraints:
        op.create_unique_constraint("uq_post_caret", "post_carets", ["post_id", "user_id"])


def downgrade() -> None:
    op.drop_constraint("uq_post_caret", "post_carets", type_="unique")
    op.drop_index("ix_post_carets_user_id", table_name="post_carets")
    op.drop_index("ix_post_carets_post_id", table_name="post_carets")
    op.drop_table("post_carets")
    op.drop_index("ix_posts_created_at", table_name="posts")
    op.drop_index("ix_posts_user_id", table_name="posts")
    op.drop_table("posts")
