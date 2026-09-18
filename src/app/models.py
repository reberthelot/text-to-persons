"""Pydantic data models for request and response schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExtractPersonsRequest(BaseModel):
    """Input payload for extracting person entities from a block of text."""

    text: str = Field(
        ...,
        min_length=1,
        description="Raw input text to analyze for person names.",
        examples=["Einstein and von Neumann meet each other."],
    )


class ExtractPersonsResponse(BaseModel):
    """Target service output format containing extracted person names."""

    persons: List[str] = Field(
        default_factory=list,
        description="List of detected person names extracted from the text.",
        examples=[["Einstein", "von Neumann"]],
    )


class ExtractPersonsProxyResponse(BaseModel):
    """Response returned by the frontend proxy endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    persons: List[str] = Field(default_factory=list)
    meta: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="_meta",
        description="Execution metadata including latency.",
    )


class MetricsResponse(BaseModel):
    """Response schema for operational metrics."""

    total_requests: int
    success_requests: int
    failed_requests: int
    last_latency_ms: Optional[float] = None
    avg_latency_ms: Optional[float] = None
    service_base_url: str
    service_endpoint: str
    timeout_seconds: float


class TestItemResult(BaseModel):
    """Outcome for an individual test case in the test benchmark."""

    model_config = ConfigDict(populate_by_name=True)

    text: str
    expected: List[str]
    got: Optional[List[str]] = None
    pass_: bool = Field(..., alias="pass")
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class TestSuiteSummary(BaseModel):
    """Aggregate statistical summary of test suite execution."""

    total: int
    passed: int
    failed: int
    pass_rate: Optional[float] = None


class TestSuiteResponse(BaseModel):
    """Response payload returned when executing the test suite."""

    summary: TestSuiteSummary
    results: List[TestItemResult]

