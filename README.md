# WebHR — готовая сборка

## Установка (Windows)
```bat
python -m venv myenv
myenv\Scripts\activate
pip install -U pip
pip install -r requirements.txt

alembic upgrade head
python -m scripts.seed_admin

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Логин по умолчанию: **admin / admin123**.
