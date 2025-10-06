# Patch: fix Alembic multiple heads + missing script.py.mako

This patch adds:
- `alembic/script.py.mako` (standard Alembic revision template)
- `scripts/fix_merge_heads.py` which auto-restores the template and creates a merge revision for current heads

## How to use
1) Copy the contents of this archive into the **root of your project** (where `alembic.ini` lives).
   - Final paths should be:
     - `alembic/script.py.mako`
     - `scripts/fix_merge_heads.py`

2) Run:
   ```bash
   python -m scripts.fix_merge_heads
   alembic upgrade head
   ```

If you still see "Multiple head revisions..." just run the two commands above again
(the first creates a merge revision, the second applies it).
