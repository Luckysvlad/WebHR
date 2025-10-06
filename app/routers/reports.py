from __future__ import annotations
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
import os, tempfile

from app.core.db import get_db
from app.core.rbac import require_permission
from app.core.models import Employee
from app.reports.employee_profile import make_employee_profile_pdf
from app.reports.employee_profile_xlsx import make_employee_profile_xlsx

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", dependencies=[Depends(require_permission("view_reports"))])
def reports_index(request: Request):
    return request.app.state.templates.TemplateResponse("reports/index.html", {"request": request})

@router.get("/employee/{employee_id}", dependencies=[Depends(require_permission("view_reports"))])
def employee_profile(employee_id: int, fmt: str = Query("pdf"), db: Session = Depends(get_db)):
    emp = db.get(Employee, employee_id)
    if not emp:
        return PlainTextResponse("Employee not found", status_code=404)
    fd, path = tempfile.mkstemp(suffix=f".{fmt}")
    os.close(fd)
    if fmt == "pdf":
        make_employee_profile_pdf(db, emp, path)
    else:
        make_employee_profile_xlsx(db, emp, path)
    return FileResponse(path, filename=f"employee_{employee_id}.{fmt}")
