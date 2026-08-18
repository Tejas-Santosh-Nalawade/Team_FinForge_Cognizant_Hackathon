# FinForge — Enterprise FP&A & Financial Audit Assurance Suite

> **Cognizant NPN • Enterprise FP&A & Audit Assurance Architecture (ARCH-SPEC-WP514 v3)**  
> **Domain:** Banking & Financial Services  
> **Framework:** US GAAP / IFRS / Bank Directives  
> **Target Entity:** Apex Global Technologies Inc.

---

## 🌟 Executive System Overview

**FinForge** is an enterprise-grade Financial Statement Audit, Continuous Assurance, and Dynamic FP&A Intelligence Platform. It bridges deterministic accounting verification with AI-powered RAG policy governance and multi-modal deliverable generation.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                1. INGESTION & PARSING                                  │
│  • Historical & Draft Financial Statements (BS, IS, CF, Equity)                        │
│  • General Ledger & Trial Balances (Preliminary & Final TB)                            │
│  • Footnote Disclosures & Schedules (AR Aging, PP&E, Debt Maturity)                    │
│  • Cloudflare R2 Object Storage Vault (`s3.r2.cloudflarestorage.com`)                  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   2. NORMALIZATION & SPELLING GRAMMAR CHECK                            │
│  • Canonical Chart of Accounts (CoA) Standardization & Multi-Entity Consolidation      │
│  • Automated Financial Spell & Grammar Audit Engine (Terminology & Quality Filtering)  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          3. DUAL-TRACK COMPUTATION ENGINES                             │
│  ┌───────────────────────────────────────────┐ ┌─────────────────────────────────────┐  │
│  │ Track A: Deterministic Audit & Close      │ │ Track B: Predictive & FP&A          │  │
│  │ • 56 Deterministic Math & Tie-Out Rules   │ │ • Statistical & ML Forecasts        │  │
│  │ • 11 Financial Ratios & Benchmarks        │ │ • Rolling Projections (4Q/8Q)       │  │
│  │ • 6 Relationship Disconnect Triggers      │ │ • Scenario & Stress Models          │  │
│  │ • 16 Input Sanity Guardrails              │ │ • Working Capital / Cash Runway     │  │
│  └─────────────────────┬─────────────────────┘ └──────────────────┬──────────────────┘  │
│                        │                                          │                     │
│                        └────────────────────┬─────────────────────┘                     │
└─────────────────────────────────────────────┼───────────────────────────────────────────┘
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                 4. INTELLIGENCE, SYNTHESIS & ADVISORY LAYER (RAG + AI)                 │
│  • Gap Identification: BvA Variance Gaps, Disclosure Compliance, Structural Disconnects│
│  • Predictive Modeling: Next-Period Trajectories, Cash Depletion, Covenant Headroom    │
│  • Prescriptive Advisory: Qdrant Vector Search (US GAAP ASC Topics / IFRS Standards)   │
│  • Executive Narrative Synthesis: Google AI Studio Gemini API Management Briefings     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              5. MULTI-MODAL OUTPUT LAYER                               │
│  • Enriched Structured JSON Payload (Procedures, Findings, Gaps, Predictions, Actions) │
│  • WP-514 Working Paper Set (PDF) via ReportLab `NumberedCanvas`                       │
│  • Reconciled Financial Model (.xlsx) via `openpyxl` with AJE Adjusting Entries        │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                    6. INTERACTIVE FP&A & AUDIT INTELLIGENCE DASHBOARD                  │
│  • Executive Dark Mode Command Dashboard (#0B1120 / #0F172A / #1E293B)                 │
│  • Real-Time Executive KPI & Liquidity Banner (Cash Runway, Quick & Current Ratios)    │
│  • Dynamic BvA & Variance Heatmap (Income Statement / Balance Sheet / Cash Flow)       │
│  • Interactive Discrepancy & Waiver Resolution Console (Accept AJE vs Waive)           │
│  • Persistent High-Risk Audit Banner across all UI views & exported documents          │
│  • What-If Scenario Simulator (Sales, Pricing, Interest, Cost Driver Sliders)          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Tailwind CSS v4, Lucide Icons, Recharts, Zustand |
| **Theme** | Executive Deep Dark Mode (`#0B1120` canvas, `#0F172A` cards, `#1E293B` borders) |
| **Backend API** | FastAPI (Python 3.11+), Pydantic v2 schemas, Uvicorn |
| **Database** | SQLAlchemy ORM (SQLite for local dev, PostgreSQL for production) |
| **AI / RAG** | Google AI Studio Gemini API (`gemini-1.5-pro`) + Qdrant Vector Search |
| **Object Store** | Cloudflare R2 (`boto3` S3-compatible client) + Local Vault Fallback |
| **Workbooks & PDF**| `openpyxl` (Adjusted Trial Balances) + ReportLab (`NumberedCanvas` 2-Pass PDF) |

---

## 🚀 Quick Start Guide

### 1. Backend Server Setup
```bash
# Navigate to backend directory
cd backend

# Run FastAPI backend with Uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*API Documentation will be live at: `http://localhost:8000/docs`*

### 2. Frontend Dashboard Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Vite development server
npm run dev
```
*Frontend UI will be live at: `http://localhost:5173`*

### 3. Run Backend Integration Test Suite
```bash
python -m pytest tests/ -v
```

---

## 🌐 Endpoints Specification (FastAPI)

1. `POST /api/v1/ingest/upload` — Ingest financial workbooks (.xlsx/.json), upload to R2, normalize via Canonical CoA, execute 56-rule audit gate.
2. `POST /api/v1/audit/resolve-discrepancies` — Interactive decision workflow (Accept AJE vs Waive) with persistent high-risk warning banner state.
3. `POST /api/v1/rag/explain-finding` — Query Qdrant vector store for ASC/IFRS standards + synthesize root-cause with Gemini.
4. `POST /api/v1/simulator/stress-test` — Driver sliders (volume, pricing, cost, interest) driving real-time 12-month cash burn curve.
5. `POST /api/v1/reports/build-deliverables` — Compile formal WP-514 PDF, Reconciled Excel workbook, and JSON payload to R2.
6. `GET /api/v1/audit/engagements` — List historical audit engagements and compliance metrics.

---

## 🛡️ License & Compliance
Confidential & Proprietary • Cognizant Hackathon • Team FinForge • WP-514 Compliance Certified.
