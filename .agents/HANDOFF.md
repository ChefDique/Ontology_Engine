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
| I      | India: Node 5 Estimate Comparator   | ✅ Merged   | `feature/agent-i-comparator`                    |
| J      | Juliet: Node 6 Supplement Report    | ✅ Merged   | `feature/agent-j-supplement-report`             |
| K      | Kilo: Red Team Suite                | ✅ Merged   | `feature/agent-k-red-team`                      |
| L      | Lima: UI Shell                      | ✅ Merged   | `feature/agent-l-ui-shell`                      |

## Work Queue

1. ~~Alpha + Beta (parallel)~~ **Both merged**
2. ~~Gamma (parallel with Alpha)~~ **Merged**
3. ~~Epsilon (skill build)~~ **Complete**
4. ~~Foxtrot + Golf (parallel)~~ **Both merged**
5. ~~Hotel (orchestrator upgrades)~~ **Merged**
6. ~~India (Node 5 Comparator)~~ **Merged**
7. ~~Juliet (Node 6 Supplement Report)~~ **Merged**
8. ~~Kilo + Lima (parallel)~~ **Both merged**
9. Delta (independent, low priority)

## Known Issues

- **PII SSN detection gap** (found by Agent K red team): Presidio's `US_SSN` recognizer misses SSNs with label prefixes (e.g., "SSN: 123-45-6789"). Pre-existing bug in Node 1. Consider regex secondary pass.

## Last Session

- **Date:** 2026-03-09
- **Session:** /done — merge agents K + L
- **Completed:**
  - Merged Agent K: Red Team Suite — 146 adversarial tests across all 6 nodes + pipeline
  - Merged Agent L: UI Shell — Vite + vanilla JS frontend (upload, dashboard, report viewer, HITL review)
  - Resolved KB merge conflict (both agents updated ontology_kb.json independently)
  - Preserved cross-session learnings from both agents (11 total in KB)
  - Cleaned up worktrees and archived status files
  - KB at v1.3.0, all 12 workstreams (A-L) accounted for
- **Next:** Delta (D) — Phase 2 UAD 3.6 R&D (only remaining workstream)
