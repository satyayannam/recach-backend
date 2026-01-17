"""add courses contact requests and inbox

Revision ID: e5a9c7b4d2f1
Revises: d2b9f2f4b5c1
Create Date: 2026-01-17
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "e5a9c7b4d2f1"
down_revision = "d2b9f2f4b5c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("course_name", sa.Text(), nullable=False),
        sa.Column("course_number", sa.String(length=50), nullable=False),
        sa.Column("professor", sa.Text(), nullable=True),
        sa.Column("grade", sa.String(length=20), nullable=False),
        sa.Column("program_level", sa.String(length=20), nullable=False),
        sa.Column("term", sa.String(length=40), nullable=True),
        sa.Column("visibility", sa.String(length=20), nullable=False, server_default="PUBLIC"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_user_courses_user_id", "user_courses", ["user_id"])
    op.create_index("ix_user_courses_course_number", "user_courses", ["course_number"])
    op.create_index("ix_user_courses_course_name", "user_courses", ["course_name"])
    op.create_index(
        "ix_user_courses_course_lookup",
        "user_courses",
        ["course_number", "course_name"],
    )

    op.create_table(
        "contact_methods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_contact_methods_user_id", "contact_methods", ["user_id"], unique=True)

    op.create_table(
        "contact_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("target_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_courses.id"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_contact_requests_requester_id", "contact_requests", ["requester_id"])
    op.create_index("ix_contact_requests_target_id", "contact_requests", ["target_id"])
    op.create_index("ix_contact_requests_course_id", "contact_requests", ["course_id"])
    op.create_index("ix_contact_requests_status", "contact_requests", ["status"])

    op.create_table(
        "inbox_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_inbox_items_user_id", "inbox_items", ["user_id"])
    op.create_index("ix_inbox_items_type", "inbox_items", ["type"])
    op.create_index("ix_inbox_items_status", "inbox_items", ["status"])


def downgrade() -> None:
    op.drop_index("ix_inbox_items_status", table_name="inbox_items")
    op.drop_index("ix_inbox_items_type", table_name="inbox_items")
    op.drop_index("ix_inbox_items_user_id", table_name="inbox_items")
    op.drop_table("inbox_items")

    op.drop_index("ix_contact_requests_status", table_name="contact_requests")
    op.drop_index("ix_contact_requests_course_id", table_name="contact_requests")
    op.drop_index("ix_contact_requests_target_id", table_name="contact_requests")
    op.drop_index("ix_contact_requests_requester_id", table_name="contact_requests")
    op.drop_table("contact_requests")

    op.drop_index("ix_contact_methods_user_id", table_name="contact_methods")
    op.drop_table("contact_methods")

    op.drop_index("ix_user_courses_course_lookup", table_name="user_courses")
    op.drop_index("ix_user_courses_course_name", table_name="user_courses")
    op.drop_index("ix_user_courses_course_number", table_name="user_courses")
    op.drop_index("ix_user_courses_user_id", table_name="user_courses")
    op.drop_table("user_courses")
