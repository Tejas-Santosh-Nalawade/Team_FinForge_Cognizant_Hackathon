# Fin - Enterprise Financial Statement Audit & Reconciliation Engine

A Python-based enterprise audit engine that ingests two-period financial statements, footnote schedules, and trial balances from Excel datasets, executes **56 automated audit procedures**, and generates structured **JSON** and multi-page **PDF** audit reports.

---

## 🏗️ Codebase Overview & Architecture

The **`Fin`** codebase is organized into modular packages:
- **`math_engine/`**: The core audit library containing ingestion loaders, Pydantic schemas, deterministic assertions, financial ratio benchmarking, input guardrails, and PDF generation.
- **`data_generator/`**: Utility scripts for generating clean baseline datasets (`data_generator.py`) and datasets with injected accounting flaws (`error_data_generator.py`).
- **`Data/`**: Consolidated directory containing `True_data` (clean audited dataset) and `Error_data` (flawed test dataset).
- **`result/`**: Result output folder containing latest and archived timestamped audit runs (`results.json` and `result.pdf`).
- **`main.py`**: CLI entry point supporting single, multi-dataset, and custom directory audit executions.

---

## 📁 Folder & File Structure

```
Fin/
├── Data/
│   ├── Error_data/              # Test dataset with 10 injected accounting flaws (19 audit findings)
│   └── True_data/               # Clean audited dataset (56/56 procedures passed, CLEARED status)
├── data_generator/
│   ├── data_generator.py        # Generator for clean 100% compliant financial datasets
│   └── error_data_generator.py  # Generator for financial datasets with randomized flaws
├── math_engine/                 # Core Python Package
│   ├── __init__.py              # Exposes MathEngine, schemas, loader, and PDF generator
│   ├── analytics.py             # YoY Variance Analysis & 11 Financial Ratio Benchmarks
│   ├── assertions.py            # 26 Deterministic Math & Cross-Statement Tie-Out Rules
│   ├── core.py                  # Core Engine Coordinator & Structured Audit Report Compiler
│   ├── guardrails.py            # Input Data Sanity & Validation Suite
│   ├── loader.py                # Excel File Ingestion & Schema Mapper
│   ├── pdf_reporter.py          # ReportLab Multi-Page PDF Audit Report Renderer
│   └── schemas.py               # Pydantic Data Models (Ingestion, Statements, Footnotes, Findings)
├── result/                      # Output Directory for Audit Results
│   ├── error_data/              # Latest results & timestamped historical runs for Error_data
│   │   ├── result.pdf
│   │   ├── results.json
│   │   └── history/
│   └── true_data/               # Latest results & timestamped historical runs for True_data
│       ├── result.pdf
│       ├── results.json
│       └── history/
├── templates/                   # JSON Schema Contracts
│   ├── Input ingestion template.json
│   └── Structured output report template.json
├── tests/
│   └── test_math_engine.py      # Pytest Suite (4/4 tests passing)
├── .gitignore                   # Ignores bytecodes, pytest cache, zip files
├── CODEBASE_OVERVIEW.md         # Comprehensive project documentation
├── main.py                      # Main Audit Execution CLI
├── pyproject.toml               # Pytest Pythonpath Configuration
└── requirements.txt             # Dependencies (pydantic, pandas, pytest, openpyxl, reportlab)
```

---

## ⚙️ How Everything Works End-to-End

### 1. Ingestion Stage (`math_engine/loader.py`)
When you execute `python main.py`, the engine loads the target directory (e.g., `Data/Error_data`, `Data/True_data`, or a custom `--data-dir` path).
- `loader.py` opens two-column Excel financial statements and multi-column trial balances using `openpyxl`.
- It maps financial line items into strongly-typed **Pydantic** schema models defined in `math_engine/schemas.py`.

### 2. Audit Execution Stage (`math_engine/core.py`)
The `MathEngine` class runs a 4-phase audit suite:
- **Input Guardrails (`guardrails.py`)**: Verifies asset non-negativity, reporting dates, scale consistency, and accounting equation balance.
- **Deterministic Assertions (`assertions.py`)**:
  - **Math Accuracy**: Subtotals, Gross Profit, Operating Income, Net Income, Cash Flow Net Change.
  - **Cross-Statement Tie-Outs**: Net Income tie-out (IS vs. CFS), Ending Cash tie-out (CFS vs. BS), Retained Earnings Roll-Forward.
  - **Footnote Schedules**: AR Aging footing, PP&E Net Book Value, Debt Maturity Schedule tie-outs to Balance Sheet.
- **Financial Statement Analytics (`analytics.py`)**:
  - Calculates Year-over-Year (YoY) dollar change and percentage change for all Income Statement and Balance Sheet line items.
  - Flags items exceeding variance thresholds.
- **Financial Ratio Benchmarking (`analytics.py`)**:
  - Tests 11 financial ratios (Current Ratio, Quick Ratio, Debt-to-Equity, Interest Coverage, DSO, DIO, DPO, Cash Conversion Cycle, Gross Margin, Operating Margin, Tax Rate) against GAAP/IFRS industry benchmarks.

### 3. Reporting & Archiving Stage (`main.py` + `math_engine/pdf_reporter.py`)
- **JSON Generation**: Outputs full structured report to `results.json`.
- **PDF Generation**: Renders a 5-section multi-page PDF report to `result.pdf` containing:
  1. Engagement Metadata & Audit Conclusion Status (`CLEARED`, `REVIEW REQUIRED`, or `REJECTED`).
  2. Detailed Audit Findings & Exceptions Table.
  3. YoY Financial Statement Variance Tables (Income Statement & Balance Sheet).
  4. Financial Ratio Benchmarking Table.
  5. Full 56-Procedure Execution Register.
- **Timestamped History**: Automatically saves a copy to `history/run_YYYYMMDD_HHMMSS/` so past runs are never lost when you update Excel data and re-run.

---

## 📊 Current Status & Verification Metrics

- **Unit Test Suite (`pytest -v`)**:
  - `test_schema_ingestion` **PASSED**
  - `test_structured_report_generation` **PASSED**
  - `test_load_true_data_folder` **PASSED**
  - `test_load_error_data_folder` **PASSED**
- **Dataset Audit Status**:
  - **`Data/True_data`**: **`CLEARED`** (56/56 procedures passed, 0 findings).
  - **`Data/Error_data`**: **`REJECTED`** (37/56 procedures passed, 19 findings detected).

---

## 🚀 Quick CLI Usage Reference

```powershell
# Run audit on both Data/Error_data and Data/True_data (Default)
python main.py

# Run audit specifically on Error_data
python main.py --dataset error

# Run audit specifically on True_data
python main.py --dataset true

# Run audit on a custom dataset folder
python main.py --data-dir "path/to/custom_excel_data"
```
