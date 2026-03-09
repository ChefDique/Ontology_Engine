# Ontology Engine — Agent Handoff Registry

## Project Info

- **Name:** Ontology Engine
- **Stack:** Python 3.13, pytest, jsonschema
- **Default Branch:** master
- **Test:** `source .venv/bin/activate && pytest tests/ -v`
- **KB:** `ontology_kb.json` (7 layers, single source of truth)

## Letter Registry

| Letter | Workstream                          | Status         | Branch / Scope                                  |
| ------ | ----------------------------------- | -------------- | ----------------------------------------------- |
| A      | Alpha: Node 1 Ingestion             | ✅ Merged      | `feature/agent-a-ingestion`                     |
| B      | Beta: Nodes 2+3 Extraction+Calculus | ✅ Merged      | `feature/agent-b-extraction-calculus`           |
| C      | Gamma: Node 4 Output Adapters       | ✅ Merged      | `feature/agent-c-output-adapters`               |
| D      | Delta: UAD 3.6 R&D                  | 📋 Assigned    | `feature/agent-d-uad-research`                  |
| E      | Epsilon: kb-orchestrator Skill      | ✅ Complete    | `~/.gemini/antigravity/skills/kb-orchestrator/` |
| F      | Foxtrot: Pipeline Wiring + HITL     | ✅ Merged      | `feature/agent-f-pipeline-wiring`               |
| G      | Golf: LLM Integration (Gemini)      | ✅ Merged      | `feature/agent-g-llm-integration`               |
| H      | Hotel: Orchestrator Upgrades        | ✅ Merged      | `~/.gemini/antigravity/skills/kb-orchestrator/` |
| I      | India: Node 5 Estimate Comparator   | ✅ Merged      | `feature/agent-i-comparator`                    |
| J      | Juliet: Node 6 Supplement Report    | ✅ Merged      | `feature/agent-j-supplement-report`             |
| K      | Kilo: Red Team Suite                | 🟡 In-Progress | `feature/agent-k-red-team`                      |
| L      | Lima: UI Shell                      | 🟡 In-Progress | `feature/agent-l-ui-shell`                      |

## Work Queue

1. ~~Alpha + Beta (parallel)~~ **Both merged**
2. ~~Gamma (parallel with Alpha)~~ **Merged**
3. ~~Epsilon (skill build)~~ **Complete**
4. ~~Foxtrot + Golf (parallel)~~ **Both merged**
5. ~~Hotel (orchestrator upgrades)~~ **Merged**
6. ~~India (Node 5 Comparator)~~ **Merged**
7. ~~Juliet (Node 6 Supplement Report)~~ **Merged**
8. **Kilo + Lima (parallel)** — Red Team Suite + UI Shell (dispatched)
9. Delta (independent, low priority)

## Last Session

- **Date:** 2026-03-09
- **Session:** Orchestrator — Red Team + UI Shell dispatch
- **Completed:**
  - All MVP nodes (1-6) merged and wired
  - Defined workstream K: Kilo — Red Team Suite (6 tasks: adversarial tests across all nodes + pipeline)
  - Defined workstream L: Lima — UI Shell (5 tasks: Vite scaffold, upload, dashboard, report viewer, HITL UI)
  - Scope collision check: ✅ passed (K=`tests/red_team/`, L=`web/` — fully disjoint)
  - Updated KB to v1.3.0
  - Neither agent touches shared files (`contracts/`, `config.py`, `pipeline.py`)
- **Next:** Agents K and L work in parallel → `/done` each when complete → then Delta (D)
