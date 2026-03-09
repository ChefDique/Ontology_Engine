# Agent K — Red Team Suite (Adversarial Testing)

## Verify Results
- `pytest tests/red_team/ -v` — PASS (146/146)
- Contract validation — PASS
- Scope boundary respected — YES

## Shared File Requests
None required.

## Red Team Findings

### PII Sanitizer Gaps (Presidio Backend)
1. **SSN detection gap**: Presidio's `US_SSN` recognizer misses SSNs when prefixed with label text (e.g., "SSN: 123-45-6789"). Regex fallback would catch these, but Presidio takes priority when installed.
2. **Long-text email detection gap**: Presidio may fail to detect emails embedded in very long text (>28K chars). Possible context-window limitation in the NER model.

**Recommendation**: Consider running regex detection as a secondary pass after Presidio, or chunking long text before PII analysis.

### LLM Response Parsing
3. **`null` JSON passthrough**: `_parse_llm_response("null")` returns Python `None` instead of raising `ExtractionError`. Downstream code must handle `None` explicitly.

## Changes
```
 tests/red_team/__init__.py       |   1 +
 tests/red_team/conftest.py       | 183 ++++++
 tests/red_team/test_k1_...py     | 189 ++++++
 tests/red_team/test_k2_...py     | 205 ++++++
 tests/red_team/test_k3_...py     | 302 +++++++++
 tests/red_team/test_k4_...py     | 284 ++++++++
 tests/red_team/test_k5_...py     | 250 +++++++
 tests/red_team/test_k6_...py     | 193 ++++++
 8 files changed, 1803 insertions(+)
```

## Notes
- 146 total adversarial tests across 6 modules
- All tests pass; no blocking issues found
- Zero-division edge cases in `roofer_math` are properly handled by existing code
- Contract schemas correctly reject all malformed inputs tested
- HITL queue handles concurrent access, corruption, and overflow gracefully
