"""
Comprehensive tests for the Ontology Engine API (M5).

Tests cover:
    - Upload validation (file type, size, missing files)
    - Kill switch (API_ENABLED=false blocks requests)
    - Circuit breaker (trips after N failures, auto-resets)
    - Rate limiting (IP daily, global budget, concurrent semaphore)
    - Successful pipeline execution (mocked)
    - Pipeline error handling
    - Health endpoint
"""

import asyncio
import io
import os
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ontology_engine.api import (
    CircuitBreaker,
    RateLimiter,
    app,
    circuit_breaker,
    rate_limiter,
)


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_state():
    """Reset circuit breaker and rate limiter state between tests."""
    circuit_breaker.reset()
    rate_limiter._ip_counts.clear()
    rate_limiter._global_count = 0
    rate_limiter._current_day = ""
    os.environ.pop("API_ENABLED", None)
    yield
    os.environ.pop("API_ENABLED", None)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def dummy_pdf():
    """Minimal PDF-like bytes for upload testing."""
    return b"%PDF-1.4 dummy content for testing"


def _make_upload(content: bytes, filename: str = "test.pdf", content_type: str = "application/pdf"):
    """Helper to create UploadFile-like tuples for TestClient."""
    return (filename, io.BytesIO(content), content_type)


# ── Health Endpoint ───────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["api_enabled"] is True

    def test_health_reports_disabled(self, client):
        os.environ["API_ENABLED"] = "false"
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "disabled"
        assert data["api_enabled"] is False

    def test_health_circuit_breaker_status(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        assert data["circuit_breaker"]["is_open"] is False
        assert data["circuit_breaker"]["consecutive_failures"] == 0

    def test_health_rate_limit_info(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        assert "ip_remaining_today" in data["rate_limit"]
        assert "global_remaining_today" in data["rate_limit"]
        assert "max_concurrent" in data["rate_limit"]


# ── Kill Switch (M4) ─────────────────────────────────────────────────────

class TestKillSwitch:
    def test_disabled_api_returns_503(self, client, dummy_pdf):
        os.environ["API_ENABLED"] = "false"
        resp = client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": _make_upload(dummy_pdf),
                "contractor_pdf": _make_upload(dummy_pdf),
            },
        )
        assert resp.status_code == 503
        assert "disabled" in resp.json()["detail"].lower()

    def test_enabled_api_proceeds(self, client, dummy_pdf):
        """When enabled, the API should proceed past the kill switch
        (may fail later due to unmocked pipeline, but NOT with 503)."""
        os.environ["API_ENABLED"] = "true"
        resp = client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": _make_upload(dummy_pdf),
                "contractor_pdf": _make_upload(dummy_pdf),
            },
        )
        # Should NOT be the kill-switch 503
        assert resp.status_code != 503 or "disabled" not in resp.json().get("detail", "").lower()


# ── Circuit Breaker (M4) ─────────────────────────────────────────────────

class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker(threshold=3, cooldown_seconds=60)
        assert cb.is_open is False
        assert cb.consecutive_failures == 0

    def test_trips_after_threshold(self):
        cb = CircuitBreaker(threshold=3, cooldown_seconds=60)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open is False  # 2 < 3
        cb.record_failure()
        assert cb.is_open is True   # 3 >= 3

    def test_success_resets_counter(self):
        cb = CircuitBreaker(threshold=3, cooldown_seconds=60)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.consecutive_failures == 0
        cb.record_failure()
        assert cb.is_open is False  # 1 < 3

    def test_auto_reset_after_cooldown(self):
        cb = CircuitBreaker(threshold=2, cooldown_seconds=1)
        cb.record_failure()
        cb.record_failure()
        assert cb.is_open is True
        time.sleep(1.1)
        assert cb.is_open is False  # Cooldown expired

    def test_tripped_breaker_blocks_request(self, client, dummy_pdf):
        # Trip the global circuit breaker
        for _ in range(CIRCUIT_BREAKER_TRIPS := 5):
            circuit_breaker.record_failure()
        assert circuit_breaker.is_open is True

        resp = client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": _make_upload(dummy_pdf),
                "contractor_pdf": _make_upload(dummy_pdf),
            },
        )
        assert resp.status_code == 503
        data = resp.json()
        assert "temporarily unavailable" in data["detail"]["error"].lower()

    def test_cooldown_remaining_reported(self):
        cb = CircuitBreaker(threshold=1, cooldown_seconds=300)
        cb.record_failure()
        assert cb.is_open is True
        assert cb.cooldown_remaining > 290  # ~300s


# ── Rate Limiter (M3) ────────────────────────────────────────────────────

class TestRateLimiter:
    def test_ip_limit_enforced(self):
        rl = RateLimiter(per_ip_daily=3, max_concurrent=10, global_daily=100)
        assert rl.check_ip_limit("1.2.3.4") is True
        rl.record_request("1.2.3.4")
        rl.record_request("1.2.3.4")
        rl.record_request("1.2.3.4")
        assert rl.check_ip_limit("1.2.3.4") is False
        # Different IP still allowed
        assert rl.check_ip_limit("5.6.7.8") is True

    def test_global_limit_enforced(self):
        rl = RateLimiter(per_ip_daily=100, max_concurrent=10, global_daily=2)
        rl.record_request("a")
        rl.record_request("b")
        assert rl.check_global_limit() is False

    def test_get_ip_remaining(self):
        rl = RateLimiter(per_ip_daily=5, max_concurrent=10, global_daily=100)
        assert rl.get_ip_remaining("1.2.3.4") == 5
        rl.record_request("1.2.3.4")
        assert rl.get_ip_remaining("1.2.3.4") == 4

    def test_ip_rate_limit_returns_429(self, client, dummy_pdf):
        # Exhaust the IP limit
        for _ in range(rate_limiter.per_ip_daily):
            rate_limiter.record_request("testclient")

        resp = client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": _make_upload(dummy_pdf),
                "contractor_pdf": _make_upload(dummy_pdf),
            },
        )
        assert resp.status_code == 429
        data = resp.json()
        assert "limit" in data["detail"]["error"].lower()


# ── Upload Validation ─────────────────────────────────────────────────────

class TestUploadValidation:
    def test_wrong_content_type_rejected(self, client):
        txt = b"not a pdf"
        resp = client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": ("test.txt", io.BytesIO(txt), "text/plain"),
                "contractor_pdf": ("test.txt", io.BytesIO(txt), "text/plain"),
            },
        )
        assert resp.status_code == 422
        assert "pdf" in resp.json()["detail"].lower()

    def test_oversized_file_rejected(self, client):
        # Create a file just over the limit
        big = b"x" * (20 * 1024 * 1024 + 1)
        resp = client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": ("big.pdf", io.BytesIO(big), "application/pdf"),
                "contractor_pdf": ("ok.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf"),
            },
        )
        assert resp.status_code == 413


# ── Successful Pipeline (mocked) ─────────────────────────────────────────

class TestSuccessfulPipeline:
    @patch("ontology_engine.api.run_supplement_pipeline")
    def test_successful_analysis(self, mock_pipeline, client, dummy_pdf):
        mock_pipeline.return_value = {
            "success": True,
            "report": {
                "executive_summary": {"total_recovery_estimate": 1234.56},
                "category_narratives": [],
                "financial_summary": {"total_recovery": 1234.56},
            },
            "gap_report": {
                "summary": {"gap_count": 3, "total_delta": 500.00},
                "line_item_gaps": [],
                "op_analysis": {},
                "depreciation_findings": [],
            },
            "metadata": {
                "duration_seconds": 2.5,
                "nodes_completed": [
                    "adjuster_nodes_1-3",
                    "contractor_nodes_1-3",
                    "node5_comparator",
                    "node6_supplement",
                ],
            },
        }

        resp = client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": _make_upload(dummy_pdf, "adjuster.pdf"),
                "contractor_pdf": _make_upload(dummy_pdf, "contractor.pdf"),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "report" in data
        assert "gap_report" in data
        assert "metadata" in data
        assert data["metadata"]["duration_seconds"] == 2.5
        assert "rate_limit" in data
        mock_pipeline.assert_called_once()


# ── Pipeline Error Handling ───────────────────────────────────────────────

class TestPipelineErrors:
    @patch("ontology_engine.api.run_supplement_pipeline")
    def test_pipeline_error_returns_500(self, mock_pipeline, client, dummy_pdf):
        mock_pipeline.side_effect = RuntimeError("LLM extraction failed")

        resp = client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": _make_upload(dummy_pdf),
                "contractor_pdf": _make_upload(dummy_pdf),
            },
        )
        assert resp.status_code == 500
        data = resp.json()
        assert "failed" in data["detail"]["error"].lower()

    @patch("ontology_engine.api.run_supplement_pipeline")
    def test_pipeline_error_increments_circuit_breaker(self, mock_pipeline, client, dummy_pdf):
        mock_pipeline.side_effect = RuntimeError("Boom")
        initial_failures = circuit_breaker.consecutive_failures

        client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": _make_upload(dummy_pdf),
                "contractor_pdf": _make_upload(dummy_pdf),
            },
        )
        assert circuit_breaker.consecutive_failures == initial_failures + 1

    @patch("ontology_engine.api.run_supplement_pipeline")
    def test_success_resets_circuit_breaker(self, mock_pipeline, client, dummy_pdf):
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        assert circuit_breaker.consecutive_failures == 2

        mock_pipeline.return_value = {
            "success": True,
            "report": {},
            "gap_report": {},
            "metadata": {"duration_seconds": 1.0, "nodes_completed": []},
        }

        client.post(
            "/api/analyze",
            files={
                "adjuster_pdf": _make_upload(dummy_pdf),
                "contractor_pdf": _make_upload(dummy_pdf),
            },
        )
        assert circuit_breaker.consecutive_failures == 0
