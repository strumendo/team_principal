# TeamPrincipal Backend Dockerfile
# Multi-stage: dev and prod
# Dockerfile do Backend TeamPrincipal
# Multi-stage: dev e prod

# ---- Base ----
FROM python:3.12-slim AS base

WORKDIR /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

# ---- Development ----
FROM base AS dev

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---- Production ----
FROM base AS prod

RUN poetry install --no-interaction --no-ansi --no-root --only main

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
