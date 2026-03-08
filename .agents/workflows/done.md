---
description: Verify, merge, and archive completed agent work
---

# /done

Verify completed agents, merge their branches, update KB status, and archive.

// turbo-all

## Step 1: Check for Completions

```bash
git status --porcelain
```

**If non-empty → STOP.** Refuse with dirty tree.

```bash
git checkout master && git pull
ls .agents/status/
git worktree list
```

For each status file found, the corresponding agent is 🔵 Claiming Done.

---

## Step 2: Verify Each Agent

For each claiming-done agent:

1. Read the status file: `cat .agents/status/[LETTER].md`
2. Read the original assignment from KB:

```bash
python3 -c "
import json
kb = json.loads(open('ontology_kb.json').read())
for name, ws in kb['workstreams'].items():
    if ws['letter'] == '[LETTER]':
        print(f'Verify: {ws[\"verify\"]}')
        print(f'Scope:  {ws[\"scope\"]}')
        print(f'Contracts: {ws[\"contracts\"]}')
"
```

3. Check the diff for scope violations: `git diff master..feature/agent-[letter] --stat`
4. Run verify command from KB on the agent's branch
5. Check for untracked files

---

## Step 3: Merge Verified Agents

For each verified agent:

```bash
git merge --no-ff feature/agent-[letter]-[desc] -m "feat: merge agent [LETTER] — [workstream name]"
source .venv/bin/activate && pytest -x
git worktree remove ../agent-[letter]
git branch -d feature/agent-[letter]-[desc]
```

---

## Step 4: Update State

```bash
mv .agents/status/[LETTER].md .agents/archive/[LETTER].md
```

Update KB workstream status:

```bash
python3 -c "
import json
kb = json.loads(open('ontology_kb.json').read())
for name, ws in kb['workstreams'].items():
    if ws['letter'] == '[LETTER]':
        ws['status'] = '✅ merged'
        ws['blocker'] = None
open('ontology_kb.json', 'w').write(json.dumps(kb, indent=2, ensure_ascii=False) + '\n')
print('✅ KB updated')
"
```

Update `.agents/HANDOFF.md` letter registry.

```bash
git add -A
git commit -m "docs: merge agent [LETTER], archive status"
git push
```

---

## Step 5: Report

```
✅ /done complete:

Merged:          [list]
Failed verify:   [list]
Still in-progress: [list]
Next ready:      [list]

Run /orchestrate to dispatch next workstream.
```

**Status Legend:**

- ✅ Merged (verified, worktree removed)
- 🟡 In-Progress (worktree exists, no status file)
- 🔵 Claiming Done (status file exists, not yet verified)
- ❌ Failed Verification (status file exists, verify failed)
- 📋 Assigned (no worktree, no status file)
- ⏳ Blocked (dependency not met)
