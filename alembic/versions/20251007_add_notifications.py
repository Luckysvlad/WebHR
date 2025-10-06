"""add notifications table (safe for SQLite)

Revision ID: add_notifications_20251007
Revises: init_auth_20251006
Create Date: 2025-10-07

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_notifications_20251007"
down_revision = "init_auth_20251006"
branch_labels = None
depends_on = None


def _has_table(bind, name: str) -> bool:
    insp = sa.inspect(bind)
    return name in insp.get_table_names()


def _has_column(bind, table: str, col: str) -> bool:
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns(table)}
    return col in cols


def upgrade() -> None:
    bind = op.get_bind()

    if not _has_table(bind, "notifications"):
        op.create_table(
            "notifications",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
    else:
        # make sure all expected columns exist (idempotent / forward-fix if table was partial)
        for name, col in [
            ("user_id", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)),
            ("message", sa.Column("message", sa.Text(), nullable=False)),
            ("is_read", sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("0"))),
            ("created_at", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"))),
        ]:
            if not _has_column(bind, "notifications", name):
                op.add_column("notifications", col)


def downgrade() -> None:
    bind = op.get_bind()
    if _has_table(bind, "notifications"):
        op.drop_table("notifications")
