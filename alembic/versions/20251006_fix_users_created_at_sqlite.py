"""Ensure users.created_at exists (SQLite-safe)

Revision ID: 20251006_fix_users_created_at_sqlite
Revises: 20251006_add_users_created_at
Create Date: 2025-10-06
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# ревизии
revision = "20251006_fix_users_created_at_sqlite"
down_revision = "20251006_add_users_created_at"  # последняя у вас
branch_labels = None
depends_on = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table_name)]
    return column_name in cols


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    # если таблицы нет — выходим (на ранних стендах)
    insp = sa.inspect(bind)
    if "users" not in insp.get_table_names():
        return

    if not _column_exists(bind, "users", "created_at"):
        # SQLite не умеет ADD COLUMN с нестатичным DEFAULT
        op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))

        if dialect == "sqlite":
            # заполняем текущим временем
            bind.execute(sa.text("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL"))
        else:
            bind.execute(sa.text("UPDATE users SET created_at = NOW() WHERE created_at IS NULL"))

        # делаем NOT NULL
        op.alter_column("users", "created_at", existing_type=sa.DateTime(), nullable=False)


def downgrade():
    bind = op.get_bind()
    if _column_exists(bind, "users", "created_at"):
        op.drop_column("users", "created_at")
