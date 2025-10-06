"""
Auto-fix "Multiple head revisions" by generating a merge revision.
- Ensures alembic/script.py.mako exists (restores a standard template if missing)
- Creates a merge revision that unifies all current heads
Usage:
    python -m scripts.fix_merge_heads
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from alembic.config import Config
from alembic import command

TEMPLATE_CONTENT = dedent("""\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
\"\"\"

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision) if down_revision else "None"}
branch_labels = ${repr(branch_labels) if branch_labels else "None"}
depends_on = ${repr(depends_on) if depends_on else "None"}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
""")

def ensure_script_template(script_location: Path) -> None:
    """
    Make sure alembic/script.py.mako exists.
    """
    target = script_location / "script.py.mako"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(TEMPLATE_CONTENT, encoding="utf-8")
        print(f"[fix_merge_heads] Restored missing template: {target}")
    else:
        print(f"[fix_merge_heads] Template OK: {target}")

def main() -> int:
    cfg = Config("alembic.ini")
    # Resolve the alembic script_location (e.g., "alembic")
    script_location = Path(cfg.get_main_option("script_location") or "alembic").resolve()
    ensure_script_template(script_location)

    # Collect current heads
    from alembic.script import ScriptDirectory
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    if len(heads) <= 1:
        print("[fix_merge_heads] No merge needed. Current heads:", ", ".join(heads) if heads else "(none)")
        return 0

    print(f"[fix_merge_heads] Found multiple heads: {', '.join(heads)}")
    print("[fix_merge_heads] Creating merge revision to unify these heads...")
    # Create a merge revision (does not upgrade automatically)
    command.merge(cfg, revisions=heads, message="merge heads (auto-generated)")
    print("[fix_merge_heads] Merge revision generated. Now run: alembic upgrade head")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
