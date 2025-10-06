
from sqlalchemy import select
from app.core.db import SessionLocal
from app.core.models import Role, Permission, User

def main():
    db = SessionLocal()
    try:
        # Ensure permission exists
        perm = db.execute(select(Permission).where(Permission.code=='admin_all')).scalars().first()
        if not perm:
            perm = Permission(code='admin_all', name='Administrator full access')
            db.add(perm); db.flush()
        # Find admin-like role
        role = db.execute(select(Role).where(Role.name.in_(['Administrator','Admin','Администратор']))).scalars().first()
        if not role:
            role = db.execute(select(Role).limit(1)).scalars().first()
        if role and perm not in role.permissions:
            role.permissions.append(perm); db.add(role)
        # Optionally ensure first user has this role
        user = db.execute(select(User).order_by(User.id.asc())).scalars().first()
        if user and role and role not in user.roles:
            user.roles.append(role); db.add(user)
        db.commit()
        print('[ok] admin_all granted')
    finally:
        db.close()

if __name__ == '__main__':
    main()
