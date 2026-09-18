# Text → Persons Frontend & Benchmark Service

A modular, lightweight, and pedagogic frontend Web application built with **FastAPI**, **Jinja2**, and modern vanilla JavaScript.

This application provides an intuitive interactive interface and an automated evaluation suite to demonstrate and benchmark independently developed Named Entity Recognition (NER) services (such as containerized LLM-powered microservices extracting person names from text).

---

## 🏛 Project Architecture

The project adheres to professional separation of concerns, decoupling UI assets, API routing, external client services, data schemas, and domain utilities:

```text
text-to-persons/
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css            # DTU-themed CSS (variables, responsive layout, cards)
│   │   └── js/
│   │       └── app.js               # Asynchronous API requests, test runner & UI updates
│   └── templates/
│       └── index.html               # Semantic HTML5 template rendered via Jinja2
├── src/
│   └── app/
│       ├── __init__.py              # Package init containing teacher assignment specifications
│       ├── config.py                # Environment-driven configuration dataclass
│       ├── models.py                # Strict Pydantic v2 schemas for requests & responses
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── dataset.py           # 38-example benchmark dataset (English & Danish)
│       │   ├── metrics.py           # In-memory operational metrics collector
│       │   └── normalization.py     # Person entity normalization with doctests
│       ├── services/
│       │   ├── __init__.py
│       │   └── person_client.py     # Async HTTP client with pedagogic error diagnostics
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── frontend.py          # Frontend HTML view route ('/')
│       │   └── api.py               # REST API routes (/api/extract-persons, /api/metrics, /api/run-tests)
│       └── main.py                  # FastAPI application factory and entry point
├── tests/
│   ├── __init__.py
│   ├── test_normalization.py        # Unit tests for text normalization
│   ├── test_metrics.py              # Unit tests for operational metrics tracker
│   └── test_api.py                  # Integration tests for FastAPI endpoints
├── requirements.txt                 # Pinned runtime and development dependencies
└── README.md                        # Documentation and usage guide
```

---

## 🚀 Getting Started

### 1. Prerequisites & Environment

Activate your virtual environment (`MLvenv` is recommended):

```powershell
MLvenv
# Or using direct path:
# & "C:\Users\remib\Python-Environments\MLvenv\Scripts\Activate.ps1"
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration

The application communicates with the independently developed person extraction service. Configure it using environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PERSON_SERVICE_URL` | `http://localhost:8000` | Base URL of the external target service |
| `PERSON_SERVICE_ENDPOINT` | `/v1/extract-persons` | Endpoint path expecting `{"text": "..."}` |
| `PERSON_SERVICE_TIMEOUT_SECONDS` | `10.0` | Timeout duration for requests in seconds |

### 3. Running the Frontend Application

Start the web server using Uvicorn:

```bash
uvicorn src.app.main:app --port 8080 --reload
```

Or run directly with Python:

```bash
python -m src.app.main
```

Open your browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🧪 Testing and Verification

Run unit tests and integration tests with `pytest`:

```bash
pytest -v
```

Execute doctests on the normalization utilities:

```bash
python -m doctest -v src/app/utils/normalization.py
```

---

## 🔍 API Endpoints

- **`GET /`**: Serves the interactive web interface.
- **`POST /api/extract-persons`**: Proxy endpoint forwarding text to the external service:
  ```json
  // Request
  { "text": "Einstein and von Neumann meet each other." }
  // Response
  {
    "persons": ["Einstein", "von Neumann"],
    "_meta": { "latency_ms": 42.1 }
  }
  ```
- **`GET /api/metrics`**: In-memory operational metrics (total requests, success/fail counts, latencies).
- **`POST /api/run-tests`**: Runs the 38 benchmark test cases against the external service and outputs accuracy pass rate and latencies.

