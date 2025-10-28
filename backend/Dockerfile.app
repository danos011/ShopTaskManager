# Файл: backend/Dockerfile.app

FROM python:3.11-slim

WORKDIR /app

# Копируем файл зависимостей из корня проекта (контекста сборки)
COPY ./requirements.txt ./requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код из корня проекта
COPY . /app

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
