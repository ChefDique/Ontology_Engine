---
description: Run as a workstream agent — reads assignment from KB, creates worktree, builds
---

# /agent [workstream]

You are an **implementation agent** for a specific Ontology Engine workstream.

**Usage:** `/agent alpha` | `/agent beta` | `/agent gamma` | `/agent delta`

// turbo-all

## Step 1: Safety Gate

```bash
git status --porcelain
```

**If non-empty → STOP.** Do NOT stash. Do NOT continue.

```bash
git checkout master && git pull
```

---

## Step 2: Load Assignment

```bash
cat .agents/rules/project-rules.md
```

Read your workstream from the KB (replace `[WORKSTREAM]` with argument):

```bash
python3 -c "
import json, sys
ws_name = '[WORKSTREAM]'
kb = json.loads(open('ontology_kb.json').read())
ws = kb['workstreams'].get(ws_name)
if not ws:
    print(f'❌ Unknown: {ws_name}. Available: {list(kb[\"workstreams\"].keys())}')
    sys.exit(1)
if ws.get('blocker'):
    print(f'⚠️  BLOCKED: {ws[\"blocker\"]}')
    print('Cannot proceed. Run /orchestrate to resolve blocker.')
    sys.exit(1)
print(f'Letter:    {ws[\"letter\"]}')
print(f'Name:      {ws[\"name\"]}')
print(f'Scope:     {ws[\"scope\"]}')
print(f'Tasks:     {ws[\"tasks\"]}')
print(f'Verify:    {ws[\"verify\"]}')
print(f'Branch:    {ws[\"branch\"]}')
print(f'Briefing:  {ws[\"briefing\"]}')
print(f'Contracts: {ws[\"contracts\"]}')
"
```

Read your briefing and contracts:

```bash
cat [BRIEFING_PATH]
cat src/ontology_engine/contracts/schemas.py
```

Read accumulated cross-session learnings (if they exist):

```bash
cat progress.txt 2>/dev/null || echo "No progress.txt yet — you are the first agent."
```

Use any relevant learnings from `progress.txt` to inform your implementation decisions.

---

## Step 3: Create Worktree

```bash
git worktree add ../agent-[LETTER] -b [BRANCH]
cd ../agent-[LETTER]
```

**ALL work happens in `../agent-[LETTER]/`.** Never return to the main repo.

---

## Step 4: Build

Work through your task list. For each task:

1. Implement the feature in your scope directories ONLY
2. Write tests
3. Run your verify command

### Scope Boundary Enforcement (CRITICAL)

You may **ONLY** edit files under your `scope` paths from KB Layer 7.

**If you need to change a shared file** (`contracts/`, `config.py`, `pipeline.py`, `pyproject.toml`):

1. Do NOT make the change
2. Note it in your status report under `## Shared File Requests`
3. The orchestrator will make the change on `master` after review

**WHY:** Parallel agents share `master`. If two agents both edit `contracts/schemas.py`, the second merge will conflict. Only the orchestrator edits shared files — it serializes those changes.

### Other Parallel Safety Rules

- **Never `git merge`** — you are on a feature branch, merging is orchestrator-only
- **Never `git stash`** — stashes create hidden state that corrupts worktree isolation
- **Never switch branches** — the worktree IS the branch
- **Never read/edit `../agent-X/`** — other agent worktrees are off-limits
- **Never edit `.agents/HANDOFF.md`** — orchestrator-only file

---

## Step 5: Verify

```bash
cd ../agent-[LETTER]
[VERIFY_COMMAND from KB]
```

If tests fail, fix them before proceeding. Do not submit with failing tests.

---

## Step 6: Report

```bash
cd ../agent-[LETTER]
git add -A
git commit -m "feat: implement [workstream name]

Tasks: [TASK_IDs]
Scope: [scope paths]"
git push -u origin [BRANCH]
```

Create completion report:

```bash
cat > .agents/status/[LETTER].md << 'REPORT'
# Agent [LETTER] — [Workstream Name]

## Verify Results
- `[VERIFY_COMMAND]` — PASS/FAIL
- Contract validation — PASS/FAIL
- Scope boundary respected — YES/NO

## Shared File Requests
(List any shared files you NEED changed but did NOT edit)

## Changes
```

git diff master --stat

```

## Notes
(Blockers, questions, or observations for orchestrator)
REPORT

git add .agents/status/[LETTER].md
git commit -m "docs: agent [LETTER] completion report"
git push
```

### Append Cross-Session Learnings

Append what you learned to `progress.txt` so future agents benefit. **Append only, never overwrite.**

```bash
cat >> progress.txt << 'LEARNINGS'

--- Agent [LETTER] ([WORKSTREAM_NAME], [DATE]) ---
- [What patterns, gotchas, or conventions you discovered]
- [What worked well or what to avoid]
- [Any tools, libraries, or approaches worth noting]
LEARNINGS

git add progress.txt
git commit -m "docs: agent [LETTER] cross-session learnings"
git push
```

---

## Agent Rules Summary

| Rule                                    | Reason                               |
| --------------------------------------- | ------------------------------------ |
| Stay in worktree                        | Isolation from other agents          |
| Only edit scope files                   | Prevents merge conflicts             |
| Never merge/stash/switch                | Worktree IS the branch               |
| Never edit HANDOFF.md                   | Orchestrator-only state              |
| Status file is last action              | Signals completion to `/done`        |
| Request shared changes, don't make them | Orchestrator serializes shared edits |
