from __future__ import annotations
"""
Robust seed script that works on local dev without MySQL.
- Tries SEED_DATABASE_URL, then settings.DATABASE_URL.
- On connection failure to MySQL/MariaDB, falls back to SQLite: sqlite:///data/app.db
- Idempotent: safe get-or-create for departments, positions, role/perm, admin user.
"""
import os
from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

import bcrypt

try:
    # Prefer local app settings if present
    from app.core.config import settings
except Exception:
    class _S:
        DATABASE_URL = "sqlite:///data/app.db"
        ENV = "local"
    settings = _S()  # type: ignore


from app.core.db import Base  # only for metadata
from app.core.models import Department, Position, User, Role, Permission


def _mk_sqlite_path(url: str) -> None:
    # Ensure folder for sqlite file exists, e.g., sqlite:///data/app.db
    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "", 1)
        folder = os.path.dirname(path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)


def connect_engine():
    # 1) allow override for seeding
    url = os.getenv("SEED_DATABASE_URL") or getattr(settings, "DATABASE_URL", "sqlite:///data/app.db")
    try:
        # Fast probe connection
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        engine = create_engine(url, future=True, pool_pre_ping=True, connect_args=connect_args)
        with engine.connect() as conn:
            conn.execute(select(1))
        print(f"[seed] Using database: {url}")
        return engine
    except OperationalError as e:
        print(f"[seed] Primary DB connection failed: {e}")
        # 2) fallback for local dev
        fallback = "sqlite:///data/app.db"
        print(f"[seed] Falling back to SQLite: {fallback}")
        _mk_sqlite_path(fallback)
        engine = create_engine(fallback, future=True, pool_pre_ping=True, connect_args={"check_same_thread": False})
        return engine


def get_or_create(db: Session, model, defaults=None, **filters):
    defaults = defaults or {}
    obj = db.execute(select(model).filter_by(**filters)).scalars().first()
    if obj:
        return obj, False
    obj = model(**{**filters, **defaults})
    db.add(obj)
    db.flush()
    return obj, True


def ensure_admin_user(db: Session) -> None:
    # Role & permission
    perm_admin, _ = get_or_create(db, Permission, code="admin_all", defaults={"name": "Administrator full access"})
    role_admin, created_role = get_or_create(db, Role, name="Administrator", defaults={"description": "All access"})
    if created_role or perm_admin not in role_admin.permissions:
        role_admin.permissions.append(perm_admin)

    # Admin user (login: admin / pass: admin)
    admin = db.execute(select(User).where(User.username == "admin")).scalars().first()
    if not admin:
        pwd = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode("utf-8")
        admin = User(username="admin", password_hash=pwd, full_name="Администратор", is_superuser=True, is_active=True)
        db.add(admin)
    # Link role
    if role_admin not in admin.roles:
        admin.roles.append(role_admin)


def main():
    engine = connect_engine()
    # Safe create (idempotent in dev; in prod expect Alembic to have run already)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        # Seed departments
        it, _ = get_or_create(db, Department, code="IT", defaults={"name": "IT", "is_active": True})
        hr, _ = get_or_create(db, Department, code="HR", defaults={"name": "HR", "is_active": True})

        # Seed positions
        get_or_create(db, Position, department_id=it.id, name="Senior Developer", defaults={"description": ""})
        get_or_create(db, Position, department_id=hr.id, name="HR Manager", defaults={"description": ""})

        # Admin user & role
        ensure_admin_user(db)

        db.commit()
        print("[seed] OK. Login with admin / admin")


if __name__ == "__main__":
    main()
