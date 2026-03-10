#!/bin/sh
# Railway start script — ensures PORT env var is properly read
exec uvicorn ontology_engine.api:app --host 0.0.0.0 --port "${PORT:-8000}"
