# Agent A — Node 1: Ingestion (OCR + PII Redaction)

## Verify Results
- `pytest tests/test_node1_ingestion/ -v` — **PASS** (56 passed, 1 skipped)
- Contract validation (NODE_1_TO_2_SCHEMA) — **PASS**
- Scope boundary respected — **YES**

## Architecture Decision: Lightweight MVP Stack
Per earlier planning agent recommendation, heavy OCR/NLP deps deferred:
- **Skipped:** Tesseract (pytesseract), pdf2image, Presidio (spacy + ML models)
- **Using:** pdfplumber (native PDF), regex PII, word-based tokenizer
- **Upgrade path:** Presidio is a drop-in upgrade (code already has fallback logic)
- **Rationale:** 90%+ of Xactimate PDFs are software-generated (native text). Regex catches structured PII (SSNs, policy #s, emails, phones). Freeform name/address NER deferred.

## Shared File Requests
None — all work stayed within scope boundaries.

## Changes
```
 src/ontology_engine/node1_ingestion/__init__.py     |  63 +++++-
 src/ontology_engine/node1_ingestion/ocr_router.py   | 124 ++++++++++--
 src/ontology_engine/node1_ingestion/pii_sanitizer.py | 155 ++++++++++++++--
 src/ontology_engine/node1_ingestion/token_chunker.py | 137 +++++++++++++--
 tests/test_node1_ingestion/__init__.py               |   0
 tests/test_node1_ingestion/test_ocr_router.py        | 112 ++++++++++++
 tests/test_node1_ingestion/test_pii_sanitizer.py     | 109 ++++++++++++
 tests/test_node1_ingestion/test_pipeline_integration.py | 90 ++++++++++
 tests/test_node1_ingestion/test_token_chunker.py     |  98 ++++++++++
```

## Task Summary
| Task    | Description                          | Status |
|---------|--------------------------------------|--------|
| TASK_A1 | OCR router (pdfplumber, native only) | ✅ Done |
| TASK_A2 | PII redaction (regex + Presidio path)| ✅ Done |
| TASK_A3 | Token chunking (overlapping)         | ✅ Done |
| TASK_A4 | Sample PDFs (directory created)      | ⚠️ Deferred (URL download separate step) |

## Notes
- TASK_A4 (sample PDF downloads) deferred — fixture dir created at `tests/fixtures/sample_pdfs/`. Tests auto-skip if no PDFs present. Download can happen as a separate step.
- The `ingest()` pipeline function in `__init__.py` chains all 3 stages and validates output against `NODE_1_TO_2_SCHEMA` before returning.
- Presidio upgrade is zero-code-change: just `pip install presidio-analyzer presidio-anonymizer` and the sanitizer auto-detects and uses it.
