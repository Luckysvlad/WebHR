from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.models import Competency, Employee, User
from app.core.rbac import require_login


router = APIRouter(prefix="/matrices", tags=["matrices"])


@router.get("/competencies")
def competencies_matrix(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_login()),
):
    employees = db.query(Employee).all()
    competencies = db.query(Competency).all()

    context = {
        "request": request,
        "user": user,
        "employees": employees,
        "competencies": competencies,
        "matrix": [],
    }
    return request.app.state.templates.TemplateResponse("matrices/competencies.html", context)

