# Alembic: fix "Multiple head revisions"

**What I changed**
- `alembic/versions/20251006_init_auth.py` now has `down_revision = 'leveling_extension_20251005'`.
  Это выстраивает единую цепочку миграций и убирает ошибку Multiple heads.

**Что делать у себя**
1. Замените файлы патча в проекте.
2. Посмотрите текущие головы:
   ```bash
   alembic heads
   ```
   Должна остаться одна голова с ревизией `init_auth_20251006`.
3. Примените миграции:
   ```bash
   alembic upgrade head
   ```
4. Засидируйте админа:
   ```bash
   python -m scripts.seed_admin
   ```

**Если `alembic heads` всё ещё выводит 2 головы**
Смерджите их:
```bash
# подставьте реальные ревизии из вывода 'alembic heads'
alembic revision --merge -m "merge heads" <rev_id_1> <rev_id_2>
alembic upgrade head
```