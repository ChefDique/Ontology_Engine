# Ontology Engine — Agent Handoff Registry

## Project Info

- **Name:** Ontology Engine
- **Stack:** Python 3.13, FastAPI, Supabase, Vite
- **Default Branch:** master
- **Test:** `source .venv/bin/activate && pytest tests/ -v`
- **KB:** `ontology_kb.json` v1.5.0
- **Supabase:** `fareqnzxhodvgdkboeff` (Adair AI org, us-west-1, free tier)

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
| M      | Mike: Backend API + Security        | ✅ Merged   | `src/ontology_engine/api.py`, `tests/test_api/` |
| N      | November: Frontend Wiring           | 📋 Ready    | `web/src/` — wire upload + history to real API  |
| O      | Oscar: Deployment                   | 📋 Ready    | Vercel (frontend) + Railway (backend)           |
| P      | Papa: App Documentation             | ✅ Merged   | `docs/`, `README.md`                            |

## Supabase Pivot (v1.5.0)

**What changed:** Replaced the planned access-code-gate + in-memory state with full Supabase integration.

**Why:**

- Auth (email/password + magic link) is production-grade and free — building from scratch would take hours and be less secure
- PostgreSQL with RLS gives per-user data isolation out of the box
- Storage bucket handles PDF uploads with per-user access policies
- Rate limits survive server restarts (durable DB-backed)
- $0/month on free tier — no cost increase

**Architecture:**

```
Frontend (Vercel) → Supabase (auth/db/storage) → FastAPI on Railway (compute) → Supabase (persist results)
```

**Impact on agents:**

- **N** scope changed: access-code-gate → wire upload to `/api/analyze` with JWT + wire `/api/history`
- **O** scope changed: add Vercel deploy for frontend, Railway for backend (Dockerfile needed)
- **P** unchanged

## Work Queue

1. ~~Alpha through Mike~~ **All merged** (A–M, 13 agents)
2. **November + Oscar + Papa** (parallel — all unblocked)
3. Delta (independent R&D, low priority)

## Known Issues

- ~~**PII SSN detection gap**~~ **FIXED**
- **Presidio email detection** may fail in 28K+ char text

## Last Session

- **Date:** 2026-03-09
- **Session:** Supabase pivot + Agent M merge
- **Completed:**
  - Agent M merged (Backend API + Security) — 22/22 tests → 460/460 full suite
  - Supabase project created (ontology-engine, Adair AI org)
  - 4 migrations: analyses, rate_limits, RLS policies, estimates storage
  - Backend: JWT auth, result persistence, /api/history endpoints
  - Frontend: login view, auth gate, Supabase JS client
  - Login page verified live at localhost:5173
  - KB bumped to v1.5.0
- **Next:** Fire N + O + P in parallel
