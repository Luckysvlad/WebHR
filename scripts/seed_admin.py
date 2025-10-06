from __future__ import annotations
from sqlalchemy import select
from app.core.db import SessionLocal
from app.core.models import User, Role, Permission, user_roles, role_permissions
import bcrypt

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

PERMISSIONS = {
    "admin.all": "Полный доступ",
    "employees.view": "Просмотр сотрудников",
    "employees.manage": "Управление сотрудниками (CRUD)",
    "notifications.view": "Просмотр уведомлений",
}

ROLES = {
    "admin": ["admin.all"],
    "manager": ["employees.view", "notifications.view"],
    "employee": ["notifications.view"],
}

def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _check(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def main():
    with SessionLocal() as db:
        # Ensure permissions
        code_to_perm = {}
        for code, name in PERMISSIONS.items():
            p = db.execute(select(Permission).where(Permission.code==code)).scalars().first()
            if not p:
                p = Permission(code=code, name=name)
                db.add(p)
                db.flush()
            code_to_perm[code] = p

        # Ensure roles and role-permission bindings
        name_to_role = {}
        for name, perm_codes in ROLES.items():
            r = db.execute(select(Role).where(Role.code==name)).scalars().first()
            if not r:
                r = Role(code=name, name=name, description=f"Role {name}")
                db.add(r)
                db.flush()
            name_to_role[name] = r
            # sync permissions
            existing = {rp[0] for rp in db.execute(select(role_permissions.c.permission_id).where(role_permissions.c.role_id==r.id)).all()}
            for code in perm_codes:
                p = code_to_perm[code]
                if p.id not in existing:
                    db.execute(role_permissions.insert().values(role_id=r.id, permission_id=p.id))

        # Ensure admin user and bind admin role
        u = db.execute(select(User).where(User.username==ADMIN_USERNAME)).scalars().first()
        if not u:
            u = User(username=ADMIN_USERNAME, password_hash=_hash(ADMIN_PASSWORD), is_active=True, is_superuser=True)
            db.add(u)
            db.flush()
            print(f"Created admin/{ADMIN_PASSWORD}")
        # bind admin role
        admin_role = name_to_role["admin"]
        existing_roles = {ur[0] for ur in db.execute(select(user_roles.c.role_id).where(user_roles.c.user_id==u.id)).all()}
        if admin_role.id not in existing_roles:
            db.execute(user_roles.insert().values(user_id=u.id, role_id=admin_role.id))

        db.commit()
        print("Seeding complete (idempotent).")

if __name__ == "__main__":
    main()
