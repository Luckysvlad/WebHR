# MIGRATION_NOTES

## Текущее состояние
- Единая голова Alembic: `5150fc890f5b_merge_heads_auto_generated.py` (merge двух веток `fix_roles_description_20251006` и `add_notifications_20251007`).
- Базовые ревизии:
  - `20251004_182728_init.py` — базовые таблицы (departments, employees, ...), SQLite-safe.
  - `20251005_leveling_extension.py` — расширения (hired_at, level) с проверками колонок.
  - `20251006_init_auth.py` — users/roles/permissions + связи (idempotent).
  - `20251006_fix_roles_description.py` — добавляет `roles.description` и линеаризует зависимость.
  - `20251007_add_notifications.py` — таблица `notifications` (FK на users).
  - `5150fc890f5b_merge_heads_auto_generated.py` — merge двух голов.

## Почему ранее были multiple heads
Ревизии `fix_roles_description_20251006` и `add_notifications_20251007` исходно ссылались каждая на свой `down_revision`. Добавлена merge‑ревизия, зависящая от обеих, без DDL (upgrade/downgrade пустые).

## Если снова появится «multiple heads»
1. `alembic heads` — посмотреть идентификаторы.
2. Создать merge-файл по образцу `5150fc890f5b_merge_heads_auto_generated.py` с tuple в `down_revision = ('head_A', 'head_B')`.
3. В `upgrade()/downgrade()` оставить `pass`.

## SQLite‑безопасные приёмы в миграциях
- Перед `op.create_table` и `op.add_column` используем `sa.inspect(bind)` и проверяем наличие таблиц/колонок.
- DDL в SQLite не оборачивается транзакциями — избегаем последовательных `ALTER` без проверок.
