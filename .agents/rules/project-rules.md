# Ontology Engine — Project Rules

## Mission

**We are building an automated Xactimate-to-CRM translation engine.** Insurance restoration contractors currently waste hours manually re-entering estimate data from Xactimate (the industry-standard estimating tool, 85-90% market share) into their CRM systems (Buildertrend, JobNimbus, AccuLynx). Our 4-node pipeline ingests an Xactimate PDF, extracts structured line items via LLM, applies deterministic roofer math (waste factors, O&P stripping, unit conversions), and routes the output as CRM-ready CSV/JSON.

**Who it's for:** Roofing and restoration contractors in the US market.

**Why it matters:** No tool does this end-to-end today. Existing integrations are shallow (file status only) or locked inside Verisk's walled garden. We sit in the gap between the estimate and the CRM — "The Wedge."

**Legal constraint (CONST_006):** MVP uses PDF/OCR extraction only. ESX/XML parsing is deferred pending legal counsel review of the Xactimate EULA. All processed files must be user-exported from their own licensed Xactimate (CONST_007).

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

## Agent Guidelines

- Be concise. Run tests after changes.
- Check if similar patterns exist before writing new code.
- Prefer editing existing files over creating new ones.
- Do NOT modify files outside your workstream's `scope`.
- Do NOT install new dependencies without checking `pyproject.toml`.
- Never disable contract validation or PII guards.
- Respect scope boundaries defined in KB Layer 7.
