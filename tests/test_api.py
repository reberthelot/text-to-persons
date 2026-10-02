"""Integration tests for FastAPI frontend and API routes.

The ``client`` fixture (see conftest.py) runs the application lifespan, which
creates the pooled HTTP client consumed by the proxy routes.
"""

from unittest.mock import AsyncMock, patch

from src.app.models import ExtractPersonsResponse


def test_get_health(client) -> None:
    """The /health liveness probe must answer 200 with no side effects."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_index_page(client) -> None:
    """The root endpoint should render HTML with title and static links."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Text → Persons (Demo Frontend)" in response.text
    assert "/static/css/style.css" in response.text
    assert "/static/js/app.js" in response.text


def test_static_assets(client) -> None:
    """Static assets CSS and JS must be served properly."""
    css_res = client.get("/static/css/style.css")
    assert css_res.status_code == 200
    assert "--dtu-red" in css_res.text

    js_res = client.get("/static/js/app.js")
    assert js_res.status_code == 200
    assert "fetchJson" in js_res.text


def test_get_metrics_endpoint(client) -> None:
    """The /api/metrics endpoint returns operational metrics."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "service_base_url" in data


def test_extract_persons_validation_error(client) -> None:
    """Missing or empty text input raises 422 validation error."""
    response = client.post("/api/extract-persons", json={"text": ""})
    assert response.status_code == 422


@patch("src.app.routes.api.call_person_service", new_callable=AsyncMock)
def test_extract_persons_mocked_success(mock_call: AsyncMock, client) -> None:
    """Successful external service call proxies the persons list and latency."""
    mock_call.return_value = (ExtractPersonsResponse(persons=["Albert Einstein"]), 42.5)

    response = client.post("/api/extract-persons", json={"text": "Albert Einstein was a physicist."})
    assert response.status_code == 200
    data = response.json()
    assert data["persons"] == ["Albert Einstein"]
    assert data["_meta"]["latency_ms"] == 42.5

