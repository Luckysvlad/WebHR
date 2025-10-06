from app.core.db import SessionLocal, engine, Base
from app.core.seed import run as seed

def setup_module():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as s:
        seed(s)
        s.commit()

def test_entities_created():
    from app.core.models import Department, Position, Employee, Role, Permission, PlanTemplate
    with SessionLocal() as s:
        assert s.query(Department).count() >= 1
        assert s.query(Position).count() >= 1
        assert s.query(Employee).count() >= 1
        assert s.query(Role).count() >= 1
        assert s.query(Permission).count() >= 1
        assert s.query(PlanTemplate).count() >= 1
