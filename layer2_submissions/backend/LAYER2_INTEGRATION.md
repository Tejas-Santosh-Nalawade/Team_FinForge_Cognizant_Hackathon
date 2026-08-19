# Layer 2 — Normalization & Spelling/Grammar Check

Architecture boundary: **Layer 1 parsed financial/planning/qualitative inputs -> Layer 2 normalization/quality -> Layer 3 computation engines**.

Layer 2 owns:
- context-aware Canonical Chart of Accounts mapping to exact Layer 3 attribute names;
- deterministic financial spelling, terminology and light grammar checks;
- unit/scale and signage normalization without FX invention;
- ambiguity/unmapped handling instead of unsafe guessing;
- source traceability and normalization reporting;
- validation against the actual `FinancialStatementsIngestionSchema` constructor.

It does **not** execute Layer 3 math, rewrite Layer 3 outputs, or perform final narrative/report formatting.

## Run with final Layer 1 data
From the `backend` directory:

```powershell
python .\run_layer2.py "C:\path\to\Cognizant-main\DATASET\True_data" --output-dir .\layer2_output --client-name "AsterNova Technologies Ltd." --period 2026-03-31 --comparative-period 2025-03-31 --currency INR --scale MILLIONS
```

The main handoff to Layer 3 is `layer2_output/financial_statements.json`. Review `normalization_report.json` and `source_trace.json` alongside it.

Use `--include-qualitative` only when Layer 2 should audit textual disclosures/MD&A. Pre-generated Layer 1 RAG derivatives and test/ground-truth artifacts are routed away from the financial contract.
