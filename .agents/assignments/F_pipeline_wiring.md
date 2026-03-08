# Agent F Assignment — Pipeline Wiring + HITL + CLI

## Problem

Nodes 1–4 are all implemented and unit-tested (175 tests pass), but `pipeline.py` and `hitl/review_queue.py` are stubs (`NotImplementedError`). There is no way to actually run the pipeline end-to-end. There is no CLI entry point.

## Goal

Wire the 4-node pipeline into a working end-to-end flow with contract validation at each boundary, a functional HITL review queue, and a CLI entry point.

## Scope

- `src/ontology_engine/pipeline.py`
- `src/ontology_engine/hitl/review_queue.py`
- `src/ontology_engine/hitl/__init__.py`
- `src/ontology_engine/__main__.py` [NEW]
- `tests/test_pipeline/` [NEW directory]
- `tests/test_hitl/` [NEW directory]

**Do NOT modify:** `contracts/`, `config.py`, `node1_ingestion/`, `node2_extraction/`, `node3_calculus/`, `node4_output/`

## Context

### Inter-Node Contracts (in `contracts/schemas.py`)

- `NODE_1_TO_2_SCHEMA` — requires: `text`, `method`, `confidence`, `page_count`, `pii_redacted` (must be True), optional `chunks`
- `NODE_2_TO_3_SCHEMA` — requires: `header`, `line_items`, `totals`
- `NODE_3_TO_4_SCHEMA` — requires: `header`, `procurement_items`, `adjusted_totals`, optional `hitl_flags`, `credit_items`

### Existing Validators (in `contracts/validators.py`)

Use `jsonschema.validate()` with the schemas above at each node boundary.

### Node Entry Points

- Node 1: `from ontology_engine.node1_ingestion import ingest` → returns NODE_1_TO_2 dict
- Node 2: `from ontology_engine.node2_extraction import extract` → takes Node 1 output, returns NODE_2_TO_3 dict
- Node 3: `from ontology_engine.node3_calculus import calculate` → takes Node 2 output, returns NODE_3_TO_4 dict
- Node 4: `from ontology_engine.node4_output import route_output` → takes Node 3 output + target_crm, returns output file path

### HITL Design (CONST_005)

- **Invariant:** NEVER auto-POST to CRM. Human must explicitly approve.
- Queue items to a local JSON file (`~/.ontology_engine/review_queue.json` or a project-local path)
- Items are flagged for review when `hitl_flags` exist in Node 3 output (F9 overrides, low confidence, negative quantities)
- `queue_for_review(items, reason)` → returns dict with `queued_items`, `queue_id`, `reason`

## Tasks

| ID      | Task                              | Details                                                                                                                                              |
| ------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| TASK_F1 | Wire `pipeline.py`                | Chain Node 1→2→3→4 with `jsonschema.validate()` at each boundary. On validation failure, halt and return error with which boundary failed.           |
| TASK_F2 | Implement `hitl/review_queue.py`  | Queue flagged items to local JSON file. Support `queue_for_review()`, `list_queue()`, `approve_item(queue_id)`, `reject_item(queue_id)`.             |
| TASK_F3 | Add CLI entry point `__main__.py` | `python -m ontology_engine <pdf_path> <target_crm>`. Print results to stdout. Exit code 0 on success, 1 on validation error, 2 on HITL items queued. |
| TASK_F4 | Write integration tests           | Test the full pipeline with mocked node functions. Test contract validation failures at each boundary. Test HITL queue operations.                   |

## Verify

```bash
source .venv/bin/activate
pytest tests/test_pipeline/ tests/test_hitl/ -v
# All tests pass
python -m ontology_engine --help
# Shows usage
```

## Key Design Decisions

1. **Mock Node 2 in integration tests** — Node 2 calls an LLM, so mock its return value with a valid NODE_2_TO_3 payload. Agent G is wiring the LLM separately.
2. **Pipeline returns a result dict** — `{success, output_path, hitl_items, metadata}` as documented in the existing stub.
3. **HITL queue is local JSON** — No database. File-based is fine for MVP.
4. **CLI is thin** — Just parses args and calls `run_pipeline()`. No UI logic.
