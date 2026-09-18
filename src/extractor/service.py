"""Service client for calling the external LLM provider to extract persons."""

from __future__ import annotations

import json
from typing import List

import httpx
from src.app.models import ExtractPersonsResponse
from src.extractor.config import extractor_settings
from src.extractor.prompts import EXTRACTION_SYSTEM_PROMPT


class ExternalLLMExtractor:
    """Async client interacting with an OpenAI-compatible completion/chat API."""

    def __init__(self) -> None:
        self.api_key = extractor_settings.llm_api_key
        self.model = extractor_settings.llm_model
        base_url = extractor_settings.llm_base_url or "https://api.openai.com/v1"
        self.endpoint = f"{base_url.rstrip('/')}/chat/completions"

    async def extract(self, text: str) -> List[str]:
        """Extract person entities from text via the external LLM API.

        Parameters
        ----------
        text : str
            The input sentence or paragraph.

        Returns
        -------
        List[str]
            A list of detected person names.
        """
        # If no API key is provided, return a clear exception or fallback
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please provide it in your .env file or environment."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Request structured JSON format adhering to ExtractPersonsResponse
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Text:\n{text}"},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.endpoint, headers=headers, json=payload)
            resp.raise_for_status()

            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_content)

            # Validate against our Pydantic schema
            response_model = ExtractPersonsResponse.model_validate(parsed)
            return response_model.persons

