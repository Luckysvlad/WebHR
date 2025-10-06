"""Application ORM models (SQLAlchemy 2.0 style)."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db import Base


# --- Association tables ----------------------------------------------------

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

position_functions = Table(
    "position_functions",
    Base.metadata,
    Column("position_id", ForeignKey("positions.id", ondelete="CASCADE"), primary_key=True),
    Column("function_id", ForeignKey("functions.id", ondelete="CASCADE"), primary_key=True),
)


class FunctionType(str, Enum):
    prof_oriented = "prof_oriented"
    management = "management"
    ability = "ability"
    additional = "additional"


class CriterionBand(str, Enum):
    basic = "basic"
    standard = "standard"
    high = "high"


# --- RBAC -----------------------------------------------------------------


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("code", name="uq_permissions_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
    )


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("name", name="uq_roles_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    is_system: Mapped[bool] = mapped_column(Boolean, server_default=text("0"), default=False)

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )
    permissions: Mapped[List[Permission]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("1"), default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, server_default=text("0"), default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())

    roles: Mapped[List[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    employee: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        back_populates="user",
        uselist=False,
    )


# --- HR core ---------------------------------------------------------------


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("1"), default=True)
    manager_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    manager: Mapped[Optional[User]] = relationship("User")
    positions: Mapped[List["Position"]] = relationship("Position", back_populates="department")
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="department")
    functions: Mapped[List["Function"]] = relationship("Function", back_populates="department")
    competencies: Mapped[List["Competency"]] = relationship("Competency", back_populates="department")


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    apex_rule_json: Mapped[Optional[str]] = mapped_column(Text)
    position_level: Mapped[Optional[int]] = mapped_column(Integer)

    department: Mapped[Optional[Department]] = relationship("Department", back_populates="positions")
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="position")
    functions: Mapped[List["Function"]] = relationship(
        "Function", secondary=position_functions, back_populates="positions"
    )


class Competency(Base):
    __tablename__ = "competencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))

    department: Mapped[Optional[Department]] = relationship("Department", back_populates="competencies")
    functions: Mapped[List["Function"]] = relationship("Function", back_populates="competency")
    plan_items: Mapped[List["PlanItem"]] = relationship("PlanItem", back_populates="competency")


class Function(Base):
    __tablename__ = "functions"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    competency_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competencies.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    weight: Mapped[Optional[float]] = mapped_column(Float)
    visible_to_employee: Mapped[bool] = mapped_column(Boolean, default=True)
    expected_result: Mapped[Optional[str]] = mapped_column(Text)

    department: Mapped[Optional[Department]] = relationship("Department", back_populates="functions")
    competency: Mapped[Optional[Competency]] = relationship("Competency", back_populates="functions")
    positions: Mapped[List[Position]] = relationship(
        "Position", secondary=position_functions, back_populates="functions"
    )
    criteria: Mapped[List["Criterion"]] = relationship("Criterion", back_populates="function")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="function")


class Criterion(Base):
    __tablename__ = "criteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    competency_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competencies.id"))
    function_id: Mapped[Optional[int]] = mapped_column(ForeignKey("functions.id"))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    scale_type: Mapped[str] = mapped_column(String(20), default="one_to_five")
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    auto_weight: Mapped[bool] = mapped_column(Boolean, default=True)
    band: Mapped[Optional[str]] = mapped_column(String(20))

    department: Mapped[Optional[Department]] = relationship("Department")
    competency: Mapped[Optional[Competency]] = relationship("Competency")
    function: Mapped[Optional[Function]] = relationship("Function", back_populates="criteria")
    tasks: Mapped[List["TaskCriterion"]] = relationship("TaskCriterion", back_populates="criterion")
    plan_items: Mapped[List["PlanItem"]] = relationship("PlanItem", back_populates="criterion")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    function_id: Mapped[Optional[int]] = mapped_column(ForeignKey("functions.id"))
    criterion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("criteria.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    expected_result: Mapped[Optional[str]] = mapped_column(Text)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    auto_weight: Mapped[bool] = mapped_column(Boolean, default=True)
    mandatory_for_level: Mapped[bool] = mapped_column(Boolean, default=False)
    mandatory_for_apex: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped[Optional[Department]] = relationship("Department")
    function: Mapped[Optional[Function]] = relationship("Function", back_populates="tasks")
    criterion: Mapped[Optional[Criterion]] = relationship("Criterion")
    task_links: Mapped[List["TaskCriterion"]] = relationship("TaskCriterion", back_populates="task")
    plan_items: Mapped[List["PlanItem"]] = relationship("PlanItem", back_populates="task")


class TaskCriterion(Base):
    __tablename__ = "task_criteria"
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    criterion_id: Mapped[int] = mapped_column(ForeignKey("criteria.id", ondelete="CASCADE"), primary_key=True)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    auto_weight: Mapped[bool] = mapped_column(Boolean, default=True)

    task: Mapped[Task] = relationship("Task", back_populates="task_links")
    criterion: Mapped[Criterion] = relationship("Criterion", back_populates="tasks")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    position_id: Mapped[Optional[int]] = mapped_column(ForeignKey("positions.id"))
    hired_at: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    last_promotion_at: Mapped[Optional[date]] = mapped_column(Date)
    level: Mapped[Optional[int]] = mapped_column(Integer)
    points: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    user: Mapped[Optional[User]] = relationship("User", back_populates="employee")
    department: Mapped[Optional[Department]] = relationship("Department", back_populates="employees")
    position: Mapped[Optional[Position]] = relationship("Position", back_populates="employees")
    plans: Mapped[List["Plan"]] = relationship("Plan", back_populates="employee")


class ScoringRule(Base):
    __tablename__ = "scoring_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    scale_type: Mapped[str] = mapped_column(String(20), nullable=False)
    rule_json: Mapped[str] = mapped_column(Text, nullable=False)


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date, default=date.today)
    criterion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("criteria.id"))
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"))
    raw_value: Mapped[Optional[float]] = mapped_column(Float)
    normalized: Mapped[Optional[float]] = mapped_column(Float)


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    completion_pct: Mapped[int] = mapped_column(Integer, default=0)
    recommend_promotion: Mapped[bool] = mapped_column(Boolean, default=False)

    employee: Mapped[Employee] = relationship("Employee", back_populates="plans")
    items: Mapped[List["PlanItem"]] = relationship(
        "PlanItem", back_populates="plan", cascade="all, delete-orphan"
    )


class PlanItem(Base):
    __tablename__ = "plan_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"))
    competency_id: Mapped[Optional[int]] = mapped_column(ForeignKey("competencies.id"))
    function_id: Mapped[Optional[int]] = mapped_column(ForeignKey("functions.id"))
    criterion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("criteria.id"))
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"))
    expected_result: Mapped[Optional[str]] = mapped_column(Text)
    employee_report: Mapped[Optional[str]] = mapped_column(Text)
    is_visible_to_employee: Mapped[bool] = mapped_column(Boolean, default=True)
    report_text: Mapped[Optional[str]] = mapped_column(Text)

    plan: Mapped[Plan] = relationship("Plan", back_populates="items")
    competency: Mapped[Optional[Competency]] = relationship("Competency", back_populates="plan_items")
    function: Mapped[Optional[Function]] = relationship("Function")
    criterion: Mapped[Optional[Criterion]] = relationship("Criterion", back_populates="plan_items")
    task: Mapped[Optional[Task]] = relationship("Task", back_populates="plan_items")


class PlanTemplate(Base):
    __tablename__ = "plan_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    items: Mapped[List["PlanTemplateItem"]] = relationship(
        "PlanTemplateItem", back_populates="template", cascade="all, delete-orphan"
    )


class PlanTemplateItem(Base):
    __tablename__ = "plan_template_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("plan_templates.id", ondelete="CASCADE"))
    competency: Mapped[Optional[str]] = mapped_column(String(255))
    function: Mapped[Optional[str]] = mapped_column(String(255))
    criterion: Mapped[Optional[str]] = mapped_column(String(255))
    task: Mapped[Optional[str]] = mapped_column(String(255))
    expected: Mapped[Optional[str]] = mapped_column(Text)

    template: Mapped[PlanTemplate] = relationship("PlanTemplate", back_populates="items")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="notifications")


class EmployeeCompetencyVisibility(Base):
    __tablename__ = "employee_competency_visibility"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    competency_id: Mapped[int] = mapped_column(ForeignKey("competencies.id", ondelete="CASCADE"))

