"""Tests for the standalone person-extraction microservice (``src.extractor``).

The ``extractor_client`` fixture (see conftest.py) runs the extractor
application lifespan (pooled HTTP client, injectable extractor on app.state).
"""


def test_get_health(extractor_client):
    """Verify the /health liveness probe targeted by the Docker HEALTHCHECK."""
    response = extractor_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
