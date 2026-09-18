# ==============================================================================
# Multi-stage / Multi-service Dockerfile for Text-to-Persons
#
# Targets:
#   1. frontend   : Serves Jinja2 templates & benchmark UI on port 8080
#   2. extractor  : Microservice performing NER extraction on port 8000
# ==============================================================================

# Base image with lean Python runtime
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if required, then Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy complete application source code
COPY src/ src/
COPY frontend/ frontend/
COPY main.py .

# ------------------------------------------------------------------------------
# Target 1: Frontend & Benchmark Service (Default)
# ------------------------------------------------------------------------------
FROM base AS frontend

ENV PERSON_SERVICE_URL="http://extractor:8000"
EXPOSE 8080

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8080"]

# ------------------------------------------------------------------------------
# Target 2: Extraction Microservice
# ------------------------------------------------------------------------------
FROM base AS extractor

EXPOSE 8000

CMD ["uvicorn", "src.extractor.server:app", "--host", "0.0.0.0", "--port", "8000"]

