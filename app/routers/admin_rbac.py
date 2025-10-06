from __future__ import annotations
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.core.rbac import require_permission
from app.core.models import Role, Permission

router = APIRouter(prefix="/admin/rbac", tags=["Admin/RBAC"])

@router.get("", dependencies=[Depends(require_permission("admin_all"))])
def rbac_page(request: Request, db: Session = Depends(get_db)):
    roles = db.execute(select(Role)).scalars().all()
    perms = db.execute(select(Permission)).scalars().all()
    return request.app.state.templates.TemplateResponse("admin/rbac.html", {"request": request, "roles": roles, "perms": perms})

@router.post("/role", dependencies=[Depends(require_permission("admin_all"))])
def create_role(name: str = Form(...), description: str = Form(""), db: Session = Depends(get_db)):
    r = db.execute(select(Role).where(Role.name == name)).scalars().first()
    if r:
        raise HTTPException(400, "Role already exists")
    r = Role(name=name, description=description, is_system=False)
    db.add(r); db.commit()
    return {"ok": True, "id": r.id}

@router.post("/role/{role_id}/toggle", dependencies=[Depends(require_permission("admin_all"))])
def toggle_perm(role_id: int, perm_code: str = Form(...), db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(404, "Role not found")
    perm = db.execute(select(Permission).where(Permission.code == perm_code)).scalars().first()
    if not perm:
        perm = Permission(code=perm_code, name=perm_code)
        db.add(perm); db.flush()
    if perm in role.permissions:
        role.permissions.remove(perm)
    else:
        role.permissions.append(perm)
    db.add(role); db.commit()
    return {"ok": True}
