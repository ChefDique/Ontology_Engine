# Ontology Engine — Agent Handoff Registry

## Project Info

- **Name:** Ontology Engine
- **Stack:** Python 3.13, pytest, jsonschema
- **Default Branch:** master
- **Test:** `source .venv/bin/activate && pytest tests/ -v`
- **KB:** `ontology_kb.json` (7 layers, single source of truth)

## Letter Registry

| Letter | Workstream                          | Status      | Branch / Scope                                  |
| ------ | ----------------------------------- | ----------- | ----------------------------------------------- |
| A      | Alpha: Node 1 Ingestion             | ✅ Merged   | `feature/agent-a-ingestion`                     |
| B      | Beta: Nodes 2+3 Extraction+Calculus | ✅ Merged   | `feature/agent-b-extraction-calculus`           |
| C      | Gamma: Node 4 Output Adapters       | ✅ Merged   | `feature/agent-c-output-adapters`               |
| D      | Delta: UAD 3.6 R&D                  | 📋 Assigned | `feature/agent-d-uad-research`                  |
| E      | Epsilon: kb-orchestrator Skill      | ✅ Complete | `~/.gemini/antigravity/skills/kb-orchestrator/` |
| F      | Foxtrot: Pipeline Wiring + HITL     | ✅ Merged   | `feature/agent-f-pipeline-wiring`               |
| G      | Golf: LLM Integration (Gemini)      | ✅ Merged   | `feature/agent-g-llm-integration`               |
| H      | Hotel: Orchestrator Upgrades        | ✅ Merged   | `~/.gemini/antigravity/skills/kb-orchestrator/` |
| I      | India: Node 5 Estimate Comparator   | 📋 Assigned | `feature/agent-i-comparator`                    |
| J      | Juliet: Node 6 Supplement Report    | 📋 Assigned | `feature/agent-j-supplement-report`             |

## Work Queue

1. ~~Alpha + Beta (parallel)~~ **Both merged**
2. ~~Gamma (parallel with Alpha)~~ **Merged**
3. ~~Epsilon (skill build)~~ **Complete**
4. ~~Foxtrot + Golf (parallel)~~ **Both merged**
5. ~~Hotel (orchestrator upgrades)~~ **Merged**
6. **India (Node 5 Comparator)** — SERIALIZE FIRST (J depends on I's output contract)
7. **Juliet (Node 6 Supplement Report)** — after I merges
8. Red Team Suite (after I+J merge)
9. UI Shell (after I+J merge)
10. Delta (independent, low priority)

## Last Session

- **Date:** 2026-03-09
- **Session:** Orchestrator — supplement engine dispatch
- **Completed:**
  - Confirmed supplement_analysis layer in KB (product pivot: CRM import → supplement intelligence)
  - Defined workstream I: Node 5 Estimate Comparator (5 tasks — diff engine, O&P detection, depreciation audit)
  - Defined workstream J: Node 6 Supplement Report Generator (5 tasks — blocked on I's output contract)
  - Updated KB to v1.2.0
  - Scope collision check: ✅ passed (I and J have disjoint scopes)
  - Note: I touches `contracts/schemas.py` (shared file) — agent must add new contracts only, not modify existing ones
- **Next:** Dispatch Agent I → `/agent india` in Planning mode → `/done` → dispatch J
