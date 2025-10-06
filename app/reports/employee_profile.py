from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import select
from app.core.models import Competency
from app.services.scoring import competency_score
def make_employee_profile_pdf(db, emp, path):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    y = h - 40
    c.setFont("Helvetica-Bold", 14); c.drawString(40, y, f"Профиль: {emp.full_name}"); y -= 20
    c.setFont("Helvetica", 10); c.drawString(40, y, f"Отдел: {emp.department_id}  Должность: {emp.position_id}"); y -= 20
    comps = db.execute(select(Competency)).scalars().all()
    for comp in comps:
        s = competency_score(db, emp.id, comp.id)
        c.drawString(50, y, f"{comp.name}: {s:.2f}"); y -= 14
        if y < 50: c.showPage(); y = h - 40
    c.showPage(); c.save()
