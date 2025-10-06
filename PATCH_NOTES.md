
# WebHR Hotfix — templates initialization

**Что исправлено**
- Инициализация Jinja2-шаблонов: теперь в `app.state.templates` гарантированно
  помещается `Jinja2Templates(...)`, из-за чего переставала работать страница `/login`
  с ошибкой `AttributeError: 'State' object has no attribute 'templates'`.
- Добавлен легкий обработчик `/favicon.ico` (204), чтобы убрать 404 в логах.
- `Base.metadata.create_all(bind=engine)` на старте — безопасная защита на случай отсутствующих таблиц
  (не конфликтует с Alembic).

**Как применить**
1. Распакуйте архив в корень вашего проекта, заменив файл `app/main.py`.
2. Убедитесь, что в конфиге указана директория шаблонов (или по умолчанию используется `./templates`).
3. Запустите сервер тем же интерпретатором, что и миграции:
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

**Ожидаемый результат**
- Переход на `/login` возвращает 200 OK.
- Больше нет `AttributeError: ... state.templates`.
- В логах пропадает 404 по `/favicon.ico`.
