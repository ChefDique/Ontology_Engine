# ──────────────────────────────────────────────────────────────────────────
# Ontology Engine — Multi-stage Dockerfile
# Stage 1: Install Python dependencies (cached layer)
# Stage 2: Runtime with tesseract + app
# ──────────────────────────────────────────────────────────────────────────

# ── Stage 1: Build dependencies ──────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build-time system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy full project (need src/ for setuptools to resolve)
COPY pyproject.toml README.md ./
COPY src/ src/

# Install all deps + the project into a prefix for clean copy
RUN pip install --no-cache-dir --prefix=/install .


# ── Stage 2: Runtime ─────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Tesseract OCR + system deps for PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy application source (already installed, but keep for any runtime path refs)
COPY src/ src/

# ── Runtime configuration ────────────────────────────────────────────────
# These are defaults; override via Railway/Docker env vars
ENV PORT=8000
ENV API_ENABLED=true
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user for security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE ${PORT}

# Health check — hit the root endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/')" || exit 1

# Start the FastAPI server
CMD ["sh", "-c", "uvicorn ontology_engine.api:app --host 0.0.0.0 --port ${PORT}"]
