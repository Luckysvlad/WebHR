# WebHR Patch — Fixes & How to Run

Date: 2025-10-05

## Что исправлено
- ✅ Убрана петля редиректов `/login ↔ /dashboard`: теперь единственный обработчик `/dashboard` живёт в `app/routers/dashboard.py`, проверяет только факт логина.
- ✅ Добавлен `SessionMiddleware` (был, проверено) и middleware `attach_user` (оставлено).
- ✅ Приведены к единому стилю пути к шаблонам/статике через `templates_utils` и `settings.TEMPLATES_DIR/STATIC_DIR`.
- ✅ Маршруты подключены централизованно: `dashboard`, `manager`, `notifications` добавлены в `app/main.py`.
- ✅ RBAC: код доступа для сотрудников заменён на `employees.view`; `/manager/probation` защищён требованием `employees.view`.
- ✅ `/notifications` требует `notifications.view`.
- ✅ Пароли: логин переведён на `bcrypt` (ранее был `sha256`).
- ✅ Сидинг (`scripts/seed_admin.py`) переписан: создаёт роли/права и пользователя admin/admin123 (bcrypt), идемпотентен.
- ✅ Alembic: в репозитории уже одна head (`5150fc890f5b` merge). Скрипты миграций проверяют наличие таблиц/колонок (SQLite-safe).

## Команды (Windows)
```bat
python -m venv myenv
myenv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed_admin
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Проверка (Acceptance)
- `/login` (GET=200) → POST admin/admin123 → 303 `/dashboard` → `/dashboard`=200.
- `/company/employees`: под `admin` — 200; под сотрудником без прав — 403 (не 401).
- `/manager/probation` и `/admin/org` — по ролям.
- `/notifications` — список и отметка «прочитано» (страницы присутствуют).
- `/static/style.css` → 200.
- В логах **нет**: `no such table/column`, `Multiple heads`, `script.py.mako not found`, `SessionMiddleware must be installed`.

## Примечания
- БД по умолчанию: `sqlite:///./webhr.db`. Можно переопределить через `.env`.
- Если вы ранее создавали пользователей SHA-256, пересоздайте их или задайте новый пароль через сидер.
