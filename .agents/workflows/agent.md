---
description: Run as a workstream agent — reads assignment from KB, creates worktree, builds
---

# /agent [workstream]

You are an **implementation agent** for a specific Ontology Engine workstream. You build, test, and verify — then report.

**Usage:** `/agent alpha` or `/agent beta` or `/agent gamma` or `/agent delta`

// turbo-all

## Step 1: Load Assignment

Read the project rules:

```bash
cat .agents/rules/project-rules.md
```

Extract your assignment from the KB:

```bash
python3 -c "
import json, sys
ws_name = '[WORKSTREAM]'  # replaced by user's argument
kb = json.loads(open('ontology_kb.json').read())
ws = kb['workstreams'].get(ws_name)
if not ws:
    print(f'❌ Unknown workstream: {ws_name}')
    print(f'Available: {list(kb[\"workstreams\"].keys())}')
    sys.exit(1)
print(f'=== Agent {ws[\"letter\"]}: {ws[\"name\"]} ===')
print(f'Scope:    {ws[\"scope\"]}')
print(f'Tasks:    {ws[\"tasks\"]}')
print(f'Verify:   {ws[\"verify\"]}')
print(f'Branch:   {ws[\"branch\"]}')
print(f'Briefing: {ws[\"briefing\"]}')
print(f'Contracts: {ws[\"contracts\"]}')
if ws.get('blocker'): print(f'⚠️ Blocker: {ws[\"blocker\"]}')
"
```

Read your briefing and contracts:

```bash
cat [BRIEFING_PATH]
cat src/ontology_engine/contracts/schemas.py
```

---

## Step 2: Create Worktree

```bash
git status --porcelain
```

**If non-empty → STOP.** Refuse with dirty tree.

```bash
git checkout master && git pull
git worktree add ../agent-[LETTER] -b [BRANCH]
```

**All work happens in `../agent-[LETTER]/` directory.** Do not work in the main repo directory.

---

## Step 3: Build

Work through your task list. For each task:

1. Implement the feature
2. Write tests
3. Run the verify command from your assignment
4. Ensure `contracts/schemas.py` validation passes for your node's output

**Scope boundary:** ONLY edit files in your `scope` directories. If you need to change shared files (`contracts/`, `pipeline.py`, `config.py`), note it in your status report and do NOT make the change.

---

## Step 4: Report

After all tasks are complete and tests pass:

```bash
cd ../agent-[LETTER]
git add -A
git commit -m "feat: implement [workstream name]"
git push -u origin [BRANCH]
```

Create completion report:

```bash
cat > .agents/status/[LETTER].md << 'EOF'
# Agent [LETTER] — [Workstream Name]

## Verify Checklist
- [ ] `[VERIFY_COMMAND]` — all tests pass
- [ ] Contract validation passes for [contracts]
- [ ] No files outside scope boundary were modified

## Changes
$(git diff master --stat)

## Status
$(git status --short)
EOF
git add .agents/status/[LETTER].md
git commit -m "docs: agent [LETTER] completion report"
git push
```

---

## Agent Rules (CRITICAL)

- ❌ NEVER edit `.agents/HANDOFF.md` (orchestrator-only)
- ❌ NEVER merge to master
- ❌ NEVER switch branches (worktree IS the branch)
- ❌ NEVER stash
- ✅ DO stay in worktree directory
- ✅ DO create status file as last action
- ✅ DO respect scope boundary
