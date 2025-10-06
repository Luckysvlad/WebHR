from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.models import Employee, Plan, User
from app.core.rbac import require_login


router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("")
def plans_index(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_login()),
):
    employee = db.execute(select(Employee).where(Employee.user_id == user.id)).scalars().first()

    plan = None
    if employee:
        plan = db.execute(
            select(Plan)
            .where(Plan.employee_id == employee.id)
            .order_by(Plan.period_end.desc())
        ).scalars().first()

    context = {
        "request": request,
        "user": user,
        "plan": plan,
    }
    return request.app.state.templates.TemplateResponse("plans/index.html", context)

