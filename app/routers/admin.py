from __future__ import annotations
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.db import get_db
from app.core.models import Department
from app.core.rbac import require_perm
from app.templates_utils import templates

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/org", response_class=HTMLResponse, dependencies=[Depends(require_perm("admin.all"))])
def org_dashboard(request: Request, db: Session = Depends(get_db)):
    departments = db.execute(select(Department).order_by(Department.name)).scalars().all()
    return templates.TemplateResponse("admin/org.html", {"request": request, "departments": departments, "active_id": None})

@router.get("/departments", response_class=HTMLResponse, dependencies=[Depends(require_perm("admin.all"))])
def departments_page(request: Request, db: Session = Depends(get_db)):
    departments = db.execute(select(Department).order_by(Department.name)).scalars().all()
    return templates.TemplateResponse("admin/departments.html", {"request": request, "departments": departments, "active_id": None})

@router.post("/departments/add", dependencies=[Depends(require_perm("admin.all"))])
def add_department(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    dep = Department(name=name.strip())
    db.add(dep)
    db.commit()
    return RedirectResponse("/admin/departments", status_code=303)
