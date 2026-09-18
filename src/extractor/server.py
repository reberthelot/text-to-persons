"""FastAPI standalone server for the Person Extraction Service.

Exposes POST /v1/extract-persons on port 8000 as specified by the benchmark client.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException, status

from src.app.models import ExtractPersonsRequest, ExtractPersonsResponse
from src.extractor.service import ExternalLLMExtractor

app = FastAPI(
    title="Person Extraction Microservice",
    description="Microservice providing NER person extraction via external LLM API.",
    version="1.0.0",
)

extractor = ExternalLLMExtractor()


@app.post(
    "/v1/extract-persons",
    response_model=ExtractPersonsResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract person entities from input text",
)
async def extract_persons(request: ExtractPersonsRequest) -> ExtractPersonsResponse:
    """Endpoint fulfilling the contract expected by the test/frontend service."""
    try:
        persons = await extractor.extract(request.text)
        return ExtractPersonsResponse(persons=persons)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(exc)}",
        )


if __name__ == "__main__":
    uvicorn.run("src.extractor.server:app", host="127.0.0.1", port=8000, reload=True)

