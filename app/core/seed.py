"""Idempotent bootstrap helpers used in tests and startup."""

from __future__ import annotations

from datetime import date
from typing import Tuple, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import (
    Competency,
    Department,
    Employee,
    Function,
    Notification,
    Permission,
    Plan,
    PlanItem,
    PlanTemplate,
    PlanTemplateItem,
    Position,
    Role,
    Task,
    User,
)
from app.core.security import hash_password, verify_password


T = TypeVar("T")


def get_or_create(session: Session, model: Type[T], /, defaults: dict | None = None, **kwargs) -> Tuple[T, bool]:
    stmt = select(model).filter_by(**kwargs)
    instance = session.execute(stmt).scalars().first()
    if instance:
        return instance, False
    params = {**kwargs, **(defaults or {})}
    instance = model(**params)  # type: ignore[arg-type]
    session.add(instance)
    session.flush()
    return instance, True


def _ensure_password(user: User, password: str) -> None:
    if not user.password_hash or not verify_password(password, user.password_hash):
        user.password_hash = hash_password(password)


def run(session: Session, admin_password: str = "admin12345") -> None:
    perms = {}
    for code, name in (
        ("admin.all", "Полный доступ"),
        ("employees.view", "Просмотр сотрудников"),
        ("plans.view", "Просмотр планов"),
    ):
        perm, _ = get_or_create(session, Permission, code=code, defaults={"name": name})
        perms[code] = perm

    role_unique_field = getattr(Role, "code", None)
    if role_unique_field is not None:
        role_admin, _ = get_or_create(session, Role, code="admin", defaults={"name": "Администратор"})
        role_user, _ = get_or_create(session, Role, code="user", defaults={"name": "Сотрудник"})
    else:
        role_admin, _ = get_or_create(session, Role, name="Администратор")
        role_user, _ = get_or_create(session, Role, name="Сотрудник")
        if hasattr(role_admin, "code"):
            role_admin.code = "admin"
        if hasattr(role_user, "code"):
            role_user.code = "user"
    role_admin.permissions = list(perms.values())
    if not role_user.permissions:
        role_user.permissions = [perms["plans.view"]]

    admin, _ = get_or_create(
        session,
        User,
        username="admin",
        defaults={
            "password_hash": hash_password(admin_password),
            "is_active": True,
            "is_superuser": True,
            "full_name": "Администратор",
        },
    )
    _ensure_password(admin, admin_password)
    admin.roles = [role_admin]

    employee_user, _ = get_or_create(
        session,
        User,
        username="employee",
        defaults={
            "password_hash": hash_password("employee"),
            "is_active": True,
            "full_name": "Петров Петр",
        },
    )
    _ensure_password(employee_user, "employee")
    employee_user.roles = [role_user]

    dept, _ = get_or_create(session, Department, name="Отдел разработки", defaults={"code": "DEV"})
    position, _ = get_or_create(
        session,
        Position,
        name="Разработчик",
        defaults={"department_id": dept.id, "position_level": 1},
    )
    employee, _ = get_or_create(
        session,
        Employee,
        full_name="Петров Петр",
        defaults={
            "user_id": employee_user.id,
            "department_id": dept.id,
            "position_id": position.id,
            "hired_at": date.today(),
        },
    )

    competency, _ = get_or_create(
        session,
        Competency,
        name="Профессиональные навыки",
        defaults={"department_id": dept.id},
    )
    function, _ = get_or_create(
        session,
        Function,
        name="Базовые задачи",
        defaults={"department_id": dept.id, "competency_id": competency.id},
    )
    task, _ = get_or_create(
        session,
        Task,
        name="Настроить окружение",
        defaults={"department_id": dept.id, "function_id": function.id, "weight": 1.0},
    )

    plan, _ = get_or_create(
        session,
        Plan,
        employee_id=employee.id,
        defaults={
            "period_start": date.today(),
            "period_end": date.today(),
            "status": "draft",
        },
    )
    get_or_create(
        session,
        PlanItem,
        plan_id=plan.id,
        task_id=task.id,
        defaults={"expected_result": "Доступ к сервисам оформлен"},
    )

    template, _ = get_or_create(
        session,
        PlanTemplate,
        title="Онбординг",
        defaults={"department_id": dept.id},
    )
    get_or_create(
        session,
        PlanTemplateItem,
        template_id=template.id,
        competency="Профессиональные навыки",
        defaults={"task": "Пройти вводный курс", "expected": "Курс завершён"},
    )

    get_or_create(
        session,
        Notification,
        user_id=admin.id,
        defaults={"message": "Добро пожаловать в WebHR"},
    )


def main() -> None:
    from app.core.db import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        run(session)
        session.commit()


if __name__ == "__main__":
    main()

