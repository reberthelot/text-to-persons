"""Configuration settings for the Person Extractor Service.

Settings are loaded from environment variables and an optional ``.env`` file
at the project root, handled natively by ``pydantic-settings`` (replaces the
former manual ``load_dotenv()`` + ``os.environ.get`` dataclass). Legacy env
names are preserved through ``AliasChoices`` (``CAMPUSAI_*``,
``EXTRACTOR_*``, ``SELF_CONSISTENCY_SAMPLES``, ``CONSISTENCY_THRESHOLD``).
"""

from __future__ import annotations

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExtractorSettings(BaseSettings):
    """Extractor service settings.

    Parameters
    ----------
    llm_api_key : SecretStr
        API key for the external LLM provider. Wrapped in ``SecretStr`` so it
        is masked in logs, tracebacks and OpenAPI/repr output.
    llm_model : str
        Name of the model to use for entity extraction.
    llm_base_url : str | None
        Optional custom base URL for OpenAI-compatible APIs (e.g. local Ollama, vLLM, Groq).
    llm_temperature : float
        Sampling temperature for self-consistency runs (ignored when n == 1).
    self_consistency_samples : int
        Number of stochastic completions (n) used for majority voting.
    consistency_threshold : float
        Minimum fraction of samples an entity must appear in to be kept.
    request_timeout_seconds : float
        HTTP timeout for a single LLM call.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated container env vars (PYTHONUNBUFFERED, ...)
    )

    llm_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("CAMPUSAI_API_KEY", "llm_api_key"),
    )
    llm_model: str = Field(
        default="google/gemma-4-26b-a4b",
        validation_alias=AliasChoices("CAMPUSAI_MODEL", "llm_model"),
    )
    llm_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CAMPUSAI_API_URL", "llm_base_url"),
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        validation_alias=AliasChoices("EXTRACTOR_TEMPERATURE", "llm_temperature"),
    )
    self_consistency_samples: int = Field(
        default=8,
        ge=1,
        validation_alias=AliasChoices(
            "SELF_CONSISTENCY_SAMPLES", "self_consistency_samples"
        ),
    )
    consistency_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("CONSISTENCY_THRESHOLD", "consistency_threshold"),
    )
    request_timeout_seconds: float = Field(
        default=60.0,
        gt=0,
        validation_alias=AliasChoices(
            "EXTRACTOR_TIMEOUT_SECONDS", "request_timeout_seconds"
        ),
    )
    #: Root logging level (env ``LOG_LEVEL``), e.g. DEBUG, INFO, WARNING.
    log_level: str = "INFO"

    @field_validator("log_level", mode="after")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        """Accept any case (``debug`` -> ``DEBUG``) and reject unknown levels."""
        level = value.upper()
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"unknown log level: {value!r}")
        return level


extractor_settings = ExtractorSettings()
