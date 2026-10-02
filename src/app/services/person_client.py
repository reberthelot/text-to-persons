"""Client service for invoking the external person extraction Web service."""

from __future__ import annotations

import time
from typing import Tuple

import httpx
from fastapi import HTTPException

from src.app.config import settings
from src.app.models import ExtractPersonsResponse
from src.app.utils.metrics import METRICS


async def call_person_service(
    text: str, client: httpx.AsyncClient
) -> Tuple[ExtractPersonsResponse, float]:
    """Call the external person-extraction Web service.

    Sends an asynchronous HTTP POST request with a JSON payload `{"text": text}`
    to the configured target endpoint. Handles timeouts, connection failures,
    HTTP status errors, and schema validation with pedagogic error messages.

    Parameters
    ----------
    text : str
        The input text string to analyze.
    client : httpx.AsyncClient
        Shared pooled client created by the application lifespan.

    Returns
    -------
    response : ExtractPersonsResponse
        Parsed response model containing the list of person names.
    latency_ms : float
        Round-trip latency of the external service call in milliseconds.

    Raises
    ------
    HTTPException
        If the external service is unreachable (502), times out (504), returns
        a non-2xx status (502), or returns invalid/malformed JSON (502).
    """
    url = f"{settings.service_base_url}{settings.service_endpoint}"
    start = time.perf_counter()

    timeout = httpx.Timeout(settings.service_timeout_seconds)
    try:
        resp = await client.post(url, json={"text": text}, timeout=timeout)
    except httpx.TimeoutException as exc:
        # Base class for ConnectTimeout / ReadTimeout / WriteTimeout / PoolTimeout.
        latency_ms = (time.perf_counter() - start) * 1000.0
        METRICS.record(ok=False, latency_ms=latency_ms)
        raise HTTPException(
            status_code=504,
            detail=(
                "The Web service did not respond before the timeout.\n\n"
                f"Timeout: {settings.service_timeout_seconds:.1f}s\n"
                f"Endpoint: {url}\n\n"
                "Typical fixes:\n"
                "• Increase PERSON_SERVICE_TIMEOUT_SECONDS\n"
                "• Make the service faster (e.g., smaller model / caching)\n"
                "• Check service logs for slow LLM calls"
            ),
        ) from exc
    except httpx.TransportError as exc:
        # Base class for ConnectError, NetworkError, ProtocolError, ...
        latency_ms = (time.perf_counter() - start) * 1000.0
        METRICS.record(ok=False, latency_ms=latency_ms)
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not connect to the Web service.\n\n"
                f"Checked: {url}\n"
                "Typical fixes:\n"
                "• Start the container / service\n"
                "• Verify port mapping (e.g., -p 8000:8000)\n"
                "• If running remotely, check firewall / host\n\n"
                f"Technical detail: {type(exc).__name__}"
            ),
        ) from exc

    latency_ms = (time.perf_counter() - start) * 1000.0

    # Pedagogic handling of non-2xx statuses
    if resp.status_code // 100 != 2:
        METRICS.record(ok=False, latency_ms=latency_ms)
        raise HTTPException(
            status_code=502,
            detail=(
                "The Web service returned an error.\n\n"
                f"HTTP status: {resp.status_code}\n"
                f"Endpoint: {url}\n"
                "Response body (first 500 chars):\n"
                f"{resp.text[:500]}"
            ),
        )

    # Validate JSON shape
    try:
        data = resp.json()
    except ValueError as exc:
        METRICS.record(ok=False, latency_ms=latency_ms)
        raise HTTPException(
            status_code=502,
            detail=(
                "The Web service responded, but the response was not valid JSON.\n\n"
                f"Endpoint: {url}\n"
                "Tip: ensure the service returns application/json with a body like:\n"
                '{"persons": ["Name 1", "Name 2"]}'
            ),
        ) from exc

    if not isinstance(data, dict) or "persons" not in data or not isinstance(data["persons"], list):
        METRICS.record(ok=False, latency_ms=latency_ms)
        raise HTTPException(
            status_code=502,
            detail=(
                "The Web service returned JSON, but not in the expected format.\n\n"
                "Expected a JSON object with a key 'persons' holding a list of strings.\n"
                "Example:\n"
                '{"persons": ["Einstein", "von Neumann"]}\n\n'
                f"Received (first 500 chars): {str(data)[:500]}"
            ),
        )

    # Coerce to strings for pedagogical robustness
    persons = [str(item) for item in data.get("persons", [])]
    METRICS.record(ok=True, latency_ms=latency_ms)
    return ExtractPersonsResponse(persons=persons), latency_ms
