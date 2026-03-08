# Beta Briefing — Nodes 2+3: Semantic Extraction + Deterministic Calculus

> **Workstream:** Beta | **Branch:** `beta/core` | **Scope:** `src/ontology_engine/node2_extraction/` + `src/ontology_engine/node3_calculus/`

## Your Mission

Build the core Ontology Engine: LLM extracts raw data from Xactimate text → Python converts to physical material quantities.

## Tasks

| ID      | Description                                                  | Priority | Status         |
| ------- | ------------------------------------------------------------ | -------- | -------------- |
| TASK_B1 | Define rigid JSON extraction schema for Xactimate data       | Critical | Todo           |
| TASK_B2 | Engineer LLM prompt for semantic extraction (NO calculation) | Critical | Todo           |
| TASK_B3 | Build Roofer Math module (Squares→Bundles, pitch, waste)     | Critical | Partially done |
| TASK_B4 | Implement O&P stripping logic                                | Critical | Todo           |
| TASK_B5 | Implement negative quantity (credit_return) handling         | High     | Todo           |
| TASK_B6 | Implement F9 note collision detection with HITL gate         | High     | Todo           |
| TASK_B7 | Build multi-trade data splitting logic                       | Medium   | Todo           |

## Input Contract (Node 2 receives from Node 1)

```json
{
  "text": "str",
  "method": "native|ocr",
  "confidence": 0.95,
  "page_count": 3,
  "pii_redacted": true
}
```

## Output Contract (Node 3 → Node 4)

```json
{
  "header": {},
  "procurement_items": [
    {
      "category": "RFG",
      "physical_qty": 97,
      "physical_unit": "bundles",
      "trade": "roofing"
    }
  ],
  "credit_items": [{ "transaction_type": "credit_return" }],
  "adjusted_totals": { "note": "O&P stripped" },
  "hitl_flags": []
}
```

Full schemas: `src/ontology_engine/contracts/schemas.py`

## Key Domain Knowledge

### Roofer Math Formulas

| Conversion           | Formula       | Rule                         |
| -------------------- | ------------- | ---------------------------- |
| Squares → Bundles    | ×3            | Standard 3-bundle-per-square |
| Linear Feet → Pieces | ÷10           | Standard 10-ft pieces        |
| Pitch Waste          | +5%/+10%/+15% | low/medium/steep             |
| Bundle Rounding      | `math.ceil()` | **ALWAYS round UP**          |

### Lexicon Matrix (partial — expand from DOC_004)

- RFG = Roofing (SQ) | SID = Siding (SF) | DRY = Drywall (SF)
- GUT = Gutters (LF) | PLM = Plumbing (EA) | ELC = Electrical (EA)

## Constraints You Must Enforce

- **LLMs NEVER calculate** — Node 2 extracts raw values only. All math happens in Node 3.
- **CONST_002 (O&P):** Strip Overhead & Profit before CRM injection.
- **CONST_003 (Negatives):** Route negative quantities to `credit_return` path.
- **CONST_004 (F9 Notes):** Flag override notes, NEVER auto-resolve.

## Test Files

Write tests in `tests/test_node2_extraction/` and `tests/test_node3_calculus/`. `test_roofer_math.py` already has passing tests.

## When You're Done

Update `HANDOFF.md` with what you completed and any blockers.
