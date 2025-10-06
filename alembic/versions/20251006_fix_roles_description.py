# ### Auto-generated patch to linearize Alembic history and add roles.description ###
# This revision depends on 'init_auth_20251006' to avoid multiple heads.
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_roles_description_20251006'
down_revision = 'init_auth_20251006'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Ensure table exists
    tables = insp.get_table_names()
    if 'roles' not in tables:
        # Nothing to do if roles table doesn't exist (should exist after init_auth_20251006)
        return

    # Add column if missing
    existing_cols = [c['name'] for c in insp.get_columns('roles')]
    if 'description' not in existing_cols:
        op.add_column('roles', sa.Column('description', sa.String(length=255), nullable=True))

def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if 'roles' in insp.get_table_names():
        existing_cols = [c['name'] for c in insp.get_columns('roles')]
        if 'description' in existing_cols:
            op.drop_column('roles', 'description')
