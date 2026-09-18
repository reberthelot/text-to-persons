"""FastAPI application factory and entry point."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.app.config import settings
from src.app.routes.api import router as api_router
from src.app.routes.frontend import router as frontend_router


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

