from __future__ import annotations
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_utils import templates
from app.core.rbac import require_perm

router = APIRouter(prefix="/manager")

@router.get("/probation", response_class=HTMLResponse, dependencies=[Depends(require_perm("employees.view"))])
def probation(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("stub.html", {"request": request, "title": "План испытательного срока", "body": "Здесь будет логика планов."})
