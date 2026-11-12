"""FastAPI application factory and entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.app.config import settings
from src.app.routes.api import router as api_router
from src.app.routes.frontend import router as frontend_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the shared pooled HTTP client at startup, close it at shutdown.

    Replaces the previous one-client-per-request pattern: connection pooling
    and keep-alive reuse now apply to every proxy call. The request timeout
    stays configurable per call (``PERSON_SERVICE_TIMEOUT_SECONDS``).
    """
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app.state.http_client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.http_client.aclose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Mounts static assets, registers frontend page routes and backend API
    endpoints.

    Returns
    -------
    FastAPI
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Text → Persons Demo Frontend",
        description="A minimal frontend web app to demonstrate/test an external person-extraction service.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Mount static assets (CSS, JS)
    app.mount(
        "/static",
        StaticFiles(directory=str(settings.static_dir)),
        name="static",
    )

    # Register routers
    app.include_router(frontend_router)
    app.include_router(api_router)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("src.app.main:app", host="127.0.0.1", port=8080, reload=True)

