# Agent C — Node 4: Output Routing (CRM Adapters)

## Verify Results

- `pytest tests/test_node4_output/ -v` — **PASS** (44/44, 0.04s)
- Contract validation — **PASS** (consumes NODE_3_TO_4_SCHEMA)
- Scope boundary respected — **YES**

## Tasks Completed

| ID      | Description                                         | Status  |
| ------- | --------------------------------------------------- | ------- |
| TASK_G1 | Buildertrend CSV generator (assembly import format) | ✅ Done |
| TASK_G2 | JobNimbus QBO bridge CSV generator                  | ✅ Done |
| TASK_G3 | AccuLynx partner API research + CSV fallback        | ✅ Done |
| TASK_G4 | Deduplication logic for CRM imports                 | ✅ Done |

## Implementation Summary

- **Buildertrend**: Maps Xactimate CAT codes → Buildertrend Cost Codes. CSV with columns: Cost Code, Title, Quantity, Unit, Unit Cost.
- **JobNimbus**: QBO Products & Services CSV with unique Display Names (dedup prevents fatal JN errors). Maps trade → QBO Income Account.
- **AccuLynx**: Dual export — JSON payload (for future partner API) + CSV fallback for manual upload. Documents that Material Order POST is partner-only.
- **Dedup**: Generates `{job_id}-{timestamp}-{index}` unique IDs. Shallow-copies records to avoid mutation.

## Shared File Requests

None — all work stayed within scope.

## Changes

```
src/ontology_engine/node4_output/acculynx_api.py    | 145 +++++++++++++++-
src/ontology_engine/node4_output/buildertrend_csv.py | 103 +++++++++++-
src/ontology_engine/node4_output/dedup.py            |  56 ++++++-
src/ontology_engine/node4_output/jobnimbus_qbo.py    | 115 ++++++++++++-
tests/test_node4_output/test_acculynx_and_dedup.py   | 175 ++++++++++++++++++
tests/test_node4_output/test_buildertrend_csv.py     | 134 +++++++++++++-
tests/test_node4_output/test_jobnimbus_qbo.py        | 130 +++++++++++++-
7 files changed, 858 insertions(+), 17 deletions(-)
```

## Notes

- AccuLynx Material Order POST requires partner API access (TASK_G3 research confirmed). CSV fallback is implemented and ready; when partner keys are obtained, swap `export()` to HTTP POST.
- All adapters integrate the dedup module automatically in `format_output()`.
