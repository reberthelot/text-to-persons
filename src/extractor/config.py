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
    llm_model: str = os.environ.get("CAMPUSAI_MODEL", "gpt-4o-mini")
    llm_embed_model: str = os.environ.get("CAMPUSAI_EMBED_MODEL", "gpt-4o-mini")
    llm_base_url: str | None = os.environ.get("CAMPUSAI_API_URL", None)


extractor_settings = ExtractorSettings()

