FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    PYTHONPATH=/code \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /code

# Минимальный набор пакетов для установки Poetry
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Кэшируем зависимости: меняются только при изменении pyproject/lock
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root --no-ansi --no-interaction

# Копируем код
COPY app ./app
COPY worker ./worker
COPY alembic ./alembic
COPY alembic.ini .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]