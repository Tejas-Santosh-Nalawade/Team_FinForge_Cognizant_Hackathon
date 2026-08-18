# Fin - Enterprise Financial Statement Audit & Analytics Engine

A Python-based enterprise financial engine executing a multi-stage audit and analytics pipeline adhering to **Cognizant NPN • FP&A & Financial Analytics Engineering Specification (SPEC-STAGE3-v1)**.

---

## 🏗️ Execution Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ INPUT: EXCEL DATASET                                                    │
│ • Primary Statements: Balance Sheet, Income Statement, Cash Flow, Equity│
│ • Footnote Schedules: AR Aging, PP&E Schedule, Debt Maturity           │
│ • Planning Inputs: Separate aob.xlsx & operational_drivers.xlsx files   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: DETERMINISTIC AUDIT GATE                                       │
│ • Runs 28 Deterministic Math & Cross-Statement Tie-Out Assertion Rules  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: MECHANICAL BREAK CHECK                                         │
│ • Checks if there are mechanical breaks (failed deterministic rules)     │
│ • If Mechanical Breaks -> Flag & Reject                                 │
│ • If No Mechanical Breaks (CLEARED) -> Proceed to Stage 3               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: FINANCIAL ANALYTICS & FP&A ENGINE (SPEC-STAGE3-v1)             │
│ 3A. Horizontal & Vertical Variance Engine (YoY Δ$, %Δ, BS/IS %, FLAG_01)│
│ 3B. Budget vs. Actual (BvA) Attainment Engine (Variances & Unit Ratios) │
│ 3C. Ratio & Disconnect Audit Engine (11 Ratios & 6 Disconnect Rules)    │
│ 3D. Dynamic Cash Runway & Working Capital Velocity (CCC & Burn Horizon) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ OUTPUT PAYLOAD & AUDIT REPORTS                                          │
│ • results.json (Complete Audit Payload & Analytics Matrix)              │
│ • result.pdf (Professional Multi-Page ReportLab PDF Audit Report)       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Fin/
├── Data/
│   ├── Error_data/              # Test dataset with injected accounting flaws, aob.xlsx, operational_drivers.xlsx
│   └── True_data/               # Clean audited dataset, aob.xlsx, operational_drivers.xlsx
├── data_generator/              # Modular Dataset Generation Package
│   ├── __init__.py              # Package exports
│   ├── data_generator.py        # 100% compliant baseline dataset generator
│   ├── error_data_generator.py  # Generator for datasets with randomized flaws
│   └── planning_generator.py    # Generator for separate aob.xlsx and operational_drivers.xlsx files
├── math_engine/                 # Core Audit & Analytics Python Package
│   ├── __init__.py              # Exposes MathEngine, schemas, loader, and PDF generator
│   ├── analytics.py             # Stage 3 Financial Analytics & FP&A Engine (Sub-Modules 3A, 3B, 3C, 3D)
│   ├── assertions.py            # 28 Deterministic Math & Cross-Statement Tie-Out Rules
│   ├── core.py                  # Core Engine Coordinator (Stage 1 -> Stage 2 -> Stage 3)
│   ├── guardrails.py            # Input Data Sanity & Validation Suite (16 Rules + AOB/Driver Guardrails)
│   ├── loader.py                # Excel Ingestion Loader
│   ├── pdf_reporter.py          # ReportLab PDF Audit Report Renderer
│   └── schemas.py               # Pydantic Data Models
├── result/                      # Output Directory for Audit & Analytics Results
│   ├── error_data/              # Latest & timestamped runs for Error_data
│   └── true_data/               # Latest & timestamped runs for True_data
├── templates/                   # JSON Schema Contracts
│   ├── 4q_schema.json
│   ├── 8q_schema.json
│   ├── aob_schema.json
│   └── operational_drivers_schema.json
├── tests/
│   └── test_math_engine.py      # Pytest suite for MathEngine & Stage 3 Analytics
├── pyproject.toml               # Pytest configuration
├── requirements.txt             # Dependencies
└── main.py                      # Main Execution CLI
```
