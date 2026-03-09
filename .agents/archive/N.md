# Agent N — Frontend Wiring

## Verify Results
- `cd web && npm run build` — PASS (355ms, 51 modules)
- `cd web && npm test` — PASS (64/64 tests, 5 files)
- Contract validation — PASS
- Scope boundary respected — YES (only `web/src/` and `web/tests/`)

## Shared File Requests
None — no shared files needed.

## Changes
```
 web/src/components/history.js  | 222 ++++++++++++++++++++++++
 web/src/components/pipeline.js | 178 +++++++++++++++-----
 web/src/components/upload.js   | 272 +++++++++++++++++++++---------
 web/src/main.js                | 130 ++++++++------
 web/src/utils/state.js         | 128 ++++++++------
 web/tests/components.test.js   |   9 +
 web/tests/wiring.test.js       | 243 +++++++++++++++++++++++++++
 7 files changed, 814 insertions(+), 74 deletions(-)
```

## Notes
- The KB `november.blocker` is stale — says "Depends on Agent M" but mike is `✅ merged`. Orchestrator should clear the blocker field.
- The `history.js` component fetches from `/api/history` and `/api/history/{id}` which match the backend endpoints exactly.
- The upload wiring maps both `data.gap_report` and `data.report` from the API response to handle either shape.
- HITL flags are extracted from `gapReport.hitl_flags` or `report.hitl_flags` for flexibility.
