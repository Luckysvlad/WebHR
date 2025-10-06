from openpyxl import Workbook
from sqlalchemy import select
from app.core.models import Competency
from app.services.scoring import competency_score
def make_employee_profile_xlsx(db, emp, path):
    wb = Workbook(); ws = wb.active; ws.title = "Profile"
    ws.append(["Сотрудник", emp.full_name]); ws.append(["Должность ID", emp.position_id]); ws.append(["Отдел ID", emp.department_id]); ws.append([]); ws.append(["Компетенция","Оценка"])
    comps = db.execute(select(Competency)).scalars().all()
    for comp in comps:
        s = competency_score(db, emp.id, comp.id)
        ws.append([comp.name, round(s,3)])
    wb.save(path)
