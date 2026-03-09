"""
Backend API + Security — FastAPI server for Ontology Engine.

Endpoints:
    POST /api/analyze   Upload two Xactimate PDFs → supplement report JSON
    GET  /api/health     Health check + circuit breaker status

Security layers:
    - Kill switch (API_ENABLED env var)
    - Circuit breaker (5 consecutive failures → 5-minute cooldown)
    - Rate limiter (IP daily limits + concurrent request semaphore + global budget)
    - File size + type validation

Tasks:
    M1: FastAPI server with /api/analyze endpoint
    M2: run_supplement_pipeline() inline (Node 1-3 per PDF → Node 5 → Node 6)
    M3: Rate limiter
    M4: Kill switch + circuit breaker
"""

import asyncio
import logging
import os
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"application/pdf"}

# Rate limiting
RATE_LIMIT_PER_IP_DAILY = int(os.getenv("RATE_LIMIT_PER_IP_DAILY", "50"))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "3"))
GLOBAL_DAILY_BUDGET = int(os.getenv("GLOBAL_DAILY_BUDGET", "500"))

# Circuit breaker
CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
CIRCUIT_BREAKER_COOLDOWN_SECONDS = int(os.getenv("CIRCUIT_BREAKER_COOLDOWN", "300"))


# ── Circuit Breaker ───────────────────────────────────────────────────────
class CircuitBreaker:
    """Trips after N consecutive pipeline failures; resets after cooldown."""

    def __init__(self, threshold: int = 5, cooldown_seconds: int = 300):
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.consecutive_failures = 0
        self.tripped_at: float | None = None

    @property
    def is_open(self) -> bool:
        """True when the breaker is tripped and still in cooldown."""
        if self.tripped_at is None:
            return False
        elapsed = time.time() - self.tripped_at
        if elapsed >= self.cooldown_seconds:
            # Cooldown expired — auto-reset
            self.reset()
            return False
        return True

    @property
    def cooldown_remaining(self) -> float:
        if self.tripped_at is None:
            return 0.0
        remaining = self.cooldown_seconds - (time.time() - self.tripped_at)
        return max(0.0, remaining)

    def record_success(self):
        self.consecutive_failures = 0

    def record_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.threshold:
            self.tripped_at = time.time()
            logger.warning(
                "Circuit breaker TRIPPED after %d consecutive failures. "
                "Cooldown: %ds",
                self.consecutive_failures,
                self.cooldown_seconds,
            )

    def reset(self):
        self.consecutive_failures = 0
        self.tripped_at = None


# ── Rate Limiter ──────────────────────────────────────────────────────────
class RateLimiter:
    """IP-based daily limits + concurrent request semaphore + global budget."""

    def __init__(
        self,
        per_ip_daily: int = 50,
        max_concurrent: int = 3,
        global_daily: int = 500,
    ):
        self.per_ip_daily = per_ip_daily
        self.max_concurrent = max_concurrent
        self.global_daily = global_daily
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._ip_counts: dict[str, int] = defaultdict(int)
        self._global_count = 0
        self._current_day: str = ""
        self._reset_if_new_day()

    def _reset_if_new_day(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._current_day:
            self._ip_counts.clear()
            self._global_count = 0
            self._current_day = today

    def check_ip_limit(self, client_ip: str) -> bool:
        """Returns True if request is allowed."""
        self._reset_if_new_day()
        return self._ip_counts[client_ip] < self.per_ip_daily

    def check_global_limit(self) -> bool:
        self._reset_if_new_day()
        return self._global_count < self.global_daily

    def record_request(self, client_ip: str):
        self._reset_if_new_day()
        self._ip_counts[client_ip] += 1
        self._global_count += 1

    @property
    def semaphore(self) -> asyncio.Semaphore:
        return self._semaphore

    def get_ip_remaining(self, client_ip: str) -> int:
        self._reset_if_new_day()
        return max(0, self.per_ip_daily - self._ip_counts[client_ip])

    def get_global_remaining(self) -> int:
        self._reset_if_new_day()
        return max(0, self.global_daily - self._global_count)


# ── Globals ───────────────────────────────────────────────────────────────
circuit_breaker = CircuitBreaker(
    threshold=CIRCUIT_BREAKER_THRESHOLD,
    cooldown_seconds=CIRCUIT_BREAKER_COOLDOWN_SECONDS,
)
rate_limiter = RateLimiter(
    per_ip_daily=RATE_LIMIT_PER_IP_DAILY,
    max_concurrent=MAX_CONCURRENT_REQUESTS,
    global_daily=GLOBAL_DAILY_BUDGET,
)


# ── App ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Ontology Engine API",
    description=(
        "Upload two Xactimate estimate PDFs (adjuster + contractor) "
        "and receive a supplement report identifying gaps and recovery opportunities."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For behind proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _is_api_enabled() -> bool:
    """Kill switch: if API_ENABLED is explicitly 'false', block all requests."""
    return os.getenv("API_ENABLED", "true").lower() != "false"


# ── M2: Supplement Pipeline (inline) ─────────────────────────────────────

def _run_nodes_1_to_3(input_path: Path) -> dict:
    """Run Nodes 1-3 on a single PDF and return Node 3 output.

    This is the ingestion → extraction → calculus sub-pipeline,
    called once per estimate PDF.
    """
    from ontology_engine.contracts.schemas import (
        NODE_1_TO_2_SCHEMA,
        NODE_2_TO_3_SCHEMA,
        NODE_3_TO_4_SCHEMA,
    )
    from ontology_engine.node1_ingestion import ingest
    from ontology_engine.node2_extraction.extractor import extract_estimate
    from ontology_engine.node3_calculus.credit_handler import handle_credits
    from ontology_engine.node3_calculus.oop_stripper import strip_overhead_and_profit
    from ontology_engine.node3_calculus.roofer_math import calculate_material_quantities
    from ontology_engine.pipeline import _validate_contract

    # Node 1: Ingestion
    node1_output = ingest(input_path)
    _validate_contract(node1_output, NODE_1_TO_2_SCHEMA, "Node1", "Node2")

    # Node 2: Semantic Extraction
    node2_output = extract_estimate(node1_output["chunks"])
    _validate_contract(node2_output, NODE_2_TO_3_SCHEMA, "Node2", "Node3")

    # Node 3: Deterministic Calculus
    procurement_items = calculate_material_quantities(node2_output["line_items"])
    oop_result = strip_overhead_and_profit(
        node2_output["totals"], node2_output["line_items"]
    )
    credit_result = handle_credits(procurement_items)

    node3_output = {
        "header": node2_output.get("header", {}),
        "procurement_items": credit_result["procurement_items"],
        "credit_items": credit_result["credit_items"],
        "adjusted_totals": oop_result["adjusted_totals"],
        "hitl_flags": [],
    }
    _validate_contract(node3_output, NODE_3_TO_4_SCHEMA, "Node3", "Node4")

    return node3_output


def run_supplement_pipeline(
    adjuster_pdf: Path,
    contractor_pdf: Path,
) -> dict:
    """Full supplement pipeline: two PDFs → Nodes 1-3 each → Node 5 → Node 6.

    Args:
        adjuster_pdf: Path to the insurance adjuster's Xactimate PDF.
        contractor_pdf: Path to the contractor's Xactimate PDF.

    Returns:
        dict with keys:
            - success: bool
            - report: supplement report (Node 6 output)
            - gap_report: intermediate gap report (Node 5 output)
            - metadata: execution timings and counts
    """
    from ontology_engine.node5_comparator.comparator import compare_estimates
    from ontology_engine.node6_supplement.report_generator import (
        generate_supplement_report,
    )

    start = time.time()
    metadata = {
        "adjuster_file": str(adjuster_pdf),
        "contractor_file": str(contractor_pdf),
        "start_time": start,
        "nodes_completed": [],
    }

    # Run Nodes 1-3 on adjuster estimate
    logger.info("Processing adjuster estimate: %s", adjuster_pdf.name)
    adjuster_n3 = _run_nodes_1_to_3(adjuster_pdf)
    metadata["nodes_completed"].append("adjuster_nodes_1-3")

    # Run Nodes 1-3 on contractor estimate
    logger.info("Processing contractor estimate: %s", contractor_pdf.name)
    contractor_n3 = _run_nodes_1_to_3(contractor_pdf)
    metadata["nodes_completed"].append("contractor_nodes_1-3")

    # Node 5: Comparison
    logger.info("Node 5: Comparing estimates")
    gap_report = compare_estimates(adjuster_n3, contractor_n3)
    metadata["nodes_completed"].append("node5_comparator")

    # Node 6: Supplement Report
    logger.info("Node 6: Generating supplement report")
    report = generate_supplement_report(gap_report)
    metadata["nodes_completed"].append("node6_supplement")

    metadata["end_time"] = time.time()
    metadata["duration_seconds"] = round(metadata["end_time"] - start, 2)

    logger.info(
        "Supplement pipeline complete in %.1fs",
        metadata["duration_seconds"],
    )

    return {
        "success": True,
        "report": report,
        "gap_report": gap_report,
        "metadata": metadata,
    }


# ── M1: /api/analyze endpoint ────────────────────────────────────────────

@app.post("/api/analyze")
async def analyze_estimates(
    request: Request,
    adjuster_pdf: UploadFile = File(..., description="Insurance adjuster's Xactimate PDF"),
    contractor_pdf: UploadFile = File(..., description="Contractor's Xactimate PDF"),
):
    """Upload two Xactimate PDFs and receive a supplement report.

    Accepts multipart/form-data with two PDF files:
        - adjuster_pdf: The insurance adjuster's estimate
        - contractor_pdf: The contractor's estimate

    Returns:
        JSON supplement report with gap analysis, financial summary,
        and recommended recovery actions.
    """
    # ── M4: Kill switch ──
    if not _is_api_enabled():
        raise HTTPException(
            status_code=503,
            detail="API is currently disabled. Contact administrator.",
        )

    # ── M4: Circuit breaker ──
    if circuit_breaker.is_open:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service temporarily unavailable due to repeated failures.",
                "cooldown_remaining_seconds": round(circuit_breaker.cooldown_remaining),
                "retry_after": round(circuit_breaker.cooldown_remaining),
            },
        )

    # ── M3: Rate limiting (IP + global) ──
    client_ip = _get_client_ip(request)

    if not rate_limiter.check_ip_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Daily request limit exceeded for your IP.",
                "limit": rate_limiter.per_ip_daily,
                "remaining": 0,
            },
        )

    if not rate_limiter.check_global_limit():
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Global daily request budget exhausted.",
                "limit": rate_limiter.global_daily,
            },
        )

    # ── Validate uploads ──
    for label, upload in [("adjuster_pdf", adjuster_pdf), ("contractor_pdf", contractor_pdf)]:
        if upload.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"{label}: Must be a PDF file. Got: {upload.content_type}",
            )

    # Read and validate file sizes
    adjuster_bytes = await adjuster_pdf.read()
    if len(adjuster_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"adjuster_pdf exceeds {MAX_FILE_SIZE_MB}MB limit.",
        )

    contractor_bytes = await contractor_pdf.read()
    if len(contractor_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"contractor_pdf exceeds {MAX_FILE_SIZE_MB}MB limit.",
        )

    # ── M3: Acquire concurrent semaphore ──
    try:
        acquired = rate_limiter.semaphore.locked()
        # Try to acquire without blocking if all slots full
        if not await asyncio.wait_for(
            _acquire_semaphore(rate_limiter.semaphore),
            timeout=0.1,
        ):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Server at maximum concurrent capacity. Try again shortly.",
                    "max_concurrent": rate_limiter.max_concurrent,
                },
            )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Server at maximum concurrent capacity. Try again shortly.",
                "max_concurrent": rate_limiter.max_concurrent,
            },
        )

    try:
        # Record the request against rate limits
        rate_limiter.record_request(client_ip)

        # Write uploaded files to temp directory for pipeline processing
        with tempfile.TemporaryDirectory(prefix="ontology_") as tmpdir:
            adj_path = Path(tmpdir) / "adjuster.pdf"
            ctr_path = Path(tmpdir) / "contractor.pdf"

            adj_path.write_bytes(adjuster_bytes)
            ctr_path.write_bytes(contractor_bytes)

            # ── M2: Run supplement pipeline ──
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                run_supplement_pipeline,
                adj_path,
                ctr_path,
            )

        # Circuit breaker: success
        circuit_breaker.record_success()

        return JSONResponse(
            content={
                "success": True,
                "report": result["report"],
                "gap_report": result["gap_report"],
                "metadata": {
                    "duration_seconds": result["metadata"]["duration_seconds"],
                    "nodes_completed": result["metadata"]["nodes_completed"],
                },
                "rate_limit": {
                    "remaining_today": rate_limiter.get_ip_remaining(client_ip),
                },
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        # Circuit breaker: failure
        circuit_breaker.record_failure()
        logger.exception("Pipeline error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Pipeline processing failed.",
                "message": str(e),
            },
        )
    finally:
        rate_limiter.semaphore.release()


async def _acquire_semaphore(sem: asyncio.Semaphore) -> bool:
    """Try to acquire the semaphore. Returns True on success."""
    await sem.acquire()
    return True


# ── Health endpoint ───────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check(request: Request):
    """Health check with circuit breaker and rate limit status."""
    client_ip = _get_client_ip(request)

    return {
        "status": "healthy" if _is_api_enabled() else "disabled",
        "api_enabled": _is_api_enabled(),
        "circuit_breaker": {
            "is_open": circuit_breaker.is_open,
            "consecutive_failures": circuit_breaker.consecutive_failures,
            "threshold": circuit_breaker.threshold,
            "cooldown_remaining_seconds": round(circuit_breaker.cooldown_remaining),
        },
        "rate_limit": {
            "ip_remaining_today": rate_limiter.get_ip_remaining(client_ip),
            "global_remaining_today": rate_limiter.get_global_remaining(),
            "max_concurrent": rate_limiter.max_concurrent,
        },
    }
