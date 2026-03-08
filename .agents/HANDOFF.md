# Ontology Engine — Agent Handoff Registry

## Project Info

- **Name:** Ontology Engine
- **Stack:** Python 3.13, pytest, jsonschema
- **Default Branch:** master
- **Test:** `source .venv/bin/activate && pytest tests/ -v`
- **KB:** `ontology_kb.json` (7 layers, single source of truth)

## Letter Registry

| Letter | Workstream                          | Status                  | Branch                                |
| ------ | ----------------------------------- | ----------------------- | ------------------------------------- |
| A      | Alpha: Node 1 Ingestion             | 📋 Assigned             | `feature/agent-a-ingestion`           |
| B      | Beta: Nodes 2+3 Extraction+Calculus | 📋 Assigned             | `feature/agent-b-extraction-calculus` |
| C      | Gamma: Node 4 Output Adapters       | ⏳ Blocked (needs Beta) | `feature/agent-c-output-adapters`     |
| D      | Delta: UAD 3.6 R&D                  | 📋 Assigned             | `feature/agent-d-uad-research`        |

## Work Queue

1. Alpha + Beta (parallel — no dependency)
2. Gamma (after Beta merges)
3. Delta (independent, low priority)

## Last Session

- **Date:** 2026-03-07
- **Session:** Orchestrator (scaffolding + orchestrator install)
- **Completed:** Full project scaffold (62 files), KB with 7 docs + Layer 7 workstreams, 15/15 tests, orchestrator system installed
- **Next:** Dispatch Alpha + Beta agents
