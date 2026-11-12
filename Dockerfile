# ==============================================================================
# Multi-stage / Ultra-lean Dockerfile for Text-to-Persons
# ==============================================================================

# Base image with Python 3.11 on Alpine Linux
FROM python:3.11-alpine3.24 AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install shared dependencies (fastapi, uvicorn, httpx, pydantic, python-dotenv,
# jinja2 for the frontend templates)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Non-root runtime user (busybox adduser on Alpine), inherited by both targets.
RUN adduser -D -H -u 10001 -s /sbin/nologin appuser
USER appuser

# ------------------------------------------------------------------------------
# Target 1: Extraction Microservice (Port 8000)
# Minimal footprint: application code only (tests are not shipped in images)
# ------------------------------------------------------------------------------
FROM base AS extractor

COPY src/extractor/ src/extractor/
COPY src/app/models.py src/app/models.py
COPY src/app/__init__.py src/app/__init__.py

EXPOSE 8000

# Liveness probe: GET /health (see src/extractor/server.py).
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"

# Single worker on purpose: the pooled HTTP client and extractor live on
# app.state. Scale with replicas, not workers.
CMD ["uvicorn", "src.extractor.server:app", "--host", "0.0.0.0", "--port", "8000"]

# ------------------------------------------------------------------------------
# Target 2: Frontend & Benchmark Service (Port 8080)
# Jinja2 is a shared direct dependency installed from requirements.txt
# ------------------------------------------------------------------------------
FROM base AS frontend

COPY src/app/ src/app/
COPY frontend/ frontend/
COPY main.py .

ENV PERSON_SERVICE_URL="http://extractor:8000"
EXPOSE 8080

# Liveness probe: GET /health (see src/app/routes/frontend.py).
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=4)"

# Single worker on purpose: in-process benchmark state and metrics.
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
