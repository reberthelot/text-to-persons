"""Configuration settings for the Person Extractor Service.

Loads settings from environment variables and supports .env files.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load variables from .env file into os.environ if present
load_dotenv()


@dataclass(frozen=True)
class ExtractorSettings:
    """Extractor service settings.

    Parameters
    ----------
    llm_api_key : str
        API key for the external LLM provider (e.g. OpenAI / LiteLLM / Mistral).
    llm_model : str
        Name of the model to use for entity extraction.
    llm_base_url : str | None
        Optional custom base URL for OpenAI-compatible APIs (e.g. local Ollama, vLLM, Groq).
    """

    llm_api_key: str = os.environ.get("CAMPUSAI_API_KEY", "")
    llm_model: str = os.environ.get("CAMPUSAI_MODEL", "google/gemma-4-26b-a4b")
    llm_embed_model: str = os.environ.get("CAMPUSAI_EMBED_MODEL", "cai-embedding")
    llm_base_url: str | None = os.environ.get("CAMPUSAI_API_URL", None)
    llm_temperature: float = float(os.environ.get("EXTRACTOR_TEMPERATURE", "0.7"))
    self_consistency_samples: int = int(os.environ.get("SELF_CONSISTENCY_SAMPLES", "8"))
    consistency_threshold: float = float(os.environ.get("CONSISTENCY_THRESHOLD", "0.5"))
    request_timeout_seconds: float = float(os.environ.get("EXTRACTOR_TIMEOUT_SECONDS", "60.0"))


extractor_settings = ExtractorSettings()

