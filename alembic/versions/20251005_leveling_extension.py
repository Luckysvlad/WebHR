"""Leveling extension (safe + idempotent for SQLite)

Revision ID: leveling_extension_20251005
Revises: init
Create Date: 2025-10-05 12:00:00
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = 'leveling_extension_20251005'
down_revision = 'init'
branch_labels = None
depends_on = None

def _table_exists(conn, table: str) -> bool:
    res = conn.execute(sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"), {"t": table}).fetchone()
    return bool(res)

def _has_column(conn, table: str, col: str) -> bool:
    info = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
    return any(row[1] == col for row in info)

def upgrade() -> None:
    conn = op.get_bind()
    table = "employees"
    if _table_exists(conn, table):
        if not _has_column(conn, table, "hired_at"):
            op.add_column(table, sa.Column("hired_at", sa.Date(), nullable=True))
        if not _has_column(conn, table, "level"):
            op.add_column(table, sa.Column("level", sa.Integer(), nullable=True))
        if not _has_column(conn, table, "points"):
            op.add_column(table, sa.Column("points", sa.Integer(), nullable=True, server_default="0"))
            conn.exec_driver_sql(f"UPDATE {table} SET points=0 WHERE points IS NULL")
        if not _has_column(conn, table, "last_reviewed_at"):
            op.add_column(table, sa.Column("last_reviewed_at", sa.DateTime(), nullable=True))

def downgrade() -> None:
    # no-op for SQLite for simplicity
    pass
