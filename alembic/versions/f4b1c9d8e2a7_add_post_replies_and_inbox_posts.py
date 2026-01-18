"""add post replies and inbox posts

Revision ID: f4b1c9d8e2a7
Revises: e5a9c7b4d2f1
Create Date: 2026-01-17
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f4b1c9d8e2a7"
down_revision = "e5a9c7b4d2f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    reply_type_enum = sa.Enum(
        "validate", "context", "impact", "clarify", "challenge", name="post_reply_type"
    )
    reaction_enum = sa.Enum(
        "thanks", "helpful", "noted", "appreciate", name="post_reply_reaction"
    )
    bind = op.get_bind()
    reply_type_enum.create(bind, checkfirst=True)
    reaction_enum.create(bind, checkfirst=True)

    op.create_table(
        "post_replies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", reply_type_enum, nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_post_replies_post_id", "post_replies", ["post_id"])
    op.create_index("ix_post_replies_owner_id", "post_replies", ["owner_id"])
    op.create_index("ix_post_replies_created_at", "post_replies", ["created_at"])

    op.create_table(
        "post_reply_carets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reply_id", sa.Integer(), sa.ForeignKey("post_replies.id"), nullable=False),
        sa.Column("post_owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_given", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_post_reply_carets_reply_id", "post_reply_carets", ["reply_id"], unique=True)
    op.create_index("ix_post_reply_carets_owner_id", "post_reply_carets", ["post_owner_id"])

    op.create_table(
        "post_reply_owner_reaction",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reply_id", sa.Integer(), sa.ForeignKey("post_replies.id"), nullable=False),
        sa.Column("post_owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reaction", reaction_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "ix_post_reply_owner_reaction_reply_id",
        "post_reply_owner_reaction",
        ["reply_id"],
        unique=True,
    )
    op.create_index(
        "ix_post_reply_owner_reaction_owner_id",
        "post_reply_owner_reaction",
        ["post_owner_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_post_reply_owner_reaction_owner_id", table_name="post_reply_owner_reaction")
    op.drop_index("ix_post_reply_owner_reaction_reply_id", table_name="post_reply_owner_reaction")
    op.drop_table("post_reply_owner_reaction")

    op.drop_index("ix_post_reply_carets_owner_id", table_name="post_reply_carets")
    op.drop_index("ix_post_reply_carets_reply_id", table_name="post_reply_carets")
    op.drop_table("post_reply_carets")

    op.drop_index("ix_post_replies_created_at", table_name="post_replies")
    op.drop_index("ix_post_replies_owner_id", table_name="post_replies")
    op.drop_index("ix_post_replies_post_id", table_name="post_replies")
    op.drop_table("post_replies")

    bind = op.get_bind()
    sa.Enum(name="post_reply_reaction").drop(bind, checkfirst=True)
    sa.Enum(name="post_reply_type").drop(bind, checkfirst=True)
