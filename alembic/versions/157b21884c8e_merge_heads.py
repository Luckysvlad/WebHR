"""merge heads

Revision ID: 157b21884c8e
Revises: 20251005_domain_init, 5150fc890f5b
Create Date: 2025-10-05 22:05:16.276906
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '157b21884c8e'
down_revision = ('20251005_domain_init', '5150fc890f5b')
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
