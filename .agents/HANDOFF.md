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
| F      | Foxtrot: Pipeline Wiring + HITL     | 🟡 In-Progress | `feature/agent-f-pipeline-wiring`               |
| G      | Golf: LLM Integration (Gemini)      | 🟡 In-Progress | `feature/agent-g-llm-integration`               |

## Work Queue

1. ~~Alpha + Beta (parallel)~~ **Both merged**
2. ~~Gamma (parallel with Alpha)~~ **Merged**
3. ~~Epsilon (skill build)~~ **Complete**
4. **Foxtrot + Golf** (parallel — no scope overlap, MVP critical path)
5. Hotel: Red Team Suite (after F+G merge)
6. India: UI Shell (after F+G merge)
7. Delta (independent, low priority)

## Last Session

- **Date:** 2026-03-08
- **Session:** Orchestrator — dispatch F + G
- **Completed:**
  - Marked Agent E complete (kb-orchestrator skill verified)
  - Synthesized DOC_010 (legal risk analysis) into KB — CONST_006-008, RISK_003-005
  - Wrote F assignment (pipeline.py + HITL + CLI, 4 tasks)
  - Wrote G assignment (Gemini Flash → Node 2, 5 tasks)
  - Scope collision check: ✅ passed
- **Next:** Agents F + G execute in parallel → `/done` → dispatch H (Red Team) + I (UI Shell)
