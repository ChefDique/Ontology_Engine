# Alpha Briefing — Node 1: Ingestion (OCR + PII Redaction)

> **Workstream:** Alpha | **Branch:** `feature/agent-a-ingestion` | **Scope:** `src/ontology_engine/node1_ingestion/`, `tests/test_node1_ingestion/`

## Your Mission

Build the ingestion layer that accepts raw PDFs/images and outputs clean, PII-free text ready for LLM processing.

## Tasks

| ID      | Description                                                                | Priority | Status |
| ------- | -------------------------------------------------------------------------- | -------- | ------ |
| TASK_A1 | OCR router: detect native vs scanned PDF, route to pdfplumber or Tesseract | Critical | Todo   |
| TASK_A2 | PII redaction pipeline using Microsoft Presidio                            | Critical | Todo   |
| TASK_A3 | Token chunking for large documents exceeding LLM context windows           | High     | Todo   |
| TASK_A4 | Download + integrate 5 Xactimate PDF samples for testing (URLs below)      | Critical | Ready  |

## Training Sample PDFs (TASK_A4)

Download these publicly available samples into `tests/fixtures/sample_pdfs/`:

| #   | Name                   | URL                                                                                              | Key Feature                               |
| --- | ---------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------- |
| 1   | UP Help Fire Loss      | https://uphelp.org/wp-content/uploads/2020/09/rra-_uphelp_sample_xactimate_estimate.pdf          | Multi-page, building code upgrades        |
| 2   | Claims Delegates Draft | https://www.claimsdelegates.com/wp-content/uploads/2021/12/EXAMPLE001_ROUGH_DRAFT_CAR.pdf        | 10-column layout, REMOVE/REPLACE split    |
| 3   | Assistimate Structure  | https://www.assistimate.com/wp-content/uploads/2022/05/Example_Xactimate_Structure.pdf           | REDACTED fields, sketch data              |
| 4   | GAF Roofing            | https://www.gaf.com/en-us/document-library/documents/brochures-&-literature/xactimate-sample.pdf | Recap by Category validation              |
| 5   | Assistimate Contents   | https://www.assistimate.com/wp-content/uploads/2022/05/Example_Xactimate_Contents.pdf            | Non-spatial units (HR, MO, EA), TBD costs |

## Key Research Context

> **Reference:** `R&D-Unsynthesized/markdown/Xactimate Data Extraction Research Plan.md` (DOC_008)

The OCR pipeline must handle these critical structural variations:

- **9-column vs 10-column tables** — Standard valuation layout (DESCRIPTION, QTY, UNIT, PRICE, TAX, O&P, RCV, DEPREC, ACV) vs action-oriented layout (adds #, CAT, SEL, ACT, CALC columns and splits PRICE into REMOVE/REPLACE)
- **Room Statistics blocks** — Parse SF, LF, SY measurements that anchor line item quantities
- **Nested F9 notes** — Italicized/indented justification text must attach to parent line items, not orphan
- **Page-spanning tables** — Cache column alignment and active room across page breaks
- **Price List token** — Extract from header (e.g., `CASO8X_SEP18`) for version/locale identification

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
