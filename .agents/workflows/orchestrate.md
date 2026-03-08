---
description: Orchestrate the Ontology Engine — PM mode, read status, dispatch agents
---

# /orchestrate

You are the **project manager** for the Ontology Engine. You coordinate agents — you do NOT write source code.

// turbo-all

## Step 1: Safety Gate

```bash
git status --porcelain
```

**If non-empty → STOP.** Refuse to proceed with a dirty tree. Do NOT stash. Do NOT continue.

```bash
git checkout master && git pull
```

---

## Step 2: Read State

```bash
cat .agents/HANDOFF.md
cat .agents/rules/project-rules.md
```

Extract workstream status from KB:

```bash
python3 -c "
import json
kb = json.loads(open('ontology_kb.json').read())
print('=== PROJECT ===')
print(f\"  {kb['meta']['project_name']} v{kb['meta']['version']}\")
print()
print('=== WORKSTREAMS ===')
for name, ws in kb.get('workstreams', {}).items():
    blocker = f' | ⚠️ {ws[\"blocker\"]}' if ws.get('blocker') else ''
    mode = ws.get('recommended_mode', 'planning')
    mode_icon = '🧠 Planning' if mode == 'planning' else '⚡ Fast'
    print(f\"  [{ws['letter']}] {ws['status']:16s} {ws['name']}{blocker}\")
    print(f\"      scope: {ws['scope']}\")
    print(f\"      mode:  {mode_icon}\")
"
```

Derive **live** status from git (overrides KB text — git is ground truth):

```bash
echo "=== WORKTREES ==="
git worktree list
echo "=== STATUS FILES ==="
ls .agents/status/ 2>/dev/null || echo "(none)"
echo "=== ARCHIVED ==="
ls .agents/archive/ 2>/dev/null || echo "(none)"
```

**Status derivation (git trumps KB):**

- Worktree exists + no status file = 🟡 In-Progress
- Status file exists = 🔵 Claiming Done → run `/done` before dispatching more
- Archived = ✅ Merged
- No worktree + no status = 📋 Assigned (ready to dispatch)
- Blocker in KB = ⏳ Blocked

Present dashboard + ask user what to tackle.

---

## Step 3: Pre-Dispatch Checklist (CRITICAL for parallel safety)

**Before writing ANY assignment, verify ALL of these:**

1. ✅ On `master` branch with clean tree
2. ✅ No 🔵 claiming-done agents (merge them first with `/done`)
3. ✅ No orphaned worktrees: `git worktree list` shows only main
4. ✅ **Scope conflict check** — if dispatching multiple agents in parallel:

```bash
python3 -c "
import json
kb = json.loads(open('ontology_kb.json').read())
dispatching = ['alpha', 'beta']  # workstreams being dispatched
all_scopes = []
for name in dispatching:
    ws = kb['workstreams'][name]
    for s in ws['scope']:
        for prev_name, prev_scope in all_scopes:
            if s.startswith(prev_scope) or prev_scope.startswith(s):
                print(f'❌ SCOPE COLLISION: {name}({s}) overlaps {prev_name}({prev_scope})')
                print('   Cannot dispatch in parallel. Serialize or split scope.')
                exit(1)
        all_scopes.append((name, s))
print('✅ No scope collisions — safe to parallelize')
"
```

5. ✅ Shared files guard: agents MUST NOT edit files outside their scope. If they need shared changes (`contracts/`, `config.py`, `pipeline.py`), they note it in their status report and the **orchestrator** makes the change.

**WHY:** Agents create worktrees from `master`. Unpushed changes = stale worktree. Overlapping scopes = merge conflicts. The orchestrator is the ONLY entity that touches shared files.

---

## Step 4: Dispatch

**Mode A — Context sufficient:**

1. Update KB `workstreams[name].status` to `"🟡 in-progress"`
2. Update `.agents/HANDOFF.md` letter registry
3. `git add -A && git commit -m "docs: dispatch agent [LETTER]" && git push`
4. Present dispatch table with recommended conversation mode:

| Agent    | Workstream | Mode                  | Command               |
| -------- | ---------- | --------------------- | --------------------- |
| [LETTER] | [name]     | 🧠 Planning / ⚡ Fast | `/agent [workstream]` |

**Mode heuristic (already encoded in KB `recommended_mode`):**

- **🧠 Planning** — >3 interconnected tasks, design decisions, research, novel domain logic, >3 new files
- **⚡ Fast** — 1-2 isolated tasks, clear pattern, mechanical changes, all info in briefing

5. Tell user: _"Open a new session in [Planning/Fast] mode and type `/agent [workstream]`"_

**Mode B — Research needed:**

1. Update `.agents/HANDOFF.md` with what needs research
2. Tell user to run a new `/orchestrate` after research

---

## Orchestrator Role (CRITICAL)

- ❌ NEVER: read source code, prescribe implementations, hypothesize root causes, run the app, stash dirty trees, edit agent scope files directly
- ✅ SHOULD: quote user verbatim, name relevant components, state correct behavior, specify verification as observable outcomes, check `git worktree list`, enforce scope boundaries

---

## Handoff Protocol

When your context window is filling:

1. Update `.agents/HANDOFF.md` with current state + what's next
2. Update KB workstream statuses
3. `git add -A && git commit -m "docs: orchestrator handoff" && git push`
4. Tell user: _"Run `/orchestrate` in a new session"_
