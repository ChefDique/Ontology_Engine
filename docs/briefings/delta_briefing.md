# Delta Briefing — Phase 2 R&D: UAD 3.6 / MISMO XML

> **Workstream:** Delta | **Branch:** `delta/research` | **Scope:** `docs/research/`

## Your Mission

Research and document the UAD 3.6 MISMO XML schema to prepare the Ontology Engine for Phase 2 (real estate appraisal automation). This is R&D only — no production code.

## Tasks

| ID      | Description                                                         | Priority | Status |
| ------- | ------------------------------------------------------------------- | -------- | ------ |
| TASK_D1 | Research UAD 3.6 MISMO XML schema specifications                    | Low      | Todo   |
| TASK_D2 | Identify GSE submission API requirements (Fannie Mae / Freddie Mac) | Low      | Todo   |
| TASK_D3 | Map appraisal data friction points to Ontology Engine architecture  | Low      | Todo   |

## Key Context

- **UAD 3.6** replaces the old static URAR 1004 PDF form with dynamic MISMO XML
- Fannie Mae and Freddie Mac are mandating this — every appraiser will need it
- The Ontology Engine's Node 2 architecture must support swapping the "Roofing Translation Dictionary" for an "Appraisal Translation Dictionary"
- The UAD mapping includes **Condition Ratings (C1-C6)** and **Quality Ratings (Q1-Q6)**

## UAD Mapping Logic (from DOC_007)

```
Input:   Xactimate Category/Selector Code (e.g., RFG 240) + UOM (Squares)
ConTech: Physical materials (Bundles, Nails, Ridge Cap) for CRM procurement
PropTech: MISMO 3.6 XML Condition Rating (C1-C6) + Quality Rating (Q1-Q6)
```

## Deliverables

Write all output to `docs/research/uad_36_analysis.md`:

1. UAD 3.6 XML tree structure
2. Required fields for property condition submission
3. C1-C6 and Q1-Q6 rating definitions
4. Cross-reference with Node 2 extraction schema — can the same architecture serve both?
5. GSE certification requirements and timeline

## When You're Done

Update `HANDOFF.md` with your findings and any blocking questions.
