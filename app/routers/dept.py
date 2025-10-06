from __future__ import annotations
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.db import get_db
from app.core.rbac import require_perm
from app.core.models import Department

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/departments")
def departments(request: Request, db: Session = Depends(get_db), _: bool = Depends(require_perm("admin.all"))):
    depts = db.execute(select(Department).order_by(Department.name)).scalars().all()
    active_id = request.session.get("active_department_id")
    return templates.TemplateResponse("admin/departments.html", {"request": request, "departments": depts, "active_id": active_id})

@router.post("/departments/add")
def add_department(request: Request, db: Session = Depends(get_db), _: bool = Depends(require_perm("admin.all")),
                   name: str = Form(...), code: str = Form(""), is_active: bool = Form(False)):
    d = Department(name=name.strip(), code=(code or None), is_active=is_active)
    db.add(d); db.commit()
    return RedirectResponse("/departments", status_code=303)

@router.post("/departments/set_active")
def set_active_department(request: Request, dept_id: int = Form(...)):
    request.session["active_department_id"] = dept_id
    return RedirectResponse("/dashboard", status_code=303)
