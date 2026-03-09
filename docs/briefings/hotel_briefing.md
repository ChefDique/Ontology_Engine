# H Briefing — Orchestrator Competitive Upgrades

> **Workstream:** Hotel | **Scope:** `~/.gemini/antigravity/skills/kb-orchestrator/`, `~/.gemini/antigravity/skills/kb-synthesizer/`

## Your Mission

Upgrade the kb-orchestrator and kb-synthesizer skills with features inspired by competitive analysis of 4 external orchestration tools. Each task has a `rationale` field explaining _why_ and _where the idea came from_.

## Context

A competitive analysis was conducted against:

- **Ralph** (snarktank) — autonomous agent loop with cross-session learning
- **PRD Planner** (jmichaelschmidt) — reasoning-level-aware task breakdown
- **PRD Implementation Planning** (meriley) — skill-to-task mapping
- **Agent Skills for Context Engineering** (muratcankoylan) — context budget theory

Full analysis: `.gemini/antigravity/brain/38a30f78-37d4-4b7d-a2a1-6fa0ea57c7fe/orchestration_comparison.md`

## Tasks

| ID      | Title                                            | Priority | Why                                                                                                                                                      |
| ------- | ------------------------------------------------ | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TASK_H1 | Add `progress.txt` cross-session learning        | High     | Ralph's key insight: agents append learnings (gotchas, patterns, conventions) to a persistent file. Future sessions read it for institutional knowledge. |
| TASK_H2 | Add `reasoning_level` field to KB tasks          | Medium   | PRD Planner sizes tasks by cognitive load (1-5). Orchestrator can recommend model/mode per workstream.                                                   |
| TASK_H3 | Add `skill` field to KB tasks                    | Medium   | PRD Impl Planning maps skills to tasks. Agent auto-loads the right skill when starting work.                                                             |
| TASK_H4 | Cross-reference kb-synthesizer ↔ kb-orchestrator | High     | Users need to understand the pipeline: **synthesize → orchestrate → agent → done**. Both SKILL.md files should reference each other.                     |
| TASK_H5 | Update `validate_kb.py` for new fields           | Medium   | Validator should warn when tasks lack `reasoning_level` or `skill` (optional but recommended).                                                           |

## Implementation Details

### TASK_H1 — progress.txt

- Create/append to `progress.txt` in the project root at the end of each `/agent` run
- Format: timestamped entries with workstream name, learnings, gotchas
- The `/agent` workflow should read `progress.txt` at startup (if it exists) for accumulated context
- The `/orchestrate` workflow should display recent entries in the dashboard
- **Example entry:**
  ```
  --- Agent A (2026-03-08) ---
  - pdfplumber handles native PDFs well but fails on scanned images
  - regex PII detection catches 90%+ of patterns without Presidio overhead
  - overlapping chunks at 200-token overlap works well for context continuity
  ```

### TASK_H2 — reasoning_level

- Add optional `reasoning_level` (1-5) to each task dict in KB Layer 7
- 1-2 = mechanical/fast (direct implementation, clear pattern)
- 3 = moderate (some design decisions)
- 4-5 = complex/planning (novel domain, research needed, multiple approaches)
- Orchestrator uses this to recommend session mode: 1-2 → ⚡ Fast, 3+ → 🧠 Planning
- Update `kb.py get` to display reasoning level
- Update `compile_briefing.py` to include it in task tables

### TASK_H3 — skill mapping

- Add optional `skill` field to task dicts naming which installed skill executes it
- Example: `{"id": "TASK_X1", "skill": "kb-synthesizer", ...}`
- Agent can then auto-read that skill's SKILL.md before starting the task
- Update `kb.py get` and `compile_briefing.py` to display skill assignments

### TASK_H4 — Cross-references

- Add to `kb-orchestrator/SKILL.md`: a "Related Skills" section noting that KBs are typically created by `kb-synthesizer`
- Add to `kb-synthesizer/SKILL.md`: a note that KBs can be operationalized via `kb-orchestrator`
- Document the full pipeline in both READMEs

### TASK_H5 — Validator updates

- Add optional field checks to `validate_kb.py`
- Warn (not error) if tasks lack `reasoning_level` or `skill`
- Report coverage: "12/15 tasks have reasoning_level, 8/15 have skill mapping"

## Scope Boundaries

You may edit files in:

- `~/.gemini/antigravity/skills/kb-orchestrator/`
- `~/.gemini/antigravity/skills/kb-synthesizer/SKILL.md` (cross-reference only)

Do NOT edit any files in the Ontology Engine repo itself.
