# WebHR Patch

This patch replaces broken files and fixes:
- Missing `TEMPLATES_DIR` in settings
- Correct SessionMiddleware import & order
- Robust session-based user attach middleware
- RBAC dependency signature (`require_perm("...")`)
- Complete SQLAlchemy models (users/roles/permissions/departments/employees/positions/notifications)
- Minimal, working routers for auth, admin (departments), company (employees), notifications
- Static files & templates
- Alembic environment and two migrations (init + safe leveling extension)

## How to apply

1) Backup your repo.
2) Unzip this archive over your project root (so files land under `app/...`, `alembic/...`, etc.)
3) Recreate DB (optional if fresh):
   ```
   del webhr.db   # on Windows cmd
   ```
4) Run migrations:
   ```
   alembic upgrade head
   ```
5) Start the app:
   ```
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
6) First login:
   - username: `admin`
   - password: `admin`
   A default superuser is created on first login if the DB is empty.

## Notes
- The admin page is at `/admin/departments`.
- The company employees page is at `/company/employees`.
- The code is intentionally minimal but consistent; extend as needed.
