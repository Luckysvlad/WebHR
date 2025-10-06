from __future__ import annotations
from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.core.rbac import require_permission
from app.core.models import LevelConfig

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/levels", dependencies=[Depends(require_permission("manage_levels"))])
def levels_view(request: Request, db: Session = Depends(get_db)):
    cfg = db.execute(select(LevelConfig)).scalars().first()
    return request.app.state.templates.TemplateResponse("settings/levels.html", {"request": request, "cfg": cfg})

@router.post("/levels", dependencies=[Depends(require_permission("manage_levels"))])
def levels_save(L1_threshold: float = Form(0.85), L2_threshold: float = Form(0.60), order_desc: bool = Form(True), db: Session = Depends(get_db)):
    cfg = db.execute(select(LevelConfig)).scalars().first()
    if not cfg:
        cfg = LevelConfig(L1_threshold=L1_threshold, L2_threshold=L2_threshold, order_desc=order_desc)
    else:
        cfg.L1_threshold = L1_threshold
        cfg.L2_threshold = L2_threshold
        cfg.order_desc = order_desc
    db.add(cfg); db.commit()
    return {"ok": True}
