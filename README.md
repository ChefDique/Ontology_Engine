# Ontology Engine

> **Universal Analog-to-Digital Translation Middleware**
> Converts unstructured proprietary documents (PDFs, scans) into structured, system-ready data — eliminating the "Human API" bottleneck where skilled professionals manually re-key data between incompatible systems.

---

## The Problem

Insurance restoration contractors receive Xactimate estimates as PDFs and spend **45–90 minutes per claim** manually re-entering line items into their CRM. At $35–60/hour, this costs **$1,050–$3,600/month** per office, introduces **2–15% error rates**, and doesn't scale.

Xactimate holds **85–90% market share** in property insurance estimating. The data is structured inside the system but delivered as unstructured PDFs — creating a universal data-entry bottleneck across the entire restoration industry.

## The Solution

A **6-node agentic pipeline** that separates semantic extraction (LLMs) from deterministic calculation (Python), enforced by Design by Contract at every node boundary:

```
                        ┌──── Adjuster PDF ────┐
                        │                      │
                        ▼                      ▼
                  ┌──────────┐           ┌──────────┐
                  │ Node 1   │           │ Node 1   │
                  │ Ingest   │           │ Ingest   │
                  └────┬─────┘           └────┬─────┘
                       │                      │
                  ┌────▼─────┐           ┌────▼─────┐
                  │ Node 2   │           │ Node 2   │
                  │ Extract  │           │ Extract  │
                  └────┬─────┘           └────┬─────┘
                       │                      │
                  ┌────▼─────┐           ┌────▼─────┐
                  │ Node 3   │           │ Node 3   │
                  │ Calculus │           │ Calculus  │
                  └────┬─────┘           └────┬─────┘
                       │                      │
                       └──────────┬───────────┘
                                  │
                           ┌──────▼──────┐
                           │   Node 5    │
                           │ Comparator  │
                           └──────┬──────┘
                                  │
                           ┌──────▼──────┐
                           │   Node 6    │
                           │ Supplement  │
                           │   Report    │
                           └─────────────┘
```

**Node 4 (Output Routing)** operates independently for single-estimate workflows, formatting Node 3 output for CRM import (CSV/JSON/API).

---

## Architecture

| Node                                | Responsibility                                                         | Key Invariant               |
| ----------------------------------- | ---------------------------------------------------------------------- | --------------------------- |
| **Node 1 — Ingestion**              | OCR routing (native vs scanned PDF) + PII redaction                    | Zero PII in output          |
| **Node 2 — Semantic Extraction**    | LLM maps Xactimate codes → structured JSON via Lexicon Matrix          | LLM never does math         |
| **Node 3 — Deterministic Calculus** | Python computes physical quantities, strips O&P, rounds UP             | No float errors in currency |
| **Node 4 — Output Routing**         | Formats for target CRM (Buildertrend CSV, JobNimbus QBO, AccuLynx API) | End-to-end data integrity   |
| **Node 5 — Estimate Comparator**    | Compares adjuster vs contractor estimates, detects line-item gaps      | All deltas accounted        |
| **Node 6 — Supplement Report**      | Generates human-readable supplement narrative from gap data            | Dollar amounts verified     |

### Design Principles

- **Z → A Reverse Extrapolation (GOAS):** Define the final output schema first, work backward to raw input. Every node boundary enforces pre/postconditions via JSON schema.
- **LLMs never calculate:** Node 2 extracts raw values (strings + numbers) only. All math happens in Node 3 using deterministic Python.
- **PII redaction is mandatory:** Zero PII reaches any LLM (CONST_001).
- **O&P stripping is mandatory:** Before any CRM injection to prevent double-dipping (CONST_002).

---

## Tech Stack

| Layer               | Technology                                  | Purpose                                   |
| ------------------- | ------------------------------------------- | ----------------------------------------- |
| **Backend API**     | FastAPI + Uvicorn                           | REST API server                           |
| **LLM Integration** | Google Gemini (primary), OpenAI, Anthropic  | Semantic extraction                       |
| **OCR**             | pdfplumber (native) + pytesseract (scanned) | PDF text extraction                       |
| **PII**             | Presidio Analyzer + Anonymizer              | PII detection & redaction                 |
| **Math**            | NumPy + custom roofer math                  | Deterministic calculations                |
| **Auth & Storage**  | Supabase (JWT auth, PostgreSQL, Storage)    | User auth, data persistence, file storage |
| **Frontend**        | Vanilla JS + Vite                           | Single-page app                           |
| **Validation**      | JSON Schema + Pydantic                      | Contract enforcement                      |

---

## Project Structure

```
ontology-engine/
├── src/ontology_engine/
│   ├── api.py                 # FastAPI server (endpoints + security)
│   ├── pipeline.py            # Pipeline orchestrator
│   ├── config.py              # Environment + settings
│   ├── supabase_client.py     # Supabase client initialization
│   ├── contracts/             # JSON Schema contracts per node boundary
│   ├── node1_ingestion/       # OCR routing + PII redaction
│   ├── node2_extraction/      # LLM semantic extraction
│   ├── node3_calculus/        # Deterministic roofer math
│   ├── node4_output/          # CRM output adapters
│   ├── node5_comparator/      # Estimate gap detection
│   ├── node6_supplement/      # Supplement report generator
│   └── hitl/                  # Human-in-the-Loop review gate
├── web/                       # Vite frontend
│   └── src/
│       ├── main.js            # App shell + auth gate
│       ├── components/        # View components (upload, pipeline, report, review, login)
│       ├── styles/            # Design system CSS
│       └── utils/             # State management, Supabase client
├── tests/                     # pytest test suite
│   ├── test_node1_ingestion/  # Node-specific tests
│   ├── test_node2_extraction/
│   ├── test_node3_calculus/
│   ├── test_node4_output/
│   ├── test_node5_comparator/
│   ├── test_node6_supplement/
│   ├── test_pipeline/
│   ├── test_api/
│   ├── test_contracts/
│   ├── test_hitl/
│   └── red_team/              # Adversarial test suite
├── docs/                      # Documentation
│   ├── adr/                   # Architecture Decision Records
│   ├── briefings/             # Agent workstream briefings
│   ├── schemas/               # Schema documentation
│   └── research/              # R&D notes
├── ontology_kb.json           # Knowledge Base (7 layers, machine-readable)
├── PRD_Ontology_Engine_Complete.md  # Full product requirements
├── Procfile                   # Heroku/Railway deployment
└── pyproject.toml             # Python project config + dependencies
```

---

## API Endpoints

| Method | Path                | Auth | Description                                           |
| ------ | ------------------- | ---- | ----------------------------------------------------- |
| `POST` | `/api/analyze`      | JWT  | Upload two Xactimate PDFs → supplement report         |
| `GET`  | `/api/history`      | JWT  | List past analyses for authenticated user             |
| `GET`  | `/api/history/{id}` | JWT  | Retrieve full analysis detail by ID                   |
| `GET`  | `/health`           | None | Health check with circuit breaker & rate limit status |

### Security Features

- **Supabase JWT authentication** on all `/api/*` endpoints
- **IP-based rate limiting** (configurable daily limits per IP)
- **Concurrent request semaphore** (default: 3 simultaneous requests)
- **Global daily budget** (default: 500 requests/day)
- **Circuit breaker** (trips after 5 consecutive failures, 5-min cooldown)
- **File validation** (PDF-only, 20MB max, content-type checks)
- **API kill switch** (`API_ENABLED=false` disables all endpoints)
- **CORS** (configurable allowed origins)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Tesseract OCR (`brew install tesseract` on macOS)
- A Google Gemini API key (for LLM extraction)

### Backend Setup

```bash
# Clone and enter project
git clone <repo-url>
cd Ontology_Engine

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
#   GEMINI_API_KEY=your_key_here
#   SUPABASE_URL=your_project_url
#   SUPABASE_ANON_KEY=your_anon_key
#   SUPABASE_SERVICE_KEY=your_service_key

# Run tests
pytest tests/ -v

# Start API server
uvicorn ontology_engine.api:app --reload --port 8000
```

### Frontend Setup

```bash
cd web
npm install
npx vite --host 0.0.0.0 --port 5173
```

Visit `http://localhost:5173` to access the UI.

### Deployment

The app includes a `Procfile` for deployment on platforms like Heroku or Railway:

```
web: uvicorn ontology_engine.api:app --host 0.0.0.0 --port ${PORT:-8000}
```

### Environment Variables

| Variable                    | Required | Default | Description                                 |
| --------------------------- | -------- | ------- | ------------------------------------------- |
| `GEMINI_API_KEY`            | Yes      | —       | Google Gemini API key for Node 2 extraction |
| `SUPABASE_URL`              | Yes\*    | —       | Supabase project URL                        |
| `SUPABASE_ANON_KEY`         | Yes\*    | —       | Supabase anonymous/public key               |
| `SUPABASE_SERVICE_KEY`      | Yes\*    | —       | Supabase service role key                   |
| `API_ENABLED`               | No       | `true`  | Kill switch to disable all endpoints        |
| `PORT`                      | No       | `8000`  | API server port                             |
| `CORS_ORIGINS`              | No       | `*`     | Comma-separated allowed origins             |
| `RATE_LIMIT_PER_IP_DAILY`   | No       | `50`    | Max requests per IP per day                 |
| `MAX_CONCURRENT_REQUESTS`   | No       | `3`     | Concurrent request limit                    |
| `GLOBAL_DAILY_BUDGET`       | No       | `500`   | Total requests allowed per day              |
| `CIRCUIT_BREAKER_THRESHOLD` | No       | `5`     | Failures before circuit trips               |
| `MAX_FILE_SIZE_MB`          | No       | `20`    | Maximum upload file size                    |

\*Required when Supabase auth is enabled. Without these, the API runs in open/dev mode.

---

## System Constraints

| ID        | Name                        | Severity | Summary                                                      |
| --------- | --------------------------- | -------- | ------------------------------------------------------------ |
| CONST_001 | PII Redaction               | Critical | All PII masked before LLM contact                            |
| CONST_002 | O&P Double-Dip Prevention   | Critical | Node 3 strips O&P before CRM injection                       |
| CONST_003 | Negative Quantity Handling  | High     | Credits/deductions flagged, never silently dropped           |
| CONST_004 | F9 Note Collision           | High     | LLM must flag adjuster overrides for HITL review             |
| CONST_005 | HITL Gate                   | High     | Low-confidence outputs held for human review                 |
| CONST_006 | PDF-First Ingestion         | Critical | MVP uses PDF/OCR only (ESX/XML deferred pending EULA)        |
| CONST_007 | User-Origin Enforcement     | High     | Files must be user-exported from their own Xactimate license |
| CONST_008 | No Format Spec Distribution | High     | Never publish reverse-engineered format specs                |

---

## Target Markets

| Phase       | Market                                                  | Status           |
| ----------- | ------------------------------------------------------- | ---------------- |
| **Phase 1** | Roofing Contractors (Xactimate → CRM)                   | **Active** — MVP |
| **Phase 2** | Real Estate Appraisers (Field Data → UAD 3.6 MISMO XML) | R&D              |
| Future      | Custom Cabinetry, Legal Discovery, CRE, Logistics       | Research         |

---

## Development

### Running Tests

```bash
source .venv/bin/activate

# Full test suite
pytest tests/ -v

# Node-specific tests
pytest tests/test_node3_calculus/ -v

# Red team adversarial tests
pytest tests/red_team/ -v

# Lint
python -m ruff check src/
```

### Agent Onboarding

This project uses a multi-agent orchestration system. If you're an AI agent, read:

1. Your **briefing file** at `docs/briefings/<workstream>_briefing.md`
2. The **contracts** at `src/ontology_engine/contracts/schemas.py`
3. The **project rules** at `.agents/rules/project-rules.md`

### Key Documents

| Document                                   | Purpose                                              |
| ------------------------------------------ | ---------------------------------------------------- |
| `ontology_kb.json`                         | Knowledge Base (7 layers, canonical source of truth) |
| `PRD_Ontology_Engine_Complete.md`          | Full product requirements document                   |
| `docs/adr/`                                | Architecture Decision Records                        |
| `docs/briefings/`                          | Scoped agent briefing files                          |
| `src/ontology_engine/contracts/schemas.py` | Inter-node data contracts                            |

---

## Methodology

**Z → A Reverse Extrapolation (GOAS):** Define the final output (Z) first, then reverse-engineer every intermediate step back to raw input (A). This ensures every node exists to serve a verified output requirement — no speculative features, no dead code paths.

## License

Proprietary — All rights reserved.
