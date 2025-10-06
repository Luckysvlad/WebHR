WebHR Alembic patch
-------------------
Purpose:
  - Fix "Multiple head revisions" error by making the fix migration depend on 'init_auth_20251006'.
  - Add 'roles.description' column if it's missing to fix runtime error "no such column: roles.description".

Installation:
  1) Unzip into your project root so the file lands at:
     alembic/versions/20251006_fix_roles_description.py
  2) Run:
     alembic upgrade head
  3) Restart the app:
     uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Notes:
  - If you still see "Multiple head revisions", run `alembic heads -v` and ensure
    there is only one head. If there are more, create a merge revision:
      alembic merge -m "merge heads" <rev1> <rev2> [<rev3> ...]
