"""Service client for calling the external LLM provider to extract persons."""

from __future__ import annotations

import json
from typing import List

import httpx
from pydantic import ValidationError
from src.app.models import ExtractPersonsResponse
from src.extractor.config import extractor_settings
from src.extractor.prompts import EXTRACTION_SYSTEM_PROMPT


class ExternalLLMExtractor:
    """Async client interacting with an OpenAI-compatible completion/chat API."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        # The API key is stored unwrapped (needed for the bearer header);
        # SecretStr guarantees it never appears in logs or repr output.
        self.api_key = extractor_settings.llm_api_key.get_secret_value()
        self.model = extractor_settings.llm_model
        base_url = extractor_settings.llm_base_url or "https://api.campusai.compute.dtu.dk/v1"
        self.endpoint = f"{base_url.rstrip('/')}/chat/completions"
        self.samples = extractor_settings.self_consistency_samples
        self.temperature = extractor_settings.llm_temperature if self.samples > 1 else 0.0
        self.threshold = extractor_settings.consistency_threshold
        self.timeout = extractor_settings.request_timeout_seconds
        # A pooled client is injected by the application lifespan; the fallback
        # keeps standalone usage working (one client per extractor instance).
        self._client = client if client is not None else httpx.AsyncClient(timeout=self.timeout)

    async def extract(self, text: str) -> List[str]:
        """Extract person entities from text via the external LLM API.

        Uses self-consistency (sampling multiple stochastic predictions and majority
        voting) together with an OpenAI-compatible JSON Schema response_format to
        ensure structured output integrity.

        Parameters
        ----------
        text : str
            The input sentence or paragraph.

        Returns
        -------
        List[str]
            A list of detected person names that passed majority voting.
        """
        if not self.api_key:
            raise RuntimeError(
                "CAMPUSAI_API_KEY is not set. Please provide it in your .env file or environment."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Request strictly structured JSON adhering to ExtractPersonsResponse schema
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Text:\n{text}"},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "extract_persons_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "persons": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Unique list of person names extracted from the text."
                            }
                        },
                        "required": ["persons"],
                        "additionalProperties": False
                    }
                }
            },
            "n": self.samples,
            "temperature": self.temperature,
        }

        # The (possibly shared, lifespan-managed) client must NOT be used as a
        # context manager here: `async with client` would close it after the
        # first request. Closing is the lifespan's responsibility.
        resp = await self._client.post(
            self.endpoint, headers=headers, json=payload, timeout=self.timeout
        )
        resp.raise_for_status()

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            return []

        # If only 1 sample was generated, parse directly
        if len(choices) == 1:
            raw_content = choices[0]["message"]["content"]
            parsed = json.loads(raw_content)
            response_model = ExtractPersonsResponse.model_validate(parsed)
            return response_model.persons

        # Aggregate self-consistency predictions
        name_counts: dict[str, int] = {}
        canonical_names: dict[str, str] = {}

        for choice in choices:
            raw_content = choice.get("message", {}).get("content", "")
            try:
                parsed = json.loads(raw_content)
                validated = ExtractPersonsResponse.model_validate(parsed)
                unique_sample_names = {name.strip() for name in validated.persons if name.strip()}
                for name in unique_sample_names:
                    key = name.lower()
                    name_counts[key] = name_counts.get(key, 0) + 1
                    if key not in canonical_names:
                        canonical_names[key] = name
            except (json.JSONDecodeError, ValidationError, TypeError):
                # Skip malformed candidates only: JSONDecodeError/ValidationError
                # from a bad sample, TypeError if content is not a string.
                # (The previous `(JSONDecodeError, Exception)` tuple was
                # equivalent to bare `except Exception` and hid real bugs.)
                continue

        # Majority voting
        min_votes = int(len(choices) * self.threshold)
        if min_votes < 1:
            min_votes = 1

        selected_persons: List[str] = [
            canonical_names[key]
            for key, count in name_counts.items()
            if count >= min_votes
        ]

        return selected_persons
