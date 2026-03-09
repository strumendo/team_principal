# TeamPrincipal Backend Dockerfile
# Multi-stage: deps, dev, prod
# Dockerfile do Backend TeamPrincipal
# Multi-stage: deps, dev, prod

# ---- Dependencies ----
FROM python:3.12-slim AS deps

WORKDIR /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

# ---- Development ----
FROM deps AS dev

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---- Production ----
FROM deps AS prod

RUN poetry install --no-interaction --no-ansi --no-root --only main

COPY . .

# Non-root user for security / Usuario nao-root para seguranca
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser && \
    mkdir -p /app/uploads && chown -R appuser:appgroup /app/uploads

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
