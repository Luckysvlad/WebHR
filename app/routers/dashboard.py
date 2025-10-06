"""Dashboard views."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.models import Department, Employee, Plan, User
from app.core.rbac import require_login


router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_login()),
):
    employees_count = db.execute(select(func.count()).select_from(Employee)).scalar_one()
    departments_count = db.execute(select(func.count()).select_from(Department)).scalar_one()

    employee = db.execute(
        select(Employee).where(Employee.user_id == user.id)
    ).scalars().first()

    latest_plan = None
    if employee:
        latest_plan = db.execute(
            select(Plan)
                .where(Plan.employee_id == employee.id)
                .order_by(Plan.period_end.desc())
        ).scalars().first()
    current_plan_status = latest_plan.status if latest_plan else "—"

    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "employees_count": employees_count,
            "departments_count": departments_count,
            "current_plan_status": current_plan_status,
        },
    )

