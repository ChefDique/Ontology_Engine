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

# Copy application source + startup script
COPY src/ src/
COPY start.sh .

# ── Runtime configuration ────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chmod +x /app/start.sh
USER appuser

EXPOSE 8000

# Start via shell script — guarantees PORT env var expansion on Railway
CMD ["/bin/sh", "/app/start.sh"]

