from app.routers import plans, matrices, levels, reports, admin_rbac
app.include_router(plans.router)
app.include_router(matrices.router)
app.include_router(levels.router)
app.include_router(reports.router)
app.include_router(admin_rbac.router)
