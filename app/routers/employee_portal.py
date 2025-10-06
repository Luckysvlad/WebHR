from __future__ import annotations
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.db import get_db
from app.core.rbac import require_login
from app.core.models import Employee, Plan, PlanItem, Department, Position, EmployeeCompetencyVisibility
from app.core.services.evaluation_service import compute_scores, distance_to_apex

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def _get_employee_by_user(db: Session, user_id: int) -> Employee | None:
    return db.execute(select(Employee).where(Employee.user_id==user_id)).scalars().first()

@router.get("/me")
def my_cabinet(request: Request, db: Session = Depends(get_db), user=Depends(require_login)):
    emp = _get_employee_by_user(db, user.id)
    if not emp:
        return templates.TemplateResponse("employee/empty.html", {"request": request, "msg": "Профиль сотрудника не найден."})
    dept = db.get(Department, emp.department_id) if emp.department_id else None
    pos = db.get(Position, emp.position_id) if emp.position_id else None
    scores = compute_scores(db, emp.id, emp.department_id)
    apex = distance_to_apex(db, emp.id, emp.position_id) if emp.position_id else {"missing_tasks": 0, "score_deficit_pct": 0.0}
    return templates.TemplateResponse("employee/cabinet.html", {"request": request, "emp": emp, "dept": dept, "pos": pos, "scores": scores, "apex": apex})

@router.get("/me/plan")
def my_plan(request: Request, db: Session = Depends(get_db), user=Depends(require_login)):
    emp = _get_employee_by_user(db, user.id)
    if not emp:
        return templates.TemplateResponse("employee/empty.html", {"request": request, "msg": "План не найден."})
    plan = db.execute(select(Plan).where(Plan.employee_id==emp.id).order_by(Plan.id.desc())).scalars().first()
    if not plan:
        return templates.TemplateResponse("employee/empty.html", {"request": request, "msg": "Нет активного плана."})
    vis_ids = {row.competency_id for row in db.execute(select(EmployeeCompetencyVisibility).where(EmployeeCompetencyVisibility.employee_id==emp.id)).scalars().all()}
    items = db.execute(select(PlanItem).where(PlanItem.plan_id==plan.id)).scalars().all()
    if vis_ids:
        items = [it for it in items]  # simplified filter placeholder
    editable = plan.status in ("draft","in_progress")
    return templates.TemplateResponse("employee/plan.html", {"request": request, "plan": plan, "items": items, "editable": editable})

@router.post("/me/plan/save")
def my_plan_save(request: Request, db: Session = Depends(get_db), user=Depends(require_login), plan_id: int = Form(...), item_id: int = Form(...), report_text: str = Form("")):
    item = db.get(PlanItem, item_id)
    if item and item.plan_id == plan_id:
        item.report_text = report_text
        db.commit()
    return my_plan(request, db, user)

@router.post("/me/plan/submit")
def my_plan_submit(request: Request, db: Session = Depends(get_db), user=Depends(require_login), plan_id: int = Form(...)):
    plan = db.get(Plan, plan_id)
    if not plan:
        return my_plan(request, db, user)
    items = db.execute(select(PlanItem).where(PlanItem.plan_id==plan.id)).scalars().all()
    if all((it.report_text or "").strip() for it in items):
        plan.status = "submitted"; db.commit()
    return my_plan(request, db, user)
