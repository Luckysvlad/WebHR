from __future__ import annotations
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.models import (
    Employee, Competency, Criterion, Task, TaskCriterion, Score, LevelConfig
)

def normalize_value(db: Session, raw_value: float, scale_type: str, department_id: int|None=None) -> float:
    st = (scale_type or "one_to_five").lower()
    try:
        rv = float(raw_value)
    except Exception:
        rv = 0.0
    if st == "one_to_five":
        return max(0.0, min(1.0, rv / 5.0))
    if st == "binary":
        return 1.0 if rv >= 1 else 0.0
    if st == "percent":
        return max(0.0, min(1.0, rv / 100.0))
    return max(0.0, min(1.0, rv))

def criterion_score(db: Session, employee_id: int, criterion_id: int) -> float:
    links = db.execute(select(TaskCriterion.task_id, TaskCriterion.weight).where(TaskCriterion.criterion_id == criterion_id)).all()
    if not links:
        row = db.execute(select(func.avg(Score.normalized)).where(Score.employee_id==employee_id, Score.criterion_id==criterion_id)).first()
        return float(row[0] or 0.0)
    total = 0.0
    for task_id, weight in links:
        norm = db.execute(select(func.avg(Score.normalized)).where(Score.employee_id==employee_id, Score.task_id==task_id)).scalar()
        total += (weight or 0.0) * float(norm or 0.0)
    return float(total)

def competency_score(db: Session, employee_id: int, competency_id: int) -> float:
    crits = db.execute(select(Criterion.id, Criterion.weight).where(Criterion.competency_id==competency_id)).all()
    if not crits:
        return 0.0
    total = 0.0
    for cid, weight in crits:
        total += (weight or 0.0) * criterion_score(db, employee_id, cid)
    return float(total)

def employee_total(db: Session, employee_id: int) -> float:
    comps = db.execute(select(Competency.id)).scalars().all()
    if not comps:
        return 0.0
    s = 0.0
    for cid in comps:
        s += competency_score(db, employee_id, cid)
    return float(s/len(comps))

def get_level_config(db: Session) -> Tuple[float, float, bool]:
    cfg = db.execute(select(LevelConfig).limit(1)).scalars().first()
    if not cfg:
        return (0.85, 0.60, True)
    return (float(cfg.L1_threshold), float(cfg.L2_threshold), bool(cfg.order_desc))
