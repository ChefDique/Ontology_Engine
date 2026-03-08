# Agent G Assignment — LLM Integration for Node 2

## Problem

Node 2 (Semantic Extraction) has a working `extractor.py`, `lexicon_matrix.py`, `f9_detector.py`, and `prompt.py` — but the actual LLM call path is not wired to a live API. The extractor needs to call a real LLM (Gemini Flash recommended for cost) and return structured JSON matching `NODE_2_TO_3_SCHEMA`.

## Goal

Wire Node 2's extractor to call Google Gemini Flash via the `google-generativeai` SDK. Update `config.py` with the necessary settings. Ensure the extractor returns valid `NODE_2_TO_3_SCHEMA` output from real LLM responses.

## Scope

- `src/ontology_engine/node2_extraction/extractor.py`
- `src/ontology_engine/node2_extraction/prompt.py` (if prompt template needs adjustment)
- `src/ontology_engine/config.py`
- `tests/test_node2_extraction/` (add LLM integration tests with mocked responses)

**Do NOT modify:** `pipeline.py`, `hitl/`, `node1_ingestion/`, `node3_calculus/`, `node4_output/`, `contracts/`

## Context

### Existing Extractor Pattern

Read `src/ontology_engine/node2_extraction/extractor.py` to understand the current interface. The `extract()` function takes Node 1 output (text + metadata) and should return a dict matching `NODE_2_TO_3_SCHEMA`:

```python
{
    "header": {"estimate_number": "...", "claim_number": "...", "carrier": "...", "loss_date": "..."},
    "line_items": [{"category": "RFG", "description": "...", "quantity": 10.5, "unit_of_measure": "SQ", ...}],
    "totals": {"rcv": 15000.00, "depreciation": 2000.00, "acv": 13000.00, ...}
}
```

### Config (existing in `config.py`)

```python
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))
```

### Lexicon Matrix

`lexicon_matrix.py` has the mapping of Xactimate category codes (RFG, SID, DRY, etc.) to human-readable names. Use this in the prompt context.

### Constraint: LLMs Never Calculate (CONST_003)

Node 2 extracts RAW values only. It must NOT perform mathematical operations. All math happens in Node 3.

## Tasks

| ID      | Task                                          | Details                                                                                                                                                      |
| ------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| TASK_G1 | Add `google-generativeai` to `pyproject.toml` | Add as optional dependency under `[project.optional-dependencies]` llm group                                                                                 |
| TASK_G2 | Wire extractor to Gemini Flash                | Implement the LLM call in `extractor.py`. Send the extraction prompt with the ingested text. Parse the JSON response. Validate against `NODE_2_TO_3_SCHEMA`. |
| TASK_G3 | Update `config.py`                            | Set `LLM_PROVIDER` default to `google`, add `GEMINI_MODEL` setting (default `gemini-2.0-flash`).                                                             |
| TASK_G4 | Add response parsing + error handling         | Handle: malformed JSON from LLM, missing required fields, rate limits, API errors. Return structured error rather than crashing.                             |
| TASK_G5 | Write integration tests with mocked LLM       | Mock the Gemini API response. Test that valid LLM JSON maps to NODE_2_TO_3_SCHEMA. Test error cases (bad JSON, missing fields, API timeout).                 |

## Verify

```bash
source .venv/bin/activate
pytest tests/test_node2_extraction/ -v
# All tests pass (including new LLM integration tests)
```

Optionally (if GOOGLE_API_KEY is set):

```bash
python -c "from ontology_engine.node2_extraction import extract; print(extract.__doc__)"
# Should show the function's docstring without error
```

## Key Design Decisions

1. **Gemini Flash is the default** — cheapest option for structured extraction. ~$0.075/1M input tokens.
2. **Structured JSON output** — Use Gemini's JSON mode (`response_mime_type="application/json"`) to get clean output.
3. **Fallback pattern** — If LLM returns invalid JSON, retry once. If still invalid, flag for HITL review.
4. **Tests mock the API** — Never call a real LLM in CI. Use `unittest.mock.patch` on the Gemini client.
5. **Do NOT add `pyproject.toml` to scope** — If you need to add the dependency, note it in your status report and the orchestrator will handle it.
