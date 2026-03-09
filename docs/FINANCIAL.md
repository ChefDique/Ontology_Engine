# Ontology Engine — Financial Analysis

> Last updated: 2026-03-09

---

## Cost Structure

### Current Operating Costs

| Item                     | Cost                      | Notes                                                    |
| ------------------------ | ------------------------- | -------------------------------------------------------- |
| **Gemini Flash API**     | ~$0.01–$0.05 per analysis | 2 PDF extractions per supplement (adjuster + contractor) |
| **Supabase (Free Tier)** | $0/mo                     | 500MB DB, 1GB storage, 50K auth users                    |
| **Hosting (API)**        | $0–$7/mo                  | Railway/Render free tier → $7/mo at scale                |
| **Hosting (Frontend)**   | $0/mo                     | Vercel free tier (static site)                           |
| **Tesseract OCR**        | $0                        | Open source, runs locally                                |
| **Domain**               | ~$12/year                 | Optional for MVP                                         |

### Per-Analysis Cost Breakdown

```
Single Supplement Analysis:
  ├── Gemini Flash API (2 extractions)     $0.02–$0.05
  ├── Supabase DB write                    $0.00   (free tier)
  ├── Supabase Storage (2 PDFs, ~2MB)      $0.00   (free tier)
  └── Server compute                       $0.001  (fractional)
  ─────────────────────────────────────────
  Total cost per analysis:                 ~$0.03–$0.06
```

### Monthly Cost at Scale

| Active Users | Analyses/Month | LLM Cost  | Infrastructure     | Total            |
| ------------ | -------------- | --------- | ------------------ | ---------------- |
| 10           | 200            | $6–$10    | $0 (free tiers)    | **$6–$10/mo**    |
| 50           | 1,000          | $30–$50   | $7 (Render basic)  | **$37–$57/mo**   |
| 200          | 5,000          | $150–$250 | $25 (Supabase Pro) | **$175–$275/mo** |
| 500          | 15,000         | $450–$750 | $50 (scaled infra) | **$500–$800/mo** |

---

## Revenue Model

### Pricing Strategy: Tiered SaaS

| Tier             | Price   | Analyses/Month | Target Segment                          |
| ---------------- | ------- | -------------- | --------------------------------------- |
| **Free**         | $0/mo   | 5              | Trial / evaluation                      |
| **Starter**      | $29/mo  | 50             | Solo contractors                        |
| **Professional** | $79/mo  | 200            | Small restoration companies (2–5 users) |
| **Enterprise**   | $199/mo | Unlimited      | Multi-office operations                 |

### Unit Economics

| Metric                                | Value                      |
| ------------------------------------- | -------------------------- |
| **Cost per analysis**                 | $0.03–$0.06                |
| **Starter revenue per analysis**      | $0.58 (=$29/50)            |
| **Gross margin (Starter)**            | **~90–95%**                |
| **Professional revenue per analysis** | $0.40 (=$79/200)           |
| **Gross margin (Professional)**       | **~85–92%**                |
| **Break-even**                        | ~7 paying users on Starter |

### Value Proposition — Contractor ROI

```
Manual Process (Status Quo):
  ├── Time per supplement analysis:     45–90 min
  ├── Labor cost ($35–60/hr):           $26–$90 per analysis
  ├── Error rate:                       2–15%
  └── Re-work from errors:             15–30 min additional

With Ontology Engine:
  ├── Time per supplement analysis:     < 2 min
  ├── Subscription cost:                $0.58–$1.59 per analysis
  ├── Error rate:                       < 1% (with HITL)
  └── Monthly savings:                  $1,050–$3,600

ROI for Starter plan ($29/mo):
  Savings:  $1,050–$3,600/mo
  Cost:     $29/mo
  ROI:      36x – 124x return
```

---

## Monetization Roadmap

### Phase 1 — MVP Revenue (Current)

**Model:** Per-seat SaaS subscription (tiered)

- Charge per user/month with analysis quotas
- Free tier for trial (5 analyses)
- Primary revenue from Professional tier ($79/mo)
- No per-analysis metering — simple flat pricing builds trust

### Phase 2 — Value-Add Revenue Streams

| Stream                      | Description                                    | Estimated Revenue |
| --------------------------- | ---------------------------------------------- | ----------------- |
| **CRM Integration Premium** | Direct push to Buildertrend/JobNimbus/AccuLynx | +$20/mo add-on    |
| **Batch Processing**        | Upload 10+ estimate pairs at once              | +$30/mo add-on    |
| **Custom Lexicon**          | Per-contractor Xactimate code overrides        | +$15/mo add-on    |
| **White Label**             | Brandable interface for franchise operations   | Custom pricing    |

### Phase 3 — Platform Revenue

| Stream               | Description                            | Estimated Revenue              |
| -------------------- | -------------------------------------- | ------------------------------ |
| **UAD 3.6 Vertical** | Real estate appraisal → MISMO XML      | Separate product line          |
| **API-Only Access**  | Headless pipeline for integrators      | Usage-based ($0.10–$0.50/call) |
| **Data Insights**    | Anonymized market pricing intelligence | Enterprise add-on              |

---

## Competitive Pricing Analysis

| Competitor/Alternative    | Pricing                     | Limitations                                |
| ------------------------- | --------------------------- | ------------------------------------------ |
| **Manual re-entry**       | $26–$90/analysis (labor)    | Slow, error-prone, doesn't scale           |
| **Virtual assistants**    | $15–$25/hr ($500–$1,000/mo) | Still manual, quality varies               |
| **Custom dev automation** | $20K–$50K upfront           | Maintenance burden, single-CRM lock-in     |
| **Ontology Engine**       | $29–$199/mo                 | Automated, multi-CRM, < 2 min per analysis |

---

## Investment Requirements

### To reach Shareable MVP

| Item                                           | Investment              | Timeline      |
| ---------------------------------------------- | ----------------------- | ------------- |
| Frontend wiring (workstream November)          | Development time        | 1–2 days      |
| Deployment + access control (workstream Oscar) | $7–25/mo infrastructure | 1–2 days      |
| Beta testing with 5–10 contractors             | Time + support          | 2–4 weeks     |
| **Total to MVP**                               | **~$25–50/mo + labor**  | **1–2 weeks** |

### To reach Revenue ($1K MRR milestone)

| Item                                                          | Investment                        | Timeline       |
| ------------------------------------------------------------- | --------------------------------- | -------------- |
| MVP deployment (above)                                        | $25–50/mo                         | 1–2 weeks      |
| Payment integration (Stripe)                                  | Development time                  | 3–5 days       |
| Landing page + onboarding flow                                | Development time                  | 2–3 days       |
| Sales outreach to contractors                                 | Time investment                   | 2–4 weeks      |
| Need: **15 Starter ($29)** or **13 Professional ($79)** users | —                                 | —              |
| **Total to $1K MRR**                                          | **~$50–100/mo + 4–6 weeks labor** | **1–2 months** |

---

## Key Financial Risks

1. **LLM cost spikes**: Gemini Flash pricing changes could impact margins (mitigated by low current costs and ability to switch providers)
2. **Supabase tier upgrade**: Free tier limits (500MB DB) will be hit around 500–1,000 active analyses with file storage
3. **Support costs**: Contractor users may need hands-on onboarding and PDF troubleshooting time
4. **CRM API access**: AccuLynx API may require partnership agreements for production access
5. **Legal**: ESX/XML direct parsing remains blocked pending EULA review; PDF-only approach has lower accuracy ceiling on complex documents
