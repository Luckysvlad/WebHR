from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext
from app.core.models import (
    Permission, Role, User, Department, Position, Employee,
    Competency, Function, FunctionType, Criterion, CriterionBand, Task,
    DepartmentFunctionMap, PlanTemplate, PlanTemplateItem, Notification
)

# PBKDF2-SHA256 (pure Python, cross-platform)
pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_or_create(session: Session, model, defaults=None, **kwargs):
    stmt = select(model).filter_by(**kwargs)
    obj = session.execute(stmt).scalars().first()
    if obj:
        return obj, False
    params = dict(kwargs)
    if defaults:
        params.update(defaults)
    obj = model(**params)
    session.add(obj)
    session.flush()
    return obj, True

def _ensure_pbkdf2(user: User, plain: str):
    """Force reset to PBKDF2 if hash is missing or not PBKDF2 (e.g., old bcrypt $2b$)."""
    current = (user.password_hash or "")
    if not current.startswith("$pbkdf2-sha256$"):
        user.password_hash = pwd.hash(plain)

def run(session: Session, admin_password: str = "admin"):
    # Permissions
    perms = {}
    for code in ["admin.all", "hr.manage", "dept.manage", "app.view"]:
        p, _ = get_or_create(session, Permission, code=code)
        perms[code] = p

    # Roles
    role_admin, _ = get_or_create(session, Role, name="Администратор")
    role_hr, _ = get_or_create(session, Role, name="HR-менеджер")
    role_lead, _ = get_or_create(session, Role, name="Руководитель отдела")
    role_user, _ = get_or_create(session, Role, name="Сотрудник")

    # Users
    admin, _ = get_or_create(session, User, username="admin", defaults={
        "password_hash": pwd.hash(admin_password), "is_active": True, "is_superuser": True
    })
    hr, _ = get_or_create(session, User, username="hr", defaults={
        "password_hash": pwd.hash("hr"), "is_active": True, "is_superuser": False
    })
    lead, _ = get_or_create(session, User, username="lead", defaults={
        "password_hash": pwd.hash("lead"), "is_active": True, "is_superuser": False
    })
    user, _ = get_or_create(session, User, username="user", defaults={
        "password_hash": pwd.hash("user"), "is_active": True, "is_superuser": False
    })

    # Attach roles
    admin.roles = [role_admin]
    hr.roles = [role_hr]
    lead.roles = [role_lead]
    user.roles = [role_user]

    # Ensure PBKDF2 hashes even if users existed before with bcrypt
    _ensure_pbkdf2(admin, admin_password)
    _ensure_pbkdf2(hr, "hr")
    _ensure_pbkdf2(lead, "lead")
    _ensure_pbkdf2(user, "user")

    # Department
    dept_a, _ = get_or_create(session, Department, name="Отдел А", defaults={"manager_user_id": lead.id})
    # Positions
    pos_head, _ = get_or_create(session, Position, title="Руководитель отдела", department_id=dept_a.id, defaults={"position_level": 1})
    pos_senior, _ = get_or_create(session, Position, title="Главный специалист", department_id=dept_a.id, defaults={"position_level": 1})
    pos_lead, _ = get_or_create(session, Position, title="Ведущий специалист", department_id=dept_a.id, defaults={"position_level": 2})
    pos_spec, _ = get_or_create(session, Position, title="Специалист", department_id=dept_a.id, defaults={"position_level": 3})

    # Employees demo
    ivanov, _ = get_or_create(session, Employee, full_name="Иванов И.И.", defaults={
        "age": 35, "department_id": dept_a.id, "position_id": pos_head.id, "level": 1, "user_id": lead.id, "visible": True
    })
    petrov, _ = get_or_create(session, Employee, full_name="Петров П.П.", defaults={
        "age": 28, "department_id": dept_a.id, "position_id": pos_spec.id, "level": 3, "visible": True
    })

    # Competency tree (minimal demo)
    comp, _ = get_or_create(session, Competency, title="Компетенция")
    functions = []
    for ftype, weight in [
        (FunctionType.prof_oriented, 0.4),
        (FunctionType.management, 0.3),
        (FunctionType.ability, 0.2),
        (FunctionType.additional, 0.1),
    ]:
        f, _ = get_or_create(session, Function, competency_id=comp.id, title=ftype.value, defaults={
            "type": ftype, "visible_to_employee": True, "weight": weight, "expected_result": "Описание результата"
        })
        functions.append(f)

        # Criteria
        crit_basic, _ = get_or_create(session, Criterion, function_id=f.id, title="Критерий (минимум)", defaults={
            "weight": 0.34, "band": "basic"
        })
        crit_std, _ = get_or_create(session, Criterion, function_id=f.id, title="Критерий (стандарт)", defaults={
            "weight": 0.33, "band": "standard"
        })
        crit_high, _ = get_or_create(session, Criterion, function_id=f.id, title="Критерий (высокий)", defaults={
            "weight": 0.33, "band": "high"
        })

        # Tasks (one per criterion for demo)
        get_or_create(session, Task, criterion_id=crit_basic.id, title="Задача 1", defaults={"expected_result": "Итог", "weight": 1.0})
        get_or_create(session, Task, criterion_id=crit_std.id, title="Задача 2", defaults={"expected_result": "Итог", "weight": 1.0})
        get_or_create(session, Task, criterion_id=crit_high.id, title="Задача 3", defaults={"expected_result": "Итог", "weight": 1.0})

    # Department → allowed functions
    for f in functions:
        get_or_create(session, DepartmentFunctionMap, department_id=dept_a.id, function_id=f.id)

    # Plan template
    tpl, _ = get_or_create(session, PlanTemplate, department_id=dept_a.id, title="Испытательный срок")
    get_or_create(session, PlanTemplateItem, template_id=tpl.id, competency="Компетенция",
                  function="prof_oriented", criterion="basic", task="Ознакомиться с регламентами", expected="Знание регламентов")
    get_or_create(session, PlanTemplateItem, template_id=tpl.id, competency="Компетенция",
                  function="management", criterion="standard", task="Сдатьмини-отчёт", expected="Отчёт принят")

    # Initial notifications example
    from app.core.models import User as U, Notification as N
    admin_user = session.execute(select(U).where(U.username=="admin")).scalars().first()
    lead_user = session.execute(select(U).where(U.username=="lead")).scalars().first()
    if admin_user:
        get_or_create(session, N, recipient_user_id=admin_user.id, title="Добро пожаловать", body="Создайте учётные записи HR-флоу")
    if lead_user:
        get_or_create(session, N, recipient_user_id=lead_user.id, title="План на испытательный срок", body="Назначьте план сотруднику")

def main():
    from app.core.db import SessionLocal, engine, Base
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        run(session)
        session.commit()

if __name__ == "__main__":
    main()
