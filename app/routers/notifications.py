from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.db import get_db
from app.core.models import Notification
from app.core.rbac import require_perm
from app.templates_utils import templates

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_class=HTMLResponse, dependencies=[Depends(require_perm("notifications.view"))])
def list_notifs(request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        return RedirectResponse("/login", status_code=303)
    items = db.execute(select(Notification).where(Notification.user_id==user.id).order_by(Notification.created_at.desc())).scalars().all()
    return templates.TemplateResponse("notifications.html", {"request": request, "items": items})
