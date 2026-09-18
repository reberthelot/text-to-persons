"""Configuration settings for the Text-to-Persons application.

Settings are loaded from environment variables with sensible defaults
suitable for local development and containerized testing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Application runtime settings and external service configuration.

    Parameters
    ----------
    service_base_url : str
        Base URL of the external person extraction Web service.
    service_endpoint : str
        Endpoint path of the person extraction service (e.g. '/v1/extract-persons').
    service_timeout_seconds : float
        Timeout duration in seconds for HTTP requests to the external service.
    base_dir : Path
        Absolute path to the project root directory.
    template_dir : Path
        Path to the HTML templates directory.
    static_dir : Path
        Path to the static assets directory.
    """

    service_base_url: str = os.environ.get("PERSON_SERVICE_URL", "http://localhost:8000").rstrip("/")
    service_endpoint: str = os.environ.get("PERSON_SERVICE_ENDPOINT", "/v1/extract-persons")
    service_timeout_seconds: float = float(os.environ.get("PERSON_SERVICE_TIMEOUT_SECONDS", "10.0"))
    service_timeout_seconds: float = float(os.environ.get("PERSON_SERVICE_TIMEOUT_SECONDS", "60.0"))

    # Project paths
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    template_dir: Path = base_dir / "frontend" / "templates"
    static_dir: Path = base_dir / "frontend" / "static"


settings = Settings()

