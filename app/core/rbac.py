from __future__ import annotations
from typing import Callable, Generator
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

try:
    from app.core.db import SessionLocal
except Exception:
    SessionLocal = None  # type: ignore

from app.core.models import User  # type: ignore


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("SessionLocal is not configured; check app.core.db")
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_obj = getattr(request.state, "user", None)
    if isinstance(user_obj, User):
        if not user_obj.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
        return user_obj

    user_id = None
    try:
        user_id = request.session.get("user_id")
    except Exception:
        user_id = None

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def require_login() -> Callable[[User], User]:
    def _dep(user: User = Depends(get_current_user)) -> User:
        return user
    return _dep


def _user_has_permission(user: User, code: str) -> bool:
    if getattr(user, "is_superuser", False):
        return True
    for role in getattr(user, "roles", []) or []:
        for perm in getattr(role, "permissions", []) or []:
            if getattr(perm, "code", None) == code:
                return True
    return False


def require_permission(code: str) -> Callable[[User], User]:
    def _dep(user: User = Depends(get_current_user)) -> User:
        if not _user_has_permission(user, code):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return _dep


def require_perm(code: str) -> Callable[[User], User]:
    return require_permission(code)
