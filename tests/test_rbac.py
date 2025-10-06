from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from app.core.rbac import require_permission
app=FastAPI()
@app.get('/secure', dependencies=[Depends(require_permission('some_perm'))])
def secure():
    return {'ok':True}

def test_rbac_dep_unauth():
    client=TestClient(app); r=client.get('/secure'); assert r.status_code in (401,403)
