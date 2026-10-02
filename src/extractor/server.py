"""FastAPI standalone server for the Person Extraction Service.

Exposes POST /v1/extract-persons on port 8000 as specified by the benchmark client.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request, status

from src.app.models import ExtractPersonsRequest, ExtractPersonsResponse
from src.extractor.config import extractor_settings
from src.extractor.service import ExternalLLMExtractor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the extractor and its pooled HTTP client once at startup.

    The extractor previously lived at module scope; moving it here makes the
    dependency injectable (tests can swap ``app.state.extractor``) and lets a
    single connection pool be shared and closed properly at shutdown.
    """
    logging.basicConfig(
        level=extractor_settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app.state.http_client = httpx.AsyncClient()
    app.state.extractor = ExternalLLMExtractor(client=app.state.http_client)
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(
    title="Person Extraction Microservice",
    description="Microservice providing NER person extraction via external LLM API.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe for Docker HEALTHCHECK: no dependencies, no side effects."""
    return {"status": "ok"}


@app.post(
    "/v1/extract-persons",
    response_model=ExtractPersonsResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract person entities from input text",
)
async def extract_persons(payload: ExtractPersonsRequest, request: Request) -> ExtractPersonsResponse:
    """Endpoint fulfilling the contract expected by the test/frontend service."""
    extractor: ExternalLLMExtractor = request.app.state.extractor
    try:
        persons = await extractor.extract(payload.text)
        return ExtractPersonsResponse(persons=persons)
    except HTTPException:
        raise
    except Exception as exc:
        # Full details go to the server logs only: upstream errors can echo
        # provider URLs or internal messages back to the client.
        logger.exception("Person extraction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Extraction failed: an unexpected error occurred while calling "
                "the LLM provider. See the server logs for details."
            ),
        ) from exc


if __name__ == "__main__":
    uvicorn.run("src.extractor.server:app", host="127.0.0.1", port=8000, reload=True)
