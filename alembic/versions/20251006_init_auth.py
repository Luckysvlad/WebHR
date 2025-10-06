"""init auth tables (users, roles, permissions) and link tables

This revision fixes multiple-head issue by making this migration depend on
`leveling_extension_20251005` (the other head seen in your logs).

- Safe for SQLite: checks for table existence with Inspector before creating.
- Idempotent: if a table already exists, it is skipped.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# --- Alembic identifiers ---
revision: str = 'init_auth_20251006'
down_revision: Union[str, None] = 'leveling_extension_20251005'  # <<< KEY FIX
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(conn, name: str) -> bool:
    insp = sa.inspect(conn)
    return name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # users
    if not _has_table(bind, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("username", sa.String(255), nullable=False, unique=True, index=True),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
            sa.Column("is_superuser", sa.Boolean, nullable=False, server_default=sa.text("0")),
        )

    # roles
    if not _has_table(bind, "roles"):
        op.create_table(
            "roles",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("code", sa.String(255), nullable=False, unique=True, index=True),
            sa.Column("name", sa.String(255), nullable=False),
        )

    # permissions
    if not _has_table(bind, "permissions"):
        op.create_table(
            "permissions",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("code", sa.String(255), nullable=False, unique=True, index=True),
            sa.Column("name", sa.String(255), nullable=False),
        )

    # user_roles (m2m)
    if not _has_table(bind, "user_roles"):
        op.create_table(
            "user_roles",
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        )

    # role_permissions (m2m)
    if not _has_table(bind, "role_permissions"):
        op.create_table(
            "role_permissions",
            sa.Column("role_id", sa.Integer, sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("permission_id", sa.Integer, sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
        )


def downgrade() -> None:
    # Keep downgrades defensive (drop only if exists)
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing = set(insp.get_table_names())

    for t in ["role_permissions", "user_roles", "permissions", "roles", "users"]:
        if t in existing:
            op.drop_table(t)