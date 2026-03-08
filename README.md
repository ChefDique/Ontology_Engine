# Ontology Engine

> **Universal Analog-to-Digital Translation Middleware**
> Automates the extraction of unstructured data (PDFs, scans) into structured, system-ready formats (CSV, JSON, API payloads).

---

## The Problem

Skilled professionals act as **"Human APIs"** — manually translating data between incompatible systems. A roofing contractor gets an Xactimate estimate (PDF) and spends 45–90 minutes re-typing it into their CRM. This costs $1,050–$3,600/month, introduces 2–15% error rates, and doesn't scale.

## The Solution

A **4-node agentic pipeline** that separates semantic extraction (LLMs) from deterministic calculation (Python), enforced by Design by Contract at every boundary:

```
PDF/Scan ──▶ [Node 1: Ingestion] ──▶ [Node 2: Extraction] ──▶ [Node 3: Calculus] ──▶ [Node 4: Output]
              OCR + PII Redaction     LLM → Structured JSON    Roofer Math (Python)   CSV / REST API
```

## Architecture

| Node                                | Responsibility                                                         | Key Invariant               |
| ----------------------------------- | ---------------------------------------------------------------------- | --------------------------- |
| **Node 1 — Ingestion**              | OCR routing (native vs scanned PDF) + PII redaction                    | Zero PII in output          |
| **Node 2 — Semantic Extraction**    | LLM maps Xactimate codes → structured JSON via Lexicon Matrix          | LLM never does math         |
| **Node 3 — Deterministic Calculus** | Python computes physical quantities, strips O&P, rounds UP             | No float errors in currency |
| **Node 4 — Output Routing**         | Formats for target CRM (Buildertrend CSV, JobNimbus QBO, AccuLynx API) | End-to-end data integrity   |

## Project Structure

```
src/ontology_engine/
├── node1_ingestion/      # Workstream Alpha: OCR + PII
├── node2_extraction/     # Workstream Beta: LLM extraction
├── node3_calculus/       # Workstream Beta: Roofer Math
├── node4_output/         # Workstream Gamma: CRM adapters
├── contracts/            # Design by Contract: JSON schema enforcement
├── hitl/                 # Human-in-the-Loop review gate
├── config.py             # Environment + settings
└── pipeline.py           # Orchestrator
```

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Copy env template
cp .env.example .env
# Add your LLM API keys to .env

# Run tests
pytest tests/ -v
```

## Key Documents

| Document                                                     | Purpose                                               |
| ------------------------------------------------------------ | ----------------------------------------------------- |
| [`ontology_kb.json`](ontology_kb.json)                       | Canonical knowledge base (6 layers, machine-readable) |
| [`PRD_ScopeBridge_Complete.md`](PRD_ScopeBridge_Complete.md) | Full product requirements document                    |
| [`docs/architecture.md`](docs/architecture.md)               | System architecture deep-dive                         |
| [`docs/constraints.md`](docs/constraints.md)                 | 5 non-negotiable system rules                         |
| [`docs/briefings/`](docs/briefings/)                         | Scoped agent briefing files per workstream            |

## Agent Onboarding

If you're an AI agent assigned to a workstream, read **only** your briefing file:

```
docs/briefings/alpha_briefing.md   → Node 1 (OCR + PII)
docs/briefings/beta_briefing.md    → Nodes 2+3 (Extraction + Calculus)
docs/briefings/gamma_briefing.md   → Node 4 (CRM Adapters)
docs/briefings/delta_briefing.md   → Phase 2 R&D (UAD 3.6)
```

Then read `src/ontology_engine/contracts/schemas.py` for inter-node data contracts.

## Methodology

**Z → A Reverse Extrapolation (GOAS):** Define the final output (Z) first, work backward to raw input (A). Every node boundary enforces preconditions and postconditions via JSON schema validation.

## Target Markets

| Phase       | Market                                                  | Status   |
| ----------- | ------------------------------------------------------- | -------- |
| **Phase 1** | Roofing Contractors (Xactimate → CRM)                   | Active   |
| **Phase 2** | Real Estate Appraisers (Field Data → UAD 3.6 MISMO XML) | R&D      |
| Future      | Custom Cabinetry, Legal Discovery, CRE, Logistics       | Research |

## License

Proprietary — All rights reserved.
