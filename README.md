# Text -> Persons Service & Benchmark Platform

A modular and lightweight application built with FastAPI, Jinja2, and vanilla JavaScript for person entity extraction (NER) using Large Language Models.

The repository includes both the frontend benchmark interface and the backend extraction microservice powered by an OpenAI-compatible LLM endpoint.

---

## Architecture

The project decouples the frontend benchmarking platform from the standalone person extraction microservice:

```text
03-text-to-persons/
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css            # Stylesheet (DTU theme, responsive grid)
│   │   └── js/
│   │       └── app.js               # Asynchronous client, test runner, and UI rendering
│   └── templates/
│       └── index.html               # Semantic HTML5 template rendered with Jinja2
├── src/
│   ├── app/                         # Frontend & benchmark orchestrator
│   │   ├── config.py                # Application runtime configuration
│   │   ├── models.py                # Pydantic v2 data contracts
│   │   ├── main.py                  # Frontend FastAPI app factory
│   │   ├── routes/
│   │   │   ├── frontend.py          # HTML view endpoint ('/')
│   │   │   └── api.py               # REST proxy and test suite runner endpoints
│   │   ├── services/
│   │   │   └── person_client.py     # HTTP client communicating with the extractor
│   │   └── utils/
│   │       ├── dataset.py           # Bilingual benchmark test suite (English & Danish)
│   │       ├── metrics.py           # Operational latency and throughput metrics
│   │       └── normalization.py     # Text and entity normalization helpers
│   └── extractor/                   # Extraction microservice
│       ├── config.py                # LLM API settings and self-consistency parameters
│       ├── prompts.py               # Domain-specific NER prompt and edge-case rules
│       ├── server.py                # Standalone FastAPI service on port 8000
│       └── service.py               # Extraction engine with structured output and voting
├── tests/
│   ├── test_normalization.py        # Unit tests for text normalization
│   ├── test_metrics.py              # Unit tests for metric tracking
│   └── test_api.py                  # Integration tests for API endpoints
├── main.py                          # Frontend application launcher
├── requirements.txt                 # Pinned dependencies
├── Dockerfile                       # Multi-stage container build (frontend & extractor)
└── README.md                        # Project documentation
```

---

## Extraction Engine Improvements

The extraction service (`src/extractor`) employs two main techniques to achieve high accuracy and robustness:

### 1. OpenAI-Compatible Structured Outputs (`json_schema`)
To prevent malformed JSON responses and schema drift, extraction requests configure `response_format` with `type: "json_schema"` and `strict: True`:

```json
{
  "type": "json_schema",
  "json_schema": {
    "name": "extract_persons_response",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {
        "persons": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Unique list of person names extracted from the text."
        }
      },
      "required": ["persons"],
      "additionalProperties": false
    }
  }
}
```

This enforces schema conformity directly during LLM token generation, guaranteeing that output text parses cleanly into the target schema without post-processing failures.

### 2. Self-Consistency with Majority Voting
Stochastic decoding variability is mitigated through sample-and-vote aggregation:
- **Parallel Sampling**: The service requests `n = 8` candidate predictions at a moderately higher temperature (`temperature = 0.7`) in a single network round-trip.
- **Majority Voting**: Extracted entities from all candidates are collected and deduplicated per sample. An entity is selected for the final prediction if and only if it appears in at least 50% of the generated choices (configurable via `CONSISTENCY_THRESHOLD`).
- **Deterministic Fallback**: If `SELF_CONSISTENCY_SAMPLES` is set to `1`, the engine defaults to greedy decoding (`temperature = 0.0`).

---

## Configuration

Configuration values are managed via environment variables or a `.env` file at the project root.

### Extraction Microservice Settings (`src/extractor/config.py`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `CAMPUSAI_API_KEY` | `""` | Bearer API key for the OpenAI-compatible LLM endpoint |
| `CAMPUSAI_API_URL` | `https://api.campusai.compute.dtu.dk/v1` | Base URL of the completion API |
| `CAMPUSAI_MODEL` | `google/gemma-4-26b-a4b` | Model name used for extraction |
| `SELF_CONSISTENCY_SAMPLES` | `8` | Number of parallel completions requested (`n`) |
| `EXTRACTOR_TEMPERATURE` | `0.7` | Sampling temperature for self-consistency |
| `CONSISTENCY_THRESHOLD` | `0.5` | Minimum vote ratio required to keep an entity |
| `EXTRACTOR_TIMEOUT_SECONDS` | `60.0` | HTTP request timeout for LLM calls |
| `LOG_LEVEL` | `INFO` | Root log level (`DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL`, case-insensitive) |

### Frontend & Benchmark Settings (`src/app/config.py`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PERSON_SERVICE_URL` | `http://localhost:8000` | Target URL of the extraction microservice |
| `PERSON_SERVICE_ENDPOINT` | `/v1/extract-persons` | Endpoint path on the extraction service |
| `PERSON_SERVICE_TIMEOUT_SECONDS` | `60.0` | Timeout for proxying extraction requests |
| `LOG_LEVEL` | `INFO` | Root log level (case-insensitive) |

---

## Getting Started

### 1. Installation

Install dependencies using Python 3.11+ (Jinja2 for the frontend templates is a shared direct dependency of `requirements.txt`):

```bash
# Core dependencies (microservice, shared runtime & frontend)
pip install -r requirements.txt

# Only needed to run the test suite (dev group declared in pyproject.toml)
pip install pytest
```

### 2. Running the Services

#### Start the Extraction Microservice (Port 8000)

```bash
uvicorn src.extractor.server:app --port 8000 --reload
```

#### Start the Frontend Application (Port 8080)

In a separate terminal:

```bash
uvicorn main:app --port 8080 --reload
```

Navigate to: `http://localhost:8080`

### 3. Docker Deployment

The project provides a multi-stage `Dockerfile` with isolated targets for `extractor` and `frontend`. Each target copies only its relevant codebase while sharing the base Python runtime and dependency layers.

#### Using Docker Compose (Recommended)

Ensure `.env` contains the required credentials (`CAMPUSAI_API_KEY`), then build and launch both containers:

```bash
# Build and start services in the background
docker compose up --build -d

# Check service logs
docker compose logs -f

# Stop containers
docker compose down
```

The frontend will be available at `http://localhost:8080` and the extractor at `http://localhost:8000`.

`compose.yaml` starts the extractor first and waits for its `/health` probe to turn **healthy** (`depends_on: condition: service_healthy`) before starting the frontend. Both containers run as a **non-root** user (`appuser`, uid 10001), expose `GET /health` for the Docker `HEALTHCHECK`, and use a **single uvicorn worker** on purpose (pooled HTTP clients, in-process metrics and benchmark state).

#### Building and Running Images Individually

If you prefer building and executing individual containers with standard Docker commands:

1. **Extraction Microservice**:
   ```bash
   # Build the extractor target
   docker build --target extractor -t person-extractor .

   # Run container with environment variables
   docker run -d --name person-extractor -p 8000:8000 --env-file .env person-extractor
   ```

2. **Frontend & Benchmark Service**:
   ```bash
   # Build the frontend target
   docker build --target frontend -t text-to-persons-ui .

   # Run container linked to the host network or custom bridge
   docker run -d --name text-to-persons-ui -p 8080:8080 -e PERSON_SERVICE_URL="http://localhost:8000" text-to-persons-ui
   ```

---

## Testing & Validation

### Automated Unit Tests

Execute the test suite with `pytest`:

```bash
pytest -v
```

Dependencies are pinned with `uv` (`pyproject.toml` + `uv.lock`). After a dependency change, refresh the lock and the Docker build files:

```bash
uv lock
uv export --no-hashes --no-dev -o requirements.txt
```

### Normalization Doctests

Run doctests verifying string normalization and edge-case behavior:

```bash
python -m doctest -v src/app/utils/normalization.py
```

---

## API Reference

### Extraction Microservice (`http://localhost:8000`)
- **`POST /v1/extract-persons`**: Directly extracts persons from the provided text payload:
  ```json
  // Request
  { "text": "Einstein and von Neumann meet each other." }

  // Response
  { "persons": ["Einstein", "von Neumann"] }
  ```

### Frontend Proxy & Benchmark API (`http://localhost:8080`)
- **`GET /`**: Serves the interactive Web interface.
- **`POST /api/extract-persons`**: Forwards text to the extraction service and returns detected entities along with latency telemetry (`_meta.latency_ms`).
- **`GET /api/metrics`**: Returns in-memory operational metrics (total requests, success/failure counts, average latency).
- **`POST /api/run-tests`**: Runs the 40-case bilingual benchmark dataset against the configured service and returns detailed pass/fail statistics.
