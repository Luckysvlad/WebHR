
# UI-навигатор + доступ к админке

1. Замените `app/templates/base.html` и `app/templates/dashboard.html` из этого патча — появится левый сайдбар с разделами.
2. Дайте админ-доступ (если /admin/rbac отдаёт 403):
   ```bash
   python -m scripts.grant_admin_all
   ```
3. Перезапустите сервер.
4. Проверьте разделы:
   - /plans
   - /matrices/competencies, /matrices/criteria
   - /settings/levels
   - /reports (+ /reports/employee/{id}?fmt=pdf|xlsx)
   - /admin/rbac
