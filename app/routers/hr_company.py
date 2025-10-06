from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.db import get_db
from app.core.models import Employee
from app.core.rbac import require_perm
from app.templates_utils import templates

router = APIRouter(prefix="/company", tags=["company"])

@router.get("/employees", response_class=HTMLResponse, dependencies=[Depends(require_perm("employees.view"))])
def employees_page(request: Request, db: Session = Depends(get_db)):
    # Require login
    user = getattr(request.state, "user", None)
    if not user:
        return RedirectResponse("/login", status_code=303)
    employees = db.execute(select(Employee).order_by(Employee.last_name, Employee.first_name)).scalars().all()
    return templates.TemplateResponse("company/employees.html", {"request": request, "employees": employees})
