"""Unit tests for the proxy client error branches (502 / 504 mapping).

The lifespan-managed pooled client is swapped for one backed by
``httpx.MockTransport`` so each failure mode (connection refused, timeout,
upstream error, malformed body) can be simulated deterministically without a
live extractor service.
"""

import httpx
from fastapi.testclient import TestClient

from src.app.main import app


def _install_transport(handler: object) -> None:
    """Replace the pooled client on ``app.state`` with a mock-transport one.

    The real client created by the lifespan is left to the lifespan's
    shutdown hook (the replacement is closed there instead).
    """
    app.state.http_client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler)  # type: ignore[arg-type]
    )


def test_connect_error_returns_502(client: TestClient) -> None:
    """A refused connection maps to an explicit 502 with pedagogic detail."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    _install_transport(handler)
    response = client.post("/api/extract-persons", json={"text": "Einstein"})
    assert response.status_code == 502
    detail = response.json()["detail"]
    assert "Could not connect" in detail
    assert "ConnectError" in detail


def test_connect_timeout_returns_504(client: TestClient) -> None:
    """Regression: ConnectTimeout derives from TimeoutException (not ReadTimeout)."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out", request=request)

    _install_transport(handler)
    response = client.post("/api/extract-persons", json={"text": "Einstein"})
    assert response.status_code == 504
    detail = response.json()["detail"]
    assert "did not respond before the timeout" in detail
    assert "PERSON_SERVICE_TIMEOUT_SECONDS" in detail


def test_read_timeout_returns_504(client: TestClient) -> None:
    """A mid-request read timeout also maps to 504."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timed out", request=request)

    _install_transport(handler)
    response = client.post("/api/extract-persons", json={"text": "Einstein"})
    assert response.status_code == 504


def test_upstream_http_error_returns_502(client: TestClient) -> None:
    """A non-2xx upstream status is proxied as 502 with the body echoed."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="upstream exploded")

    _install_transport(handler)
    response = client.post("/api/extract-persons", json={"text": "Einstein"})
    assert response.status_code == 502
    detail = response.json()["detail"]
    assert "503" in detail
    assert "upstream exploded" in detail


def test_invalid_json_returns_502(client: TestClient) -> None:
    """A 2xx response with a non-JSON body maps to 502."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="<html>not json</html>",
            headers={"content-type": "application/json"},
        )

    _install_transport(handler)
    response = client.post("/api/extract-persons", json={"text": "Einstein"})
    assert response.status_code == 502
    assert "not valid JSON" in response.json()["detail"]


def test_wrong_shape_returns_502(client: TestClient) -> None:
    """A JSON body without the expected ``persons`` list maps to 502."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"names": ["Einstein"]})

    _install_transport(handler)
    response = client.post("/api/extract-persons", json={"text": "Einstein"})
    assert response.status_code == 502
    assert "not in the expected format" in response.json()["detail"]
