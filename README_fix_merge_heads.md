# Patch: fix multiple Alembic heads

This patch adds a helper script that automatically **merges multiple Alembic heads into a single head**.
It is safe and does not modify your models — it only creates a *merge revision* in `alembic/versions`.

## Files included
- `scripts/fix_merge_heads.py`

## How to use

1. Copy the `scripts/fix_merge_heads.py` file into your repository at `scripts/fix_merge_heads.py`
   (next to your other helper scripts).
2. From the **project root** (where `alembic.ini` is located), run:
   ```bash
   python -m scripts.fix_merge_heads
   ```
   If multiple heads exist, the script will create a merge revision automatically.
3. Then apply migrations normally:
   ```bash
   alembic upgrade head
   ```

## Notes
- If you still see "Multiple head revisions" after this, run again to ensure the newly created merge
  revision is included; then re-run `alembic upgrade head`.
- If you want to inspect heads manually:
  ```bash
  alembic heads -v
  ```
  and you can also create a merge by hand:
  ```bash
  alembic merge -m "merge heads" <rev1> <rev2> [...]
  ```
