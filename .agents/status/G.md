# Agent G — LLM Integration (Gemini Flash → Node 2)

## Verify Results
- `pytest tests/test_node2_extraction/ -v` — PASS (40/40)
- Contract validation — PASS (NODE_2_TO_3_SCHEMA enforced)
- Scope boundary respected — YES

## Shared File Requests
- `config.py` was listed in Golf scope → edited directly (added Gemini env vars)
- `pyproject.toml` — NO CHANGES NEEDED (google-generativeai already listed)

## Changes
- `src/ontology_engine/config.py` — Added GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_OUTPUT_TOKENS, GEMINI_MAX_RETRIES, GEMINI_RETRY_DELAY, changed default LLM_PROVIDER to "gemini"
- `src/ontology_engine/node2_extraction/extractor.py` — Replaced _call_llm stub with real Gemini Flash integration via _call_gemini(), added LLMProviderError/LLMRateLimitError exceptions, retry with exponential backoff, safety filter detection, response_mime_type="application/json"
- `tests/test_node2_extraction/test_extractor.py` — Added 8 Gemini-specific tests (missing API key, successful call, safety block, no candidates, rate limit retries, retries exhausted, max tokens, transient errors), uses sys.modules mocking for SDK

## Notes
- google-generativeai SDK is NOT installed in the venv (listed in pyproject.toml but never pip installed). Tests work via sys.modules mocking. Run `pip install -e ".[dev]"` to install all deps.
- The `_call_gemini` function uses deferred imports from config with try/except fallback to os.environ for test compatibility.
