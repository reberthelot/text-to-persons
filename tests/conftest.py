"""Shared pytest fixtures for the text-to-persons test suite."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.extractor.server import app as extractor_app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Yield a TestClient started inside a ``with`` block so the application
    lifespan runs (creates the pooled HTTP client on ``app.state``)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def extractor_client() -> Iterator[TestClient]:
    """Yield a TestClient for the standalone extraction microservice with its
    lifespan running (pooled HTTP client, extractor injectable on app.state)."""
    with TestClient(extractor_app) as test_client:
        yield test_client
