# Ontology Engine — Complete Product Requirements Document

> **Generated from:** `ontology_kb.json` (v1.0.0)
> **Date:** 2026-03-08
> **Methodology:** Z → A Reverse Extrapolation Pipeline (GOAS)
> **MVP Window:** 2 days

---

## 1. Problem Statement

Skilled professionals currently act as **"Human APIs"** — manually translating unstructured data (Xactimate estimates, blueprints, legal documents, real estate appraisals) into structured formats required by downstream systems (CRMs, ERPs, procurement platforms). This creates:

- **Latency:** Hours to days per translation
- **Cost:** $25–150/hour for skilled human translators
- **Error Cascades:** 2–15% error rates in manual data entry
- **Scale Ceiling:** Capacity is limited by the number of humans available

**The Ontology Engine** eliminates this bottleneck by automating the full translation pipeline using a 4-node agentic architecture that separates semantic extraction (LLMs) from deterministic calculation (Python), enforced by Design by Contract at every boundary.

---

## 2. Target Markets

| Phase       | Market                                                  | Rationale                                                                                                                                   | Priority      |
| ----------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **Phase 1** | Roofing Contractors (Xactimate → CRM)                   | Fastest time-to-revenue. Clear pain point, existing contractor relationships. Three target CRMs with documented integration paths.          | **Immediate** |
| **Phase 2** | Real Estate Appraisers (Field Data → UAD 3.6 MISMO XML) | Higher enterprise value and competitive moat due to GSE certification requirements (Fannie Mae / Freddie Mac). Longer development timeline. | Future        |
| Future      | Custom Cabinetry (CAD → CNC G-code)                     | High-value friction point: skilled CNC programmers cost $60–100/hr and are in short supply.                                                 | Research      |
| Future      | Legal Discovery (Documents → Review DB)                 | Massive market ($15B+) but well-established eDiscovery platforms already using AI/ML.                                                       | Research      |
| Future      | Commercial Real Estate (Leases → Structured Data)       | Lease abstraction, CAM reconciliation, tenant billing.                                                                                      | Research      |
| Future      | Logistics / Supply Chain (BOL → Systems)                | Bill of Lading processing, customs documentation.                                                                                           | Research      |

---

## 3. System Architecture

### 3.1 Core Design Principles

1. **Output-First (Z → A):** Define the final, mathematically verifiable output schema (Z) before any code is written. Work backward to deduce all prerequisite data structures and transformations.
2. **Design by Contract (DbC):** Every agent-to-agent handoff enforces preconditions, postconditions, and invariants via JSON schema validation.
3. **Agentic V-Model:** Acceptance criteria and test cases are defined BEFORE generative execution begins.
4. **LLMs Never Calculate:** Semantic extraction is strictly separated from deterministic calculus. LLMs extract raw values; Python does the math.
5. **Human-in-the-Loop (HITL) Gates:** High-uncertainty outputs require human approval before propagation.

### 3.2 The 4-Node Pipeline

```
┌─────────────┐    ┌──────────────────┐    ┌───────────────────────┐    ┌────────────────┐
│   NODE 1    │    │     NODE 2       │    │       NODE 3          │    │    NODE 4       │
│  INGESTION  │───▶│   SEMANTIC       │───▶│   DETERMINISTIC       │───▶│   OUTPUT        │
│             │    │   EXTRACTION     │    │   CALCULUS            │    │   ROUTING       │
│ OCR + PII   │    │   (LLM)          │    │   (Python)            │    │   (CSV/API)     │
└─────────────┘    └──────────────────┘    └───────────────────────┘    └────────────────┘
```

#### Node 1 — Ingestion

| Field              | Value                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| **Inputs**         | Raw PDF (native or scanned), Image files (JPG, PNG, TIFF)                                               |
| **Outputs**        | Clean text with metadata, PII-redacted content                                                          |
| **Tools**          | Tesseract OCR, AWS Textract, Microsoft Presidio                                                         |
| **Preconditions**  | File is a valid PDF or image format; file size within processing limits                                 |
| **Postconditions** | Output is clean text string; no PII remains in output; OCR confidence score attached to each text block |
| **Invariants**     | **Zero PII in output — no exceptions**                                                                  |

#### Node 2 — Semantic Extraction

| Field              | Value                                                                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Inputs**         | PII-redacted text from Node 1                                                                                                                   |
| **Outputs**        | Structured JSON matching rigid extraction schema                                                                                                |
| **Tools**          | LLM (GPT-4 / Claude / Gemini), JSON Schema Validator                                                                                            |
| **Preconditions**  | Input text is PII-free; input text is within LLM context window (or chunked)                                                                    |
| **Postconditions** | Output JSON validates against defined schema; all Xactimate codes from input are present in output; NO calculations performed — raw values only |
| **Invariants**     | **LLM never performs arithmetic; LLM never invents data not present in source**                                                                 |

#### Node 3 — Deterministic Calculus

| Field              | Value                                                                                                                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Inputs**         | Structured JSON from Node 2                                                                                                                                                               |
| **Outputs**        | Calculated JSON with physical units, quantities, and costs                                                                                                                                |
| **Tools**          | Python (NumPy/custom), Roofer Math library                                                                                                                                                |
| **Preconditions**  | Input JSON passes schema validation; all required fields present (area, pitch, code)                                                                                                      |
| **Postconditions** | All quantities converted to physical units (bundles, pieces, rolls); O&P stripped from cost calculations; negative quantities flagged as `credit_return`; bundle counts always rounded UP |
| **Invariants**     | **No floating-point rounding errors in currency; O&P never applied twice**                                                                                                                |

#### Node 4 — Output Routing

| Field              | Value                                                                                                                             |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| **Inputs**         | Calculated JSON from Node 3                                                                                                       |
| **Outputs**        | CRM-specific payload (CSV or API JSON)                                                                                            |
| **Tools**          | CSV generator, REST API client, CRM adapter modules                                                                               |
| **Preconditions**  | Input JSON passes calculated schema validation; target CRM identified and adapter available                                       |
| **Postconditions** | Output matches target CRM import format exactly; deduplication identifiers appended; import/API call returns success confirmation |
| **Invariants**     | **Data integrity preserved end-to-end from Node 1 input to Node 4 output**                                                        |

### 3.3 Key Data Structures

#### Lexicon Matrix

Mapping of ~50 core Xactimate category codes (RFG, SID, DRY, etc.) to their semantic meanings, physical units, and supplier equivalents. This is the foundation for semantic extraction in Node 2.

#### Roofer Math Formulas

| Conversion           | Formula              | Rule                                                         |
| -------------------- | -------------------- | ------------------------------------------------------------ |
| Squares → Bundles    | ×3                   | Standard 3-bundle-per-square                                 |
| Linear Feet → Pieces | ÷10                  | Standard 10-ft starter/ridge pieces                          |
| Pitch Waste Factor   | +15% for steep pitch | Configurable per pitch category                              |
| Bundle Rounding      | `ceil()`             | **ALWAYS round UP — never round down on physical materials** |

---

## 4. Workstreams

### 4.1 Workstream Alpha — Ingestion, OCR & Sanitization

**Pipeline Node:** NODE_1

| Task ID | Description                                                           | Priority | Dependencies | Status |
| ------- | --------------------------------------------------------------------- | -------- | ------------ | ------ |
| TASK_A1 | Build OCR router (Tesseract for scanned, direct parse for native PDF) | Critical | —            | Todo   |
| TASK_A2 | Implement PII redaction pipeline using Microsoft Presidio             | Critical | TASK_A1      | Todo   |
| TASK_A3 | Build token chunking strategy for large documents                     | High     | TASK_A1      | Todo   |
| TASK_A4 | Acquire 5+ diverse Xactimate PDF samples for testing                  | Critical | —            | Todo   |

**Acceptance Criteria:** OCR produces clean text from both native and scanned PDFs with PII fully redacted. Token chunking handles documents exceeding LLM context windows.

---

### 4.2 Workstream Beta — Ontology Engine Core

**Pipeline Nodes:** NODE_2 + NODE_3

| Task ID | Description                                                                        | Priority | Dependencies | Status |
| ------- | ---------------------------------------------------------------------------------- | -------- | ------------ | ------ |
| TASK_B1 | Define rigid JSON extraction schema for Xactimate data                             | Critical | —            | Todo   |
| TASK_B2 | Engineer LLM prompt for semantic extraction (no calculation)                       | Critical | TASK_B1      | Todo   |
| TASK_B3 | Build Roofer Math Python module (Squares→Bundles, pitch adjustment, waste factors) | Critical | TASK_B1      | Todo   |
| TASK_B4 | Implement O&P stripping logic                                                      | Critical | TASK_B3      | Todo   |
| TASK_B5 | Implement negative quantity (`credit_return`) handling                             | High     | TASK_B3      | Todo   |
| TASK_B6 | Implement F9 note collision detection with HITL gate                               | High     | TASK_B2      | Todo   |
| TASK_B7 | Build multi-trade data splitting logic                                             | Medium   | TASK_B1      | Todo   |

**Acceptance Criteria:** LLM extracts all Xactimate codes into valid JSON without performing any calculations. Python module correctly converts all values to physical units with proper rounding, O&P handling, and `credit_return` flagging.

---

### 4.3 Workstream Gamma — Destination Adapters

**Pipeline Node:** NODE_4

| Task ID | Description                                                  | Priority | Dependencies     | Status |
| ------- | ------------------------------------------------------------ | -------- | ---------------- | ------ |
| TASK_G1 | Build Buildertrend CSV generator (assembly import format)    | High     | TASK_B3          | Todo   |
| TASK_G2 | Build JobNimbus QBO bridge CSV generator                     | High     | TASK_B3          | Todo   |
| TASK_G3 | Research AccuLynx partner API access for Material Order POST | Medium   | —                | Todo   |
| TASK_G4 | Build deduplication logic for CRM imports                    | High     | TASK_G1, TASK_G2 | Todo   |

**Acceptance Criteria:** CSV generators produce valid import files for Buildertrend and JobNimbus. AccuLynx API research completed with partner access path documented.

**CRM Integration Notes:**

| CRM              | Integration Method      | Key Constraints                                                                                                                  |
| ---------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Buildertrend** | CSV assembly import     | Published XLSX template with documented field limits                                                                             |
| **JobNimbus**    | QBO bridge (backdoor)   | No native product import; strict deduplication on Display Name (fatal error on duplicates)                                       |
| **AccuLynx**     | REST API V2 (OAuth 2.0) | Material Order POST is a private/partner API — not publicly documented. Public API covers leads, contacts, webhooks, financials. |

**Critical Constraint — Duplication Paradox:** CRMs enforce strict deduplication. JobNimbus throws fatal errors on duplicate Display Names. The engine MUST append unique identifiers (job site number, timestamp, project ID) to every record.

**Critical Constraint — Async Price Sync:** Price sync latency between supplier catalogs and CRM product libraries (e.g., QBO-to-JobNimbus sync) can cause stale data. The engine should cross-reference live supplier APIs (ABC Supply, SRS Distribution) as final validation.

---

### 4.4 Workstream Delta — Phase 2 R&D

**Pipeline Node:** Future

| Task ID | Description                                                           | Priority | Dependencies | Status |
| ------- | --------------------------------------------------------------------- | -------- | ------------ | ------ |
| TASK_D1 | Research UAD 3.6 MISMO XML schema specifications                      | Low      | —            | Todo   |
| TASK_D2 | Identify GSE submission API requirements for Fannie Mae / Freddie Mac | Low      | —            | Todo   |
| TASK_D3 | Map appraisal data friction points to Ontology Engine architecture    | Low      | TASK_D1      | Todo   |

**Acceptance Criteria:** UAD 3.6 schema fully documented. GSE submission requirements documented. Architecture adaptation plan drafted.

---

## 5. Hardcoded Constraints

These are **non-negotiable rules** that must be enforced in the system. They cannot be overridden by configuration.

| ID        | Name                                | Severity    | Description                                                                                                                         | Mitigation                                                                                     |
| --------- | ----------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| CONST_001 | **PII Redaction**                   | 🔴 Critical | All PII (names, addresses, SSNs, policy numbers) must be masked by local Python script BEFORE any data reaches the LLM.             | Microsoft Presidio runs as first step in Node 1. Zero-data-retention policy for LLM API calls. |
| CONST_002 | **Tax & O&P Double-Dip Prevention** | 🔴 Critical | Xactimate includes O&P margins. CRMs apply their own O&P. Node 3 must strip O&P before CRM injection.                               | Node 3 explicitly strips O&P line items and recalculates material-only costs.                  |
| CONST_003 | **Negative Quantity Handling**      | 🟠 High     | Negative integers in Xactimate supplements represent credits/deductions. Must be flagged as `credit_return`, not treated as errors. | Node 3 detects negative quantities and routes them to a `credit_return` data path.             |
| CONST_004 | **F9 Note Collision**               | 🟠 High     | Xactimate F9 notes can override standard line item values. LLM must flag these but NEVER auto-resolve.                              | Node 2 flags F9 collisions → HITL gate requires manual approval.                               |
| CONST_005 | **Human-in-the-Loop Gate**          | 🟠 High     | Any output with confidence below threshold or F9 conflicts must be held for human review.                                           | HITL queue with notification. User approves/rejects/edits before data proceeds to Node 4.      |

---

## 6. Risk Register

| ID       | Risk                                      | Severity    | Description                                                                                                           | Mitigation Strategy                                                                                                        | Status |
| -------- | ----------------------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------ |
| RISK_001 | **PII & Data Privacy Liability**          | 🔴 Critical | Processing insurance/appraisal docs may expose PII regulated by HIPAA, state privacy laws, and insurance regulations. | Local PII redaction before LLM. Zero-data-retention agreements. Legal review of data handling.                             | Open   |
| RISK_002 | **API Paywall Trap**                      | 🟠 High     | CRM API access may require Premium/Enterprise subscription tiers. Contractors on lower tiers may not have API access. | Audit all target CRM tiers for API availability. Fall back to CSV import where API unavailable.                            | Open   |
| RISK_003 | **Context Window / Token Limit Drop-off** | 🟠 High     | Large Xactimate PDFs may exceed LLM context windows, causing information loss.                                        | Token chunking strategy with overlap windows. Cost analysis for multi-call processing. Document segmentation by trade.     | Open   |
| RISK_004 | **OCR Volatility**                        | 🟡 Medium   | Scanned vs native PDFs produce vastly different text quality.                                                         | PDF type detection → native uses direct extraction, scanned routes through Tesseract/Textract with confidence scoring.     | Open   |
| RISK_005 | **Multi-Trade Routing Collision**         | 🟡 Medium   | A single estimate may contain multiple trades (roofing, siding, gutters) destined for different suppliers.            | Xactimate category codes segment by trade. Node 2 extracts trade tags. Node 3 splits by trade for separate Node 4 routing. | Open   |

---

## 7. Success Metrics

| #   | Metric                                   | Target                                          |
| --- | ---------------------------------------- | ----------------------------------------------- |
| 1   | Xactimate PDF → CRM-ready output         | < 60 seconds                                    |
| 2   | Extraction accuracy on structured fields | ≥ 95%                                           |
| 3   | PII leakage to LLM                       | **Zero**                                        |
| 4   | Successful CRM import/push               | ≥ 2 of 3 target CRMs                            |
| 5   | Contractor time savings                  | From 30–60 min manual entry → < 2 min automated |

---

## 8. Key Entities & Tools

| Entity                 | Type       | Role                                                                              |
| ---------------------- | ---------- | --------------------------------------------------------------------------------- |
| **Xactimate**          | Tool       | Insurance estimation software — the primary data source                           |
| **JobNimbus**          | CRM        | Primary Phase 1 target. REST API + QBO bridge. Strict deduplication.              |
| **AccuLynx**           | CRM        | Phase 1 target. OAuth 2.0 REST API V2. Partner access needed for Material Orders. |
| **Buildertrend**       | CRM        | Phase 1 target. CSV-based assembly imports.                                       |
| **QuickBooks Online**  | Accounting | Intermediary bridge for JobNimbus product/service imports                         |
| **Microsoft Presidio** | PII Tool   | Open-source PII detection and anonymization framework                             |
| **Tesseract**          | OCR        | Open-source OCR engine for scanned PDFs                                           |
| **AWS Textract**       | OCR        | Cloud-based OCR/document analysis service                                         |
| **ABC Supply**         | Supplier   | National roofing supplier with AccuLynx native integration                        |
| **SRS Distribution**   | Supplier   | National roofing supplier with AccuLynx integration via Roof Hub                  |

---

## 9. Source Document Traceability

This PRD was synthesized from 6 R&D documents. Every requirement, constraint, and finding traces back to its source.

| Doc ID  | Title                                         | Type             | Path                                                                          |
| ------- | --------------------------------------------- | ---------------- | ----------------------------------------------------------------------------- |
| DOC_001 | Ontology Thinking Mode                        | Framework        | `R&D-Unsynthesized/markdown/gemchat-Ontology Thinking Mode.md`                |
| DOC_002 | Z → A Pipeline Research & Blueprint           | Framework        | `R&D-Unsynthesized/markdown/Z → A Pipeline Research & Blueprint.md`           |
| DOC_003 | PRD - ScopeBridge                             | PRD (Incomplete) | `R&D-Unsynthesized/markdown/PRD - ScopeBridge.md`                             |
| DOC_004 | Roofing CRM & Xactimate Integration Blueprint | Blueprint        | `R&D-Unsynthesized/markdown/Roofing CRM & Xactimate Integration Blueprint.md` |
| DOC_005 | Data Friction Matrix Generation               | Research         | `R&D-Unsynthesized/markdown/Data Friction Matrix Generation.md`               |
| DOC_006 | GOAS Data Friction Matrix Generation          | Research         | `R&D-Unsynthesized/markdown/GOAS Data Friction Matrix Generation.md`          |

---

## 10. Appendix: Ontology Concept Graph

The full concept graph (18 nodes, 18 edges) is available in `ontology_kb.json` under the `ontology` layer. Key relationships:

```
GOAS ──instantiated_by──▶ Z → A Pipeline ──structures──▶ 4-Node Pipeline
                                                              │
                                              ┌───────────────┼───────────────┐
                                              ▼               ▼               ▼
                                          Ingestion     Extraction      Calculus      Routing
                                          (Node 1)      (Node 2)       (Node 3)      (Node 4)
                                              │               │               │
                                          PII Redaction   Lexicon        Roofer Math
                                          constrains     Matrix         implements
                                                         enables        O&P Prevention
                                                                        constrains

Data Friction Matrix ──identifies_opportunity_for──▶ AI/Code Arbitrage ──implemented_as──▶ Ontology Engine
                                                                                              │
                                                                                          eliminates
                                                                                              │
                                                                                          Human API
```

---

_This document is designed for **agent consumption**. Each section maps directly to a layer in `ontology_kb.json`. Agents working on specific workstreams only need relevant sections — not the full corpus._
