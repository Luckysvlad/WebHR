PATCH: fix import error for Notification model and add notifications table migration

What’s included
---------------
1) app/core/models.py
   - Adds a minimal Notification SQLAlchemy model and re-exports it from app.core.models.
   - Keeps common auth models (User, Role, Permission) and Department so imports remain stable.
   - No behavioral changes if your existing definitions match table structures from your migrations.

2) alembic/versions/20251007_add_notifications.py
   - Creates the notifications table if missing.
   - Idempotent: on SQLite it will not fail if table/columns already exist.

How to apply
------------
1. Unzip preserving paths into your project root so files land at:
   - app/core/models.py
   - alembic/versions/20251007_add_notifications.py

2. Run migrations:
   alembic upgrade head

3. Start the app:
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Notes
-----
- If you have local customizations in app/core/models.py, copy the Notification class from this patch
  to your file instead of overwriting the whole file.
- If Alembic complains about heads/branches, run `alembic heads` to confirm and then `alembic upgrade head` again.