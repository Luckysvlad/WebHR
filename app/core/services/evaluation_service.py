from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.models import (
    ScoringRule, Score, Criterion, TaskCriterion, Task, Plan, PlanItem
)

def normalize_weights(pairs: List[Tuple[int, float]], auto_ids: List[int]) -> Dict[int, float]:
    manual = [(i, w) for i, w in pairs if i not in auto_ids and w is not None]
    total_manual = sum(max(0.0, w) for _, w in manual)
    rem = max(0.0, 1.0 - total_manual)
    per_auto = (rem / len(auto_ids)) if auto_ids else 0.0
    out = {i: max(0.0, w) for i, w in manual}
    for i in auto_ids:
        out[i] = per_auto
    s = sum(out.values())
    if s > 0:
        out = {k: v / s for k, v in out.items()}
    return out

def normalize_value(db: Session, scale_type: str, raw_value: Optional[float]) -> float:
    if raw_value is None:
        return 0.0
    # simple defaults; can be extended by ScoringRule
    if scale_type == "binary":
        return 1.0 if raw_value >= 1.0 else 0.0
    if scale_type == "one_to_five":
        return max(0.0, min(1.0, (raw_value - 1.0) / 4.0))
    if scale_type == "percent":
        return max(0.0, min(1.0, raw_value / 100.0))
    if scale_type == "text_map":
        return 0.0
    return max(0.0, min(1.0, float(raw_value)))

# Placeholder aggregation APIs (wire up to your UI/handlers)
def compute_criterion_score(db: Session, employee_id: int, criterion_id: int) -> float:
    # average of task scores connected to criterion via TaskCriterion weights
    tcs = db.execute(select(TaskCriterion).where(TaskCriterion.criterion_id == criterion_id)).scalars().all()
    if not tcs:
        return 0.0
    acc = 0.0
    for tc in tcs:
        sc = db.execute(select(Score).where(Score.employee_id == employee_id, Score.task_id == tc.task_id)).scalars().first()
        acc += (sc.normalized if sc and sc.normalized is not None else 0.0) * (tc.weight or 0.0)
    return acc

