# Ontology Engine — Agent Handoff Registry

## Project Info

- **Name:** Ontology Engine
- **Stack:** Python 3.13, pytest, jsonschema
- **Default Branch:** master
- **Test:** `source .venv/bin/activate && pytest tests/ -v`
- **KB:** `ontology_kb.json` (7 layers, single source of truth)

## Letter Registry

| Letter | Workstream                          | Status                          | Branch                                |
| ------ | ----------------------------------- | ------------------------------- | ------------------------------------- |
| A      | Alpha: Node 1 Ingestion             | 📋 Assigned (ready to dispatch) | `feature/agent-a-ingestion`           |
| B      | Beta: Nodes 2+3 Extraction+Calculus | ✅ Merged                       | `feature/agent-b-extraction-calculus` |
| C      | Gamma: Node 4 Output Adapters       | 📋 Assigned (ready to dispatch) | `feature/agent-c-output-adapters`     |
| D      | Delta: UAD 3.6 R&D                  | 📋 Assigned                     | `feature/agent-d-uad-research`        |

## Work Queue

1. ~~Alpha + Beta (parallel — no dependency)~~ **Beta merged**
2. **Alpha + Gamma** (parallel — no scope overlap, both now unblocked)
3. Delta (independent, low priority)

## Last Session

- **Date:** 2026-03-07
- **Session:** Orchestrator (R&D synthesis + dispatch prep)
- **Completed:**
  - Synthesized DOC_008 (Xactimate Data Extraction Research Plan) into KB — 5 public PDF sample URLs identified
  - Synthesized DOC_009 (GOAS Hybrid Architecture Summary) into KB
  - Resolved TASK_A4 blocker (Xactimate samples now available via public URLs)
  - Unblocked Gamma (Beta merged, Node 3→4 contract finalized)
  - Enriched Alpha briefing with PDF URLs and OCR research context
  - Updated Gamma briefing to reflect Beta completion
- **Next:** Dispatch Alpha + Gamma agents in parallel
