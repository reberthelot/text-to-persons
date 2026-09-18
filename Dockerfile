# ==============================================================================
# Multi-stage / Ultra-lean Dockerfile for Text-to-Persons
# ==============================================================================

# Base image with Python 3.11 on Alpine Linux
FROM python:3.11-alpine3.24 AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install core shared dependencies (fastapi, uvicorn, httpx, pydantic, python-dotenv)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Target 1: Extraction Microservice (Port 8000)
# Minimal footprint: strictly core dependencies, no pytest, no jinja2
# ------------------------------------------------------------------------------
FROM base AS extractor

COPY src/extractor/ src/extractor/
COPY src/app/models.py src/app/models.py
COPY src/app/__init__.py src/app/__init__.py

EXPOSE 8000

CMD ["uvicorn", "src.extractor.server:app", "--host", "0.0.0.0", "--port", "8000"]

# ------------------------------------------------------------------------------
# Target 2: Frontend & Benchmark Service (Port 8080)
# Includes Jinja2 for HTML templating and Pytest for test execution
# ------------------------------------------------------------------------------
FROM base AS frontend

# Install frontend-specific dependencies (Jinja2, Pytest)
COPY requirements-frontend.txt .
RUN pip install --no-cache-dir -r requirements-frontend.txt

COPY src/app/ src/app/
COPY frontend/ frontend/
COPY tests/ tests/
COPY main.py .

ENV PERSON_SERVICE_URL="http://extractor:8000"
EXPOSE 8080

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
