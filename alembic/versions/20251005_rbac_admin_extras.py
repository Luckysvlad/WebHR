"""RBAC admin extras: is_system roles + unique indexes
Revision ID: 20251005_rbac_admin_extras
Revises: 157b21884c8e
Create Date: 2025-10-05
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20251005_rbac_admin_extras"
down_revision: Union[str, None] = "157b21884c8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _has_column(inspector, table: str, column: str) -> bool:
    try:
        return column in [c["name"] for c in inspector.get_columns(table)]
    except Exception:
        return False

def _has_index(inspector, table: str, name: str) -> bool:
    try:
        return any(ix.get("name") == name for ix in inspector.get_indexes(table))
    except Exception:
        return False

def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if insp.has_table("roles") and not _has_column(insp, "roles", "is_system"):
        op.add_column("roles", sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("0")))
        with op.batch_alter_table("roles") as batch_op:
            batch_op.alter_column("is_system", server_default=None)

    if insp.has_table("permissions"):
        try:
            op.create_unique_constraint("uq_permissions_code", "permissions", ["code"])
        except Exception:
            pass

    if insp.has_table("roles"):
        try:
            op.create_unique_constraint("uq_roles_name", "roles", ["name"])
        except Exception:
            pass

def downgrade() -> None:
    pass
