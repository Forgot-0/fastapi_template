FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы миграций и конфиг Alembic
COPY alembic.ini /app/
COPY migrations/ /app/migrations/

# Копируем код приложения
COPY app/ /app/app/

# Прогоняем миграции перед запуском и запускаем uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"]
