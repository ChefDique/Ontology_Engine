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
# Railway injects PORT as an env var; our app defaults to 8000 if unset
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user for security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

# Start the FastAPI server — Railway sets PORT env var at runtime
CMD uvicorn ontology_engine.api:app --host 0.0.0.0 --port ${PORT:-8000}

