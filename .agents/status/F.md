# Agent F — Pipeline Wiring + HITL + CLI

## Verify Results
- `pytest tests/test_pipeline/ tests/test_hitl/ -v` — **PASS** (45/45)
- Contract validation — **PASS** (all 3 inter-node schemas validated)
- Scope boundary respected — **YES**

## Shared File Requests
None. No shared files were modified.

## Changes
```
src/ontology_engine/__main__.py     | 217 +++ (NEW)
src/ontology_engine/hitl/__init__.py|  11 +-
src/ontology_engine/hitl/review_queue.py | 191 +++
src/ontology_engine/pipeline.py     | 246 +++
tests/test_hitl/__init__.py         |   0 (NEW)
tests/test_hitl/test_review_queue.py| 175 +++ (NEW)
tests/test_pipeline/__init__.py     |   0 (NEW)
tests/test_pipeline/test_cli.py     |  92 +++ (NEW)
tests/test_pipeline/test_pipeline.py| 321 +++ (NEW)
```

## Notes
- `python-dotenv` was installed in the venv during testing (was listed in pyproject.toml but not installed).
- Nodes 2–4 function calls use local imports in `run_pipeline()` so mocks must target source modules.
- HITL queue is on-disk JSON (`~/.ontology_engine/hitl_queue/`) — no database required for MVP.
