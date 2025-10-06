from __future__ import annotations
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.models import User
from passlib.hash import bcrypt

router = APIRouter()

@router.get("/login")
def login_form(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.username == username, User.is_active == True)).scalars().first()
    if not user or not bcrypt.verify(password, user.password_hash):
        return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"}, status_code=400)
    request.session["user_id"] = user.id
    resp = RedirectResponse(url="/dashboard", status_code=303)
    return resp

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
