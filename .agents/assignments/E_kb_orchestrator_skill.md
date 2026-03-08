# Agent E Assignment — Build `kb-orchestrator` Skill

## Problem

The current orchestrator system (`/install-orchestrator`) installs markdown-based workflows (`AGENT_ASSIGNMENTS.md`, `HANDOFF.md`). These work but can't leverage a JSON knowledge base as single source of truth. The Ontology Engine project evolved a JSON-native variant (`ontology_kb.json` Layer 7 + briefing compilation + scope collision detection) that's more powerful. This needs to be generalized into a reusable skill with helper scripts, so any project can adopt it.

## Context

**Reference implementation (working):**

- `/Users/richardadair/ai_projects/Ontology_Engine/.agents/workflows/` — 3 local workflows (orchestrate, agent, done)
- `/Users/richardadair/ai_projects/Ontology_Engine/ontology_kb.json` — Layer 7 `workstreams` schema
- `/Users/richardadair/ai_projects/Ontology_Engine/docs/briefings/` — compiled briefing files

**Global templates to understand:**

- `~/.gemini/antigravity/global_workflows/install-orchestrator.md` — current markdown-based installer
- `~/.gemini/antigravity/global_workflows/improve-orchestrator.md` — bidirectional sync workflow

**Skill creation guide:**

- `~/.gemini/antigravity/skills/skill-creator/SKILL.md` — how to create skills

## Goal

Create `~/.gemini/antigravity/skills/kb-orchestrator/` with:

### SKILL.md

- Triggers: user has a `kb.json` or wants JSON-native orchestration
- Instructions for using each script
- How it differs from the markdown-based `/install-orchestrator`

### scripts/

| Script                | Purpose                                                                                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `preflight.py`        | Pre-dispatch safety: dirty tree guard, scope collision detection, blocker check, orphan worktree detection. Single command replaces 5+ inline checks. |
| `kb.py`               | Read/mutate KB: `kb.py status alpha "🟡 in-progress"`, `kb.py add-workstream`, `kb.py list`. Atomic JSON updates with validation.                     |
| `dashboard.py`        | Render workstream status table from KB Layer 7 + git state (worktrees, status files). One command replaces 3 separate queries.                        |
| `compile_briefing.py` | Auto-generate briefing markdown from KB layers 4+5+7 for a given workstream. Eliminates manual briefing maintenance.                                  |
| `validate_kb.py`      | JSON Schema validation for the KB itself — ensures structure integrity after mutations.                                                               |

### resources/

| File             | Purpose                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `kb_schema.json` | JSON Schema defining valid KB structure (meta, documents, ontology, pipeline, workstreams) |
| `sample_kb.json` | Minimal KB template for bootstrapping new projects                                         |

### examples/

| File                              | Purpose                                                |
| --------------------------------- | ------------------------------------------------------ |
| `sample_workflows/orchestrate.md` | Template orchestrate workflow that calls skill scripts |
| `sample_workflows/agent.md`       | Template agent workflow                                |
| `sample_workflows/done.md`        | Template done workflow                                 |

## Verify

1. `python3 scripts/preflight.py --help` runs without error
2. `python3 scripts/kb.py list` parses any valid KB JSON and prints workstreams
3. `python3 scripts/dashboard.py` produces a formatted table
4. `python3 scripts/validate_kb.py resources/sample_kb.json` passes
5. SKILL.md follows the format from `skill-creator/SKILL.md`

## Scope Boundary

- `~/.gemini/antigravity/skills/kb-orchestrator/` only
- Do NOT modify the Ontology Engine project files
- Do NOT modify `install-orchestrator.md` (that's a separate `/improve-orchestrator` run after skill is built)

## Key Design Decisions

1. **Scripts must be project-agnostic** — they accept KB path as argument, don't hardcode project paths
2. **Scripts must work without pip install** — use only stdlib + json (jsonschema optional with graceful fallback)
3. **KB schema is flexible** — validate structure not content (workstreams must exist, but trade names are project-specific)
4. **Skill complements, doesn't replace, the workflow system** — workflows call scripts, scripts do the heavy lifting
