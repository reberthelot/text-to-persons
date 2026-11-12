"""Configuration settings for the Text-to-Persons application.

Settings are loaded from environment variables and an optional ``.env`` file
at the project root (handled natively by ``pydantic-settings``). Legacy env
names that do not match the field name are preserved through ``AliasChoices``
so existing Compose/Docker files keep working unchanged
(``PERSON_SERVICE_URL``, ``PERSON_SERVICE_ENDPOINT``,
``PERSON_SERVICE_TIMEOUT_SECONDS``).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings and external service configuration.

    Parameters
    ----------
    service_base_url : str
        Base URL of the external person extraction Web service.
    service_endpoint : str
        Endpoint path of the external person extraction service (e.g. '/v1/extract-persons').
    service_timeout_seconds : float
        Timeout duration in seconds for HTTP requests to the external service.
    base_dir : Path
        Absolute path to the project root directory.
    template_dir : Path
        Path to the HTML templates directory.
    static_dir : Path
        Path to the static assets directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated container env vars (PYTHONUNBUFFERED, ...)
    )

    service_base_url: str = Field(
        default="http://localhost:8000",
        validation_alias=AliasChoices("PERSON_SERVICE_URL", "service_base_url"),
    )
    service_endpoint: str = Field(
        default="/v1/extract-persons",
        validation_alias=AliasChoices("PERSON_SERVICE_ENDPOINT", "service_endpoint"),
    )
    service_timeout_seconds: float = Field(
        default=60.0,
        gt=0,
        validation_alias=AliasChoices(
            "PERSON_SERVICE_TIMEOUT_SECONDS", "service_timeout_seconds"
        ),
    )

    # Project paths (computed, not environment-driven)
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    template_dir: Path = base_dir / "frontend" / "templates"
    static_dir: Path = base_dir / "frontend" / "static"
    #: Root logging level (env ``LOG_LEVEL``), e.g. DEBUG, INFO, WARNING.
    log_level: str = "INFO"

    @field_validator("service_base_url", mode="after")
    @classmethod
    def _strip_trailing_slash(cls, value: str) -> str:
        """Normalize the base URL so path joining never yields a double slash."""
        return value.rstrip("/")

    @field_validator("log_level", mode="after")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        """Accept any case (``debug`` -> ``DEBUG``) and reject unknown levels."""
        level = value.upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"unknown log level: {value!r}")
        return level


settings = Settings()
