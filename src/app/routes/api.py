"""API proxy and benchmark endpoints for text-to-persons extraction."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.app.models import (
    ExtractPersonsProxyResponse,
    ExtractPersonsRequest,
    MetricsResponse,
    TestSuiteResponse,
)
from src.app.services.person_client import call_person_service
from src.app.utils.dataset import TEST_DATASET
from src.app.utils.metrics import METRICS
from src.app.utils.normalization import normalize_person_list

router = APIRouter(prefix="/api", tags=["API"])


@router.post(
    "/extract-persons",
    response_model=ExtractPersonsProxyResponse,
    summary="Extract person entities",
)
async def api_extract_persons(req: ExtractPersonsRequest) -> JSONResponse:
    """Proxy endpoint calling the external extraction service.

    Accepts text, dispatches it to the configured external web service,
    and returns detected person entities along with request latency metadata.

    Parameters
    ----------
    req : ExtractPersonsRequest
        Request payload containing the input text.

    Returns
    -------
    JSONResponse
        Dictionary containing 'persons' list and '_meta' latency information.
    """
    resp, latency_ms = await call_person_service(req.text)
    payload: Dict[str, Any] = {
        "persons": resp.persons,
        "_meta": {"latency_ms": latency_ms},
    }
    return JSONResponse(content=payload)


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Retrieve operational metrics",
)
async def api_metrics() -> JSONResponse:
    """Retrieve operational request and latency metrics.

    Returns
    -------
    JSONResponse
        In-memory metrics summary dictionary.
    """
    return JSONResponse(content=METRICS.summary())


@router.post(
    "/run-tests",
    response_model=TestSuiteResponse,
    summary="Run benchmark test suite",
)
async def api_run_tests() -> JSONResponse:
    """Execute the built-in benchmark test dataset against the external service.

    Notes
    -----
    - Calls the external service once for each benchmark test case.
    - Evaluates predictions using order-insensitive comparisons.
    - Captures latency and detailed error responses for failing test cases.

    Returns
    -------
    JSONResponse
        Summary statistics and per-item test results.
    """
    results: List[Dict[str, Any]] = []
    passed = 0

    for ex in TEST_DATASET:
        text = ex["text"]
        expected = normalize_person_list(list(ex["persons"]))

        try:
            got_resp, latency_ms = await call_person_service(text)
            got = normalize_person_list(got_resp.persons)
            is_match = sorted(got) == sorted(expected)
            if is_match:
                passed += 1

            results.append(
                {
                    "text": text,
                    "expected": expected,
                    "got": got,
                    "pass": is_match,
                    "latency_ms": latency_ms,
                }
            )
        except HTTPException as exc:
            results.append(
                {
                    "text": text,
                    "expected": expected,
                    "got": None,
                    "pass": False,
                    "error": exc.detail,
                }
            )

    total_count = len(TEST_DATASET)
    summary: Dict[str, Any] = {
        "total": total_count,
        "passed": passed,
        "failed": total_count - passed,
        "pass_rate": (passed / total_count) if total_count > 0 else 0.0,
    }

    return JSONResponse(content={"summary": summary, "results": results})

