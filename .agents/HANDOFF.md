# Ontology Engine — Agent Handoff Registry

## Project Info

- **Name:** Ontology Engine
- **Stack:** Python 3.13, pytest, jsonschema, FastAPI (incoming)
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
| K      | Kilo: Red Team Suite                | ✅ Merged      | `feature/agent-k-red-team`                      |
| L      | Lima: UI Shell                      | ✅ Merged      | `feature/agent-l-ui-shell`                      |
| M      | Mike: Backend API + Security        | 🟡 In-Progress | `src/ontology_engine/api.py`, `tests/test_api/` |
| N      | November: Frontend Wiring           | 📋 Assigned    | `web/src/` (blocked on M)                       |
| O      | Oscar: Deployment + Access          | 📋 Assigned    | `Dockerfile`, `.env.example`, `railway.toml`    |
| P      | Papa: App Documentation             | 📋 Assigned    | `docs/`, `README.md`                            |

## Work Queue

1. ~~Alpha + Beta (parallel)~~ **Both merged**
2. ~~Gamma (parallel with Alpha)~~ **Merged**
3. ~~Epsilon (skill build)~~ **Complete**
4. ~~Foxtrot + Golf (parallel)~~ **Both merged**
5. ~~Hotel (orchestrator upgrades)~~ **Merged**
6. ~~India (Node 5 Comparator)~~ **Merged**
7. ~~Juliet (Node 6 Supplement Report)~~ **Merged**
8. ~~Kilo + Lima (parallel)~~ **Both merged**
9. **Mike** (Backend API — FIRST, blocks N+O)
10. **November + Oscar + Papa** (parallel, after M merges)
11. Delta (independent, low priority)

## Known Issues

- ~~**PII SSN detection gap**~~ **FIXED** — regex secondary pass added (belt+suspenders for CONST_001)
- **Presidio email detection** may fail in 28K+ char text (chunk text before passing to Presidio)

## Last Session

- **Date:** 2026-03-09
- **Session:** /orchestrate — dispatch deployment agents (M, N, O, P)
- **Completed:**
  - Fixed SSN PII bug (regex secondary pass after Presidio)
  - 438 tests passing, 0 failures
  - Financial analysis: $0.0024/analysis, ~$5/mo at beta scale
  - Security plan: access code gate, IP rate limiter, kill switch, circuit breaker
  - KB bumped to v1.4.0
- **Next:** Fire Agent M (Backend API), then N+O+P in parallel after M merges
