"""Add users.created_at (idempotent, SQLite-safe)

Revision ID: 20251006_add_users_created_at
Revises: 20251005_rbac_admin_extras
Create Date: 2025-10-06
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251006_add_users_created_at"
down_revision = "20251005_rbac_admin_extras"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("users")}
    dialect = bind.dialect.name

    if "created_at" not in cols:
        # В SQLite НЕЛЬЗЯ добавлять колонку с DEFAULT CURRENT_TIMESTAMP
        # Поэтому добавляем без server_default
        col = sa.Column("created_at", sa.DateTime(), nullable=True)
        op.add_column("users", col)

        # Заполняем существующие строки текущим временем на стороне БД
        op.execute(sa.text("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))

        # Делать NOT NULL/DEFAULT задним числом в SQLite — это пересоздание таблицы.
        # Оставляем nullable=True, а дефолт дадим на уровне ORM (client-side).


def downgrade() -> None:
    # Удаляем колонку там, где это возможно
    bind = op.get_bind()
    dialect = bind.dialect.name
    try:
        if dialect == "sqlite":
            # В старых SQLite DROP COLUMN может быть недоступен — просто игнорируем
            op.execute(sa.text("ALTER TABLE users DROP COLUMN created_at"))
        else:
            op.drop_column("users", "created_at")
    except Exception:
        pass
