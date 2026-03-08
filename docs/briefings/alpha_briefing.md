# Alpha Briefing — Node 1: Ingestion (OCR + PII Redaction)

> **Workstream:** Alpha | **Branch:** `alpha/node1` | **Scope:** `src/ontology_engine/node1_ingestion/`

## Your Mission

Build the ingestion layer that accepts raw PDFs/images and outputs clean, PII-free text ready for LLM processing.

## Tasks

| ID      | Description                                                                | Priority | Status                 |
| ------- | -------------------------------------------------------------------------- | -------- | ---------------------- |
| TASK_A1 | OCR router: detect native vs scanned PDF, route to pdfplumber or Tesseract | Critical | Todo                   |
| TASK_A2 | PII redaction pipeline using Microsoft Presidio                            | Critical | Todo                   |
| TASK_A3 | Token chunking for large documents exceeding LLM context windows           | High     | Todo                   |
| TASK_A4 | Acquire 5+ diverse Xactimate PDF samples for testing                       | Critical | Blocked (human action) |

## Output Contract (Node 1 → Node 2)

Your output MUST validate against this schema before passing to Node 2:

```json
{
  "text": "string (min 1 char)",
  "method": "native | ocr",
  "confidence": "float 0.0–1.0",
  "page_count": "int >= 1",
  "pii_redacted": true,
  "chunks": [
    { "chunk_text": "str", "chunk_index": "int", "token_count": "int" }
  ]
}
```

Full schema: `src/ontology_engine/contracts/schemas.py` → `NODE_1_TO_2_SCHEMA`

## Constraints You Must Enforce

- **CONST_001 (PII Redaction):** ALL PII (names, addresses, SSNs, policy numbers) must be masked BEFORE any data reaches the LLM. Zero PII in output — no exceptions.
- **RISK_004 (OCR Volatility):** Scanned vs native PDFs produce vastly different text quality. Detect PDF type first, route accordingly, and attach confidence scores.
- **RISK_003 (Token Limits):** Large PDFs may exceed LLM context windows. Implement overlapping chunk strategy.

## Tools

- `pdfplumber` — native PDF text extraction
- `pytesseract` — OCR for scanned images
- `presidio-analyzer` + `presidio-anonymizer` — PII detection/redaction
- `Pillow` — image preprocessing for OCR

## Test Files

Write tests in `tests/test_node1_ingestion/`. Sample PDFs go in `tests/fixtures/sample_pdfs/`.

## When You're Done

Update `HANDOFF.md` with what you completed and any blockers.
