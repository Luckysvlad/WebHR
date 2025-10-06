"""Domain init: core HR tables (base)
Revision ID: 20251005_domain_init
Revises: 
Create Date: 2025-10-05
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251005_domain_init'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def table_exists(conn, name: str) -> bool:
    insp = sa.inspect(conn)
    return insp.has_table(name)

def upgrade() -> None:
    conn = op.get_bind()

    if not table_exists(conn, "departments"):
        op.create_table("departments",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("code", sa.String(50), nullable=False, unique=True),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
        )

    if not table_exists(conn, "positions"):
        op.create_table("positions",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id", ondelete="CASCADE"), index=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text),
            sa.Column("apex_rule_json", sa.Text),
        )

    if not table_exists(conn, "functions"):
        op.create_table("functions",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id", ondelete="CASCADE"), index=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text),
        )

    if not table_exists(conn, "position_functions"):
        op.create_table("position_functions",
            sa.Column("position_id", sa.Integer, sa.ForeignKey("positions.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("function_id", sa.Integer, sa.ForeignKey("functions.id", ondelete="CASCADE"), primary_key=True),
        )

    if not table_exists(conn, "competencies"):
        op.create_table("competencies",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id", ondelete="CASCADE"), index=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text),
            sa.Column("category", sa.String(100)),
        )

    if not table_exists(conn, "criteria"):
        op.create_table("criteria",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id", ondelete="CASCADE"), index=True),
            sa.Column("competency_id", sa.Integer, sa.ForeignKey("competencies.id", ondelete="CASCADE"), index=True),
            sa.Column("scale_type", sa.String(20), nullable=False, server_default="one_to_five"),
            sa.Column("weight", sa.Float, nullable=False, server_default="0"),
            sa.Column("auto_weight", sa.Boolean, nullable=False, server_default=sa.text("1")),
        )

    if not table_exists(conn, "tasks"):
        op.create_table("tasks",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id", ondelete="CASCADE"), index=True),
            sa.Column("function_id", sa.Integer, sa.ForeignKey("functions.id", ondelete="SET NULL"), index=True, nullable=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text),
            sa.Column("weight", sa.Float, nullable=False, server_default="0"),
            sa.Column("auto_weight", sa.Boolean, nullable=False, server_default=sa.text("1")),
            sa.Column("mandatory_for_level", sa.Boolean, nullable=False, server_default=sa.text("0")),
            sa.Column("mandatory_for_apex", sa.Boolean, nullable=False, server_default=sa.text("0")),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
        )

    if not table_exists(conn, "task_criteria"):
        op.create_table("task_criteria",
            sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("criterion_id", sa.Integer, sa.ForeignKey("criteria.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("weight", sa.Float, nullable=False, server_default="0"),
            sa.Column("auto_weight", sa.Boolean, nullable=False, server_default=sa.text("1")),
        )

    if not table_exists(conn, "employees"):
        op.create_table("employees",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("full_name", sa.String(200), nullable=False),
            sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id", ondelete="CASCADE")),
            sa.Column("position_id", sa.Integer, sa.ForeignKey("positions.id", ondelete="CASCADE")),
            sa.Column("hired_at", sa.Date, nullable=False),
            sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
            sa.Column("birth_date", sa.Date),
            sa.Column("last_promotion_at", sa.Date),
        )

    if not table_exists(conn, "scoring_rules"):
        op.create_table("scoring_rules",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("department_id", sa.Integer, sa.ForeignKey("departments.id", ondelete="CASCADE")),
            sa.Column("scale_type", sa.String(20), nullable=False),
            sa.Column("rule_json", sa.Text, nullable=False),
        )

    if not table_exists(conn, "scores"):
        op.create_table("scores",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("employee_id", sa.Integer, sa.ForeignKey("employees.id", ondelete="CASCADE"), index=True),
            sa.Column("date", sa.Date, nullable=False),
            sa.Column("criterion_id", sa.Integer, sa.ForeignKey("criteria.id", ondelete="SET NULL"), nullable=True),
            sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True),
            sa.Column("raw_value", sa.Float),
            sa.Column("normalized", sa.Float),
        )

    if not table_exists(conn, "level_configs"):
        op.create_table("level_configs",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("L1_threshold", sa.Float, nullable=False, server_default="0.85"),
            sa.Column("L2_threshold", sa.Float, nullable=False, server_default="0.60"),
            sa.Column("order_desc", sa.Boolean, nullable=False, server_default=sa.text("1")),
        )

    if not table_exists(conn, "position_baselines"):
        op.create_table("position_baselines",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("position_id", sa.Integer, sa.ForeignKey("positions.id", ondelete="CASCADE")),
            sa.Column("competency_id", sa.Integer, sa.ForeignKey("competencies.id", ondelete="CASCADE")),
            sa.Column("min_level", sa.Integer, nullable=False, server_default="3"),
            sa.Column("min_score", sa.Float, nullable=False, server_default="0"),
            sa.Column("is_core", sa.Boolean, nullable=False, server_default=sa.text("0")),
        )

    if not table_exists(conn, "position_baseline_required_tasks"):
        op.create_table("position_baseline_required_tasks",
            sa.Column("position_baseline_id", sa.Integer, sa.ForeignKey("position_baselines.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
        )

    if not table_exists(conn, "position_apex_rules"):
        op.create_table("position_apex_rules",
            sa.Column("position_id", sa.Integer, sa.ForeignKey("positions.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("rule_json", sa.Text, nullable=False),
        )

    if not table_exists(conn, "visibility"):
        op.create_table("visibility",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("employee_id", sa.Integer, sa.ForeignKey("employees.id", ondelete="CASCADE")),
            sa.Column("competency_id", sa.Integer, sa.ForeignKey("competencies.id", ondelete="CASCADE"), nullable=True),
            sa.Column("criterion_id", sa.Integer, sa.ForeignKey("criteria.id", ondelete="CASCADE"), nullable=True),
            sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True),
            sa.Column("is_visible", sa.Boolean, nullable=False, server_default=sa.text("1")),
        )

    if not table_exists(conn, "plans"):
        op.create_table("plans",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("employee_id", sa.Integer, sa.ForeignKey("employees.id", ondelete="CASCADE"), index=True),
            sa.Column("period_start", sa.Date, nullable=False),
            sa.Column("period_end", sa.Date, nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
            sa.Column("completion_pct", sa.Integer, nullable=False, server_default="10"),
            sa.Column("recommend_promotion", sa.Boolean, nullable=False, server_default=sa.text("0"))
        )

    if not table_exists(conn, "plan_items"):
        op.create_table("plan_items",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("plan_id", sa.Integer, sa.ForeignKey("plans.id", ondelete="CASCADE"), index=True),
            sa.Column("competency_id", sa.Integer, sa.ForeignKey("competencies.id", ondelete="SET NULL"), nullable=True),
            sa.Column("function_id", sa.Integer, sa.ForeignKey("functions.id", ondelete="SET NULL"), nullable=True),
            sa.Column("criterion_id", sa.Integer, sa.ForeignKey("criteria.id", ondelete="SET NULL"), nullable=True),
            sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True),
            sa.Column("expected_result", sa.Text),
            sa.Column("employee_report", sa.Text),
            sa.Column("is_visible_to_employee", sa.Boolean, nullable=False, server_default=sa.text("1")),
        )

def downgrade() -> None:
    # оставляем недеструктивно для безопасности
    pass
