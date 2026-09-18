"""Unit tests for operational metrics tracker."""

from src.app.utils.metrics import Metrics


def test_metrics_initial_state() -> None:
    """A fresh metrics instance starts with zero counts."""
    m = Metrics()
    summary = m.summary()
    assert summary["total_requests"] == 0
    assert summary["success_requests"] == 0
    assert summary["failed_requests"] == 0
    assert summary["last_latency_ms"] is None
    assert summary["avg_latency_ms"] is None


def test_metrics_recording_and_averaging() -> None:
    """Metrics properly accumulate counts and average latency."""
    m = Metrics()
    m.record(ok=True, latency_ms=100.0)
    m.record(ok=False, latency_ms=200.0)

    summary = m.summary()
    assert summary["total_requests"] == 2
    assert summary["success_requests"] == 1
    assert summary["failed_requests"] == 1
    assert summary["last_latency_ms"] == 200.0
    assert summary["avg_latency_ms"] == 150.0


def test_metrics_reset() -> None:
    """Reset clears all historical data."""
    m = Metrics()
    m.record(ok=True, latency_ms=50.0)
    m.reset()
    summary = m.summary()
    assert summary["total_requests"] == 0
    assert summary["avg_latency_ms"] is None

