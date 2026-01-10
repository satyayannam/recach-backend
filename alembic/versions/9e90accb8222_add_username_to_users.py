"""add username to users

Revision ID: 9e90accb8222
Revises: <PUT_YOUR_PREVIOUS_REVISION_ID_HERE>
Create Date: 2026-01-07

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
import re


# revision identifiers, used by Alembic.
revision = "9e90accb8222"
down_revision = "e4cc50ddcbeb"
branch_labels = None
depends_on = None


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._]+", "", s)
    s = re.sub(r"\.+", ".", s).strip(".")
    if len(s) < 3:
        s = "user"
    return s[:32]


def upgrade() -> None:
    # 1) add column nullable first
    op.add_column("users", sa.Column("username", sa.String(length=32), nullable=True))

    bind = op.get_bind()

    users = bind.execute(sa.text("SELECT id, full_name, email FROM users")).fetchall()
    existing = set(
        r[0]
        for r in bind.execute(
            sa.text("SELECT username FROM users WHERE username IS NOT NULL")
        ).fetchall()
    )

    for (user_id, full_name, email) in users:
        base = _slugify(full_name) or _slugify((email or "").split("@")[0])

        candidate = base
        n = 2
        while candidate in existing:
            suffix = str(n)
            candidate = base[: (32 - len(suffix))] + suffix
            n += 1

        existing.add(candidate)

        bind.execute(
            sa.text("UPDATE users SET username = :u WHERE id = :id"),
            {"u": candidate, "id": user_id},
        )

    # 2) enforce not-null + constraints
    op.alter_column("users", "username", existing_type=sa.String(length=32), nullable=False)
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.create_index("ix_users_username", "users", ["username"])


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.drop_column("users", "username")
