
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.db import Base, engine

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# --- Static ---
static_dir = Path(getattr(settings, "STATIC_DIR", "static"))
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# --- Templates (FIX) ---
templates_dir = Path(getattr(settings, "TEMPLATES_DIR", "templates"))
# Ensure directory exists or fallback to ./templates
if not templates_dir.exists():
    templates_dir = Path("templates")
app.state.templates = Jinja2Templates(directory=str(templates_dir))

# --- Sessions ---
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=getattr(settings, "SESSION_COOKIE_NAME", "session"),
    same_site="lax",
)

# --- DB bootstrap for safety (create tables if missing) ---
# This is safe with Alembic since CREATE TABLE IF NOT EXISTS logic is used by SQLAlchemy.
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # Don't block startup if DB bootstrap fails, let error middleware expose details later
    if settings.DEBUG:
        raise

# --- Routers ---
from app.routers import auth as auth_router  # noqa: E402
from app.routers import dashboard as dashboard_router  # noqa: E402
from app.routers import plans as plans_router  # noqa: E402
from app.routers import matrices as matrices_router  # noqa: E402

app.include_router(auth_router.router)
app.include_router(dashboard_router.router)
app.include_router(plans_router.router)
app.include_router(matrices_router.router)

# --- Simple favicon to avoid 404 noise ---
from fastapi import Response  # noqa: E402
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# --- Error middleware ---
@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception:
        if settings.DEBUG:
            raise
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# --- Root redirect ---
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/dashboard")

# --- Health ---
@app.get("/health")
async def health_check():
    return {"status": "healthy", "debug": settings.DEBUG}
