# Gamma Briefing — Node 4: Output Routing (CRM Adapters)

> **Workstream:** Gamma | **Branch:** `gamma/adapters` | **Scope:** `src/ontology_engine/node4_output/`

## Your Mission

Build CRM-specific output adapters that take calculated pipeline data and format it for Buildertrend (CSV), JobNimbus (QBO bridge CSV), and AccuLynx (REST API).

## Tasks

| ID      | Description                                                  | Priority | Dependencies | Status |
| ------- | ------------------------------------------------------------ | -------- | ------------ | ------ |
| TASK_G1 | Buildertrend CSV generator (assembly import format)          | High     | Beta output  | Todo   |
| TASK_G2 | JobNimbus QBO bridge CSV generator                           | High     | Beta output  | Todo   |
| TASK_G3 | Research AccuLynx partner API access for Material Order POST | Medium   | —            | Todo   |
| TASK_G4 | Deduplication logic for CRM imports                          | High     | TASK_G1, G2  | Todo   |

## Input Contract (Node 4 receives from Node 3)

```json
{
  "header": { "estimate_number": "str", "claim_number": "str|null" },
  "procurement_items": [
    {
      "category": "RFG",
      "description": "str",
      "physical_qty": 97,
      "physical_unit": "bundles",
      "trade": "roofing",
      "unit_cost": 25.5
    }
  ],
  "credit_items": [{ "transaction_type": "credit_return" }],
  "adjusted_totals": { "note": "O&P already stripped" }
}
```

Full schema: `src/ontology_engine/contracts/schemas.py` → `NODE_3_TO_4_SCHEMA`

## CRM Integration Notes

| CRM              | Method                  | Key Constraints                                                                                   |
| ---------------- | ----------------------- | ------------------------------------------------------------------------------------------------- |
| **Buildertrend** | CSV assembly import     | Published XLSX template. Fields: Cost Code, Title, Quantity, Unit, Unit Cost                      |
| **JobNimbus**    | QBO bridge (backdoor)   | No native product import. QBO Products & Services CSV. **Fatal error on duplicate Display Names** |
| **AccuLynx**     | REST API V2 (OAuth 2.0) | Material Order POST is **private/partner API**. Public API covers leads, contacts, webhooks only  |

## Critical Constraints

- **Duplication Paradox:** Append unique identifiers (job_id + timestamp) to every record. JobNimbus throws fatal errors on duplicates.
- **Async Price Sync:** Supplier catalog prices may be stale in CRM. Cross-reference live pricing if possible.
- **Data Integrity:** End-to-end integrity must be preserved from Node 1 input all the way through.

## Dependencies

This workstream **depends on Beta** being completed first. You need the Node 3→4 output format to be finalized. Check `contracts/schemas.py` for the latest schema.

## When You're Done

Update `HANDOFF.md` with what you completed and any blockers.
