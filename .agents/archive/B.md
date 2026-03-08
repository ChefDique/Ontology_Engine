# Agent B — Nodes 2+3: Semantic Extraction + Deterministic Calculus

## Verify Results
- `pytest tests/test_node2_extraction/ tests/test_node3_calculus/ -v` — **PASS** (71/71)
- Contract validation — **PASS** (schemas used in extractor validation)
- Scope boundary respected — **YES** (only edited node2_extraction/, node3_calculus/, and their tests)

## Shared File Requests
None required. All implementations use existing contracts from `schemas.py` and `validators.py` without modification.

## Changes
```
 14 files changed, 1039 insertions(+), 25 deletions(-)
```

### Node 2 — Semantic Extraction
- `prompt.py` — TASK_B1: Rigid JSON schema with VALID_CATEGORY_CODES, VALID_UNITS, EXTRACTION_OUTPUT_SCHEMA + TASK_B2: Enhanced system prompt with user prompt template
- `extractor.py` — TASK_B2: Full extraction orchestrator with LLM stub, markdown fence stripping, schema validation
- `f9_detector.py` — TASK_B6: F9 override detection via flag + text pattern matching, always resolution="pending" (CONST_004)

### Node 3 — Deterministic Calculus
- `roofer_math.py` — TASK_B3: calculate_material_quantities with converter dispatch table (RFG→bundles, GUT→pieces, SID/DRY→sheets) + new square_feet_to_sheets
- `oop_stripper.py` — TASK_B4: O&P stripping with Decimal arithmetic, proportional tax recalculation
- `credit_handler.py` — TASK_B5: Negative qty → credit_return routing with abs() for CRM, zero-qty exclusion
- `trade_splitter.py` — TASK_B7: Lexicon Matrix-based trade grouping with "general" fallback

## Notes
- LLM provider in `extractor.py` is a stub (`_call_llm` raises NotImplementedError) — designed for mocked testing. Actual API wiring is a separate integration task.
- Lexicon Matrix has 8 codes mapped. `TODO` comment preserved for expanding to full ~50 from DOC_004.
- No dependencies added to `pyproject.toml`.
