"""Utility routines for normalising and aggregating evaluation data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Criterion, Plan, PlanItem, Score, Task, TaskCriterion


@dataclass
class TaskScore:
    weight: float
    normalized: float


@dataclass
class CriterionScoreInput:
    weight: float
    tasks: List[TaskScore]


def normalize_weights(pairs: List[tuple[int, Optional[float]]], auto_ids: List[int]) -> Dict[int, float]:
    manual = [(i, w if w is not None else 0.0) for i, w in pairs if i not in auto_ids]
    total_manual = sum(max(0.0, w) for _, w in manual)
    remaining = max(0.0, 1.0 - total_manual)
    share = remaining / len(auto_ids) if auto_ids else 0.0

    result = {idx: max(0.0, weight) for idx, weight in manual}
    for idx in auto_ids:
        result[idx] = share

    total = sum(result.values())
    if total > 0:
        result = {idx: weight / total for idx, weight in result.items()}
    return result


def normalize_value(db: Session | None, scale_type: str, raw_value: Optional[float]) -> float:
    if raw_value is None:
        return 0.0
    if scale_type == "binary":
        return 1.0 if raw_value >= 1 else 0.0
    if scale_type == "one_to_five":
        return max(0.0, min(1.0, (raw_value - 1.0) / 4.0))
    if scale_type == "percent":
        return max(0.0, min(1.0, raw_value / 100.0))
    if scale_type == "text_map":
        return 0.0
    return max(0.0, min(1.0, float(raw_value)))


def criterion_score(criterion: CriterionScoreInput) -> float:
    if not criterion.tasks:
        return 0.0
    total_weight = sum(max(ts.weight, 0.0) for ts in criterion.tasks)
    if total_weight <= 0:
        total_weight = len(criterion.tasks)
    acc = sum(max(ts.weight, 0.0) * max(ts.normalized, 0.0) for ts in criterion.tasks)
    return acc / total_weight


def function_score(criteria_inputs: Iterable[CriterionScoreInput]) -> float:
    inputs = list(criteria_inputs)
    if not inputs:
        return 0.0
    total_weight = sum(max(c.weight, 0.0) for c in inputs)
    if total_weight <= 0:
        total_weight = len(inputs)
    acc = sum(max(c.weight, 0.0) * criterion_score(c) for c in inputs)
    return acc / total_weight


def competency_score(functions: Mapping[str, Iterable[CriterionScoreInput]]) -> float:
    if not functions:
        return 0.0
    scores = [function_score(items) for items in functions.values()]
    return sum(scores) / len(scores)


def gating_ok(
    *,
    completion_pct: int,
    prof_oriented_score: float,
    no_red_criteria: bool,
    recommend_promotion: bool,
) -> bool:
    if completion_pct < 80:
        return False
    if prof_oriented_score < 0.75:
        return False
    if not no_red_criteria:
        return False
    return recommend_promotion


def compute_criterion_score(db: Session, employee_id: int, criterion_id: int) -> float:
    links = db.execute(
        select(TaskCriterion).where(TaskCriterion.criterion_id == criterion_id)
    ).scalars().all()
    if not links:
        return 0.0

    total = 0.0
    weight_total = 0.0
    for link in links:
        score = db.execute(
            select(Score).where(
                Score.employee_id == employee_id,
                Score.task_id == link.task_id,
            )
        ).scalars().first()
        normalized = score.normalized if score and score.normalized is not None else 0.0
        weight = link.weight or 0.0
        total += normalized * weight
        weight_total += weight
    if weight_total <= 0:
        return total / len(links)
    return total / weight_total


def compute_scores(db: Session, employee_id: int, department_id: int | None) -> Dict[str, float]:
    if department_id is None:
        return {}
    criteria_ids = db.execute(
        select(Criterion.id).where(Criterion.department_id == department_id)
    ).scalars().all()
    return {
        str(cid): compute_criterion_score(db, employee_id, cid)
        for cid in criteria_ids
    }


def distance_to_apex(db: Session, employee_id: int, position_id: int) -> Dict[str, float]:
    # Placeholder: real implementation would compare scores with apex profile.
    outstanding_tasks = db.execute(
        select(Task.id)
        .join(TaskCriterion, TaskCriterion.task_id == Task.id)
        .join(Criterion, Criterion.id == TaskCriterion.criterion_id)
    ).scalars().all()
    return {
        "missing_tasks": 0 if outstanding_tasks else 1,
        "score_deficit_pct": 0.0,
    }

