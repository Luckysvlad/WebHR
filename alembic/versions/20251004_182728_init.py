"""init

Revision ID: init
Revises: 
Create Date: 2025-10-04 18:27:28

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # NO-OP:
    # Ранее тут вызывался Base.metadata.create_all(bind=engine),
    # что тянуло приложенческий engine из .env и ломало миграции,
    # пытаясь подключиться к MySQL. Миграции должны работать
    # через Alembic-context (op.*). Схему создают последующие
    # ревизии (safe-create).
    pass

def downgrade() -> None:
    # NO-OP: не трогаем схему откатом здесь
    pass
