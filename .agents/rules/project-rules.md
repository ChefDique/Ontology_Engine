# Ontology Engine — Project Rules

## Mission

**The Ontology Engine is a universal analog-to-digital translation engine** — it converts unstructured proprietary documents into structured, system-ready data. The core methodology (Z→A / GOAS) is industry-agnostic: define the target output schema first, then reverse-engineer everything needed to get there.

**Phase 1 (current MVP):** Xactimate → Roofing CRM. Insurance restoration contractors waste hours re-entering estimate data from Xactimate (85-90% market share) into CRM systems (Buildertrend, JobNimbus, AccuLynx). Our 4-node pipeline ingests a PDF, extracts structured line items via LLM, applies deterministic roofer math, and routes CRM-ready CSV/JSON. This is "The Wedge" — fast time-to-revenue, immediate pain relief.

**Phase 2 (planned):** UAD 3.6 MISMO XML for real estate appraisers. Higher enterprise value, GSE certification requirements, longer runway. Same pipeline architecture, different lexicon and output adapters.

**Future verticals:** Construction, legal, logistics — anywhere a "Human API" bottleneck exists (manual re-entry of structured data trapped in proprietary formats).

**Legal constraint (CONST_006):** MVP uses PDF/OCR extraction only. ESX/XML parsing deferred pending EULA review. All files must be user-exported from the user's own license (CONST_007).

## Documentation & Tracking

- **Knowledge Base:** `ontology_kb.json` is the single source of truth (7 layers)
- **Workstreams:** KB Layer 7 (`workstreams`) holds all assignments and status
- **Briefings:** `docs/briefings/` — context-efficient compiled views (~2-4KB each)
- **Contracts:** `src/ontology_engine/contracts/schemas.py` — inter-node data contracts
- **ADRs:** `docs/adr/` — architecture decision records

## Architecture

- **4-Node Pipeline:** Ingestion → Extraction → Calculus → Output
- **Design by Contract:** Every node boundary validates via JSON Schema
- **LLMs never calculate:** Node 2 extracts raw values only; Node 3 does all math
- **PII redaction mandatory:** Before any data reaches LLMs (CONST_001)
- **O&P stripping mandatory:** Before CRM injection (CONST_002)

## Build & Test

```bash
source .venv/bin/activate
pytest tests/ -v                    # full suite
pytest tests/test_node3_calculus/ -v  # node-specific
python -m ruff check src/            # lint
```

## Git Workflow

- **Default branch:** `master`
- **Agent branches:** `feature/agent-[letter]-[description]`
- **Commit style:** Conventional (`feat:`, `fix:`, `docs:`, `test:`)
- **Worktrees:** Each agent works in `../agent-[letter]/` directory
- **Never commit to master directly** — only orchestrator merges via `/done`
- **Every commit must be followed by a push.** No exceptions. Other agents pull from origin — an unpushed commit is invisible to them and causes stale state. This applies to orchestrator KB updates, agent work, and `/done` merges equally.

## Agent Guidelines

- Be concise. Run tests after changes.
- Check if similar patterns exist before writing new code.
- Prefer editing existing files over creating new ones.
- Do NOT modify files outside your workstream's `scope`.
- Do NOT install new dependencies without checking `pyproject.toml`.
- Never disable contract validation or PII guards.
- Respect scope boundaries defined in KB Layer 7.
- **Always `git push` immediately after `git commit`.** Never leave committed work unpushed — parallel agents depend on origin being current.
