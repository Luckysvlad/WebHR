# app/routers/dashboard.py
from __future__ import annotations

from types import SimpleNamespace
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.db import get_db

# --- Устойчивый импорт модели пользователя из разных возможных мест
User: Optional[type] = None
_import_errors = []

for path in (
    "app.db.models",          # вариант 1: app/db/models.py  -> class User
    "app.models.user",        # вариант 2: app/models/user.py -> class User
    "app.models",             # вариант 3: app/models.py      -> class User
):
    if User:
        break
    try:
        mod = __import__(path, fromlist=["User"])
        if hasattr(mod, "User"):
            User = getattr(mod, "User")
    except Exception as e:  # noqa: BLE001
        _import_errors.append((path, repr(e)))

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    # Если не залогинен — на /login
    user_id = request.session.get("user_id")
    username = request.session.get("username")
    if not (user_id or username):
        return RedirectResponse("/login")

    user_obj = None

    # 1) Если модель User доступна — попробуем вытащить пользователя из БД
    if User is not None:
        if user_id:
            # через pk
            try:
                user_obj = db.get(User, user_id)
            except Exception:
                user_obj = None

        if not user_obj and username:
            # через username
            try:
                user_obj = db.execute(
                    select(User).where(getattr(User, "username") == username)
                ).scalars().first()
            except Exception:
                user_obj = None

    # 2) Если модель недоступна или в БД не нашли — соберём "легковесного" пользователя из сессии
    if not user_obj and username:
        user_obj = SimpleNamespace(username=username, full_name=username)

    # Плейсхолдер статистики (безопасно, не упадёт, если модели нет/полей нет)
    employees_total = None
    if User is not None and hasattr(User, "is_active"):
        try:
            employees_total = db.execute(
                select(func.count()).select_from(User).where(getattr(User, "is_active") == True)  # noqa: E712
            ).scalar_one()
        except Exception:
            employees_total = None

    stats = {
        "greeting": "Добро пожаловать в WebHR",
        "employees_total": employees_total,
    }

    # В шаблон ВСЕГДА передаём ключ user, чтобы Jinja не падала
    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user_obj,
            "stats": stats,
        },
    )
