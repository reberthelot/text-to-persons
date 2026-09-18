"""Operational metrics tracking for requests and service latencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.app.config import settings


@dataclass
class Metrics:
    """In-memory operational metrics tracker.

    Tracks request counts, error rates, and response latency statistics.

    Parameters
    ----------
    total_requests : int, default=0
        Total number of processed extraction requests.
    success_requests : int, default=0
        Number of successful responses (2xx).
    failed_requests : int, default=0
        Number of failed or errored requests (5xx/4xx/timeouts).
    last_latency_ms : float or None, default=None
        Latency of the most recent service call in milliseconds.
    latencies_ms : list of float
        History of latencies recorded for all calls.

    Notes
    -----
    This tracker is intentionally process-local and in-memory (no database
    dependency). In multi-worker environments, each worker maintains its own
    process metrics.
    """

    total_requests: int = 0
    success_requests: int = 0
    failed_requests: int = 0
    last_latency_ms: Optional[float] = None
    latencies_ms: List[float] = field(default_factory=list)

    def record(self, ok: bool, latency_ms: float) -> None:
        """Record the outcome and latency of a single service request.

        Parameters
        ----------
        ok : bool
            True if the service call succeeded and response format was valid,
            False otherwise.
        latency_ms : float
            Request latency measured in milliseconds.
        """
        self.total_requests += 1
        self.last_latency_ms = latency_ms
        self.latencies_ms.append(latency_ms)
        if ok:
            self.success_requests += 1
        else:
            self.failed_requests += 1

    def reset(self) -> None:
        """Reset all metric counters and latency history."""
        self.total_requests = 0
        self.success_requests = 0
        self.failed_requests = 0
        self.last_latency_ms = None
        self.latencies_ms.clear()

    def summary(self) -> Dict[str, Any]:
        """Compute and return an operational summary dictionary.

        Returns
        -------
        dict
            Summary containing request counts, average latency, last latency,
            and current external service configuration parameters.
        """
        avg = (sum(self.latencies_ms) / len(self.latencies_ms)) if self.latencies_ms else None
        return {
            "total_requests": self.total_requests,
            "success_requests": self.success_requests,
            "failed_requests": self.failed_requests,
            "last_latency_ms": self.last_latency_ms,
            "avg_latency_ms": avg,
            "service_base_url": settings.service_base_url,
            "service_endpoint": settings.service_endpoint,
            "timeout_seconds": settings.service_timeout_seconds,
        }


# Global singleton instance for the process
METRICS = Metrics()

