from __future__ import annotations
from starlette.templating import Jinja2Templates

# single templates instance; accessed as request.app.state.templates
templates = Jinja2Templates(directory="templates")

def get_templates():
    return templates

__all__ = ["templates", "get_templates"]
