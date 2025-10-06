from __future__ import annotations
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.models import User

router = APIRouter(prefix="/plans", tags=["plans"])

def _user(request: Request, db: Session):
    uid = request.session.get("user_id")
    return db.get(User, uid) if uid else None

@router.get("")
def plans_index(request: Request, db: Session = Depends(get_db)):
    user = _user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    sample = {"quarter": "Q4", "year": 2025, "items": []}
    return request.app.state.templates.TemplateResponse("plans/index.html", {"request": request, "user": user, "plan": sample})
