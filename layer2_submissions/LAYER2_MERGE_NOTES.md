# Layer 2 Merge Notes

This build follows the architecture specification boundary:

`Layer 1 Ingestion & Parsing -> Layer 2 Normalization & Spelling/Grammar Check -> Layer 3 Dual-Track Computation`

## Added / upgraded

- `backend/app/core/normalization/coa_mapper.py` — context-aware exact/alias/fuzzy canonical mapper with ambiguity safety.
- `backend/app/core/normalization/canonical_taxonomy.json` — extensible finance alias taxonomy mapped to exact Layer 3 field/code names.
- `backend/app/core/parser/spell_checker.py` — deterministic financial spelling, terminology, signage and light grammar audit.
- `backend/app/core/normalization/normalization_utils.py` — currency/scale inference, scale conversion and field-specific sign normalization.
- `backend/app/core/normalization/source_router.py` — routes financial/planning/qualitative sources and excludes ground-truth/derived artifacts.
- `backend/app/core/normalization/layer2_gateway.py` — end-to-end Layer 2 orchestration, source trace and normalization report.
- `backend/app/core/normalization/layer2_service.py` — validates the Layer 2 financial payload with the actual Layer 3 Pydantic constructor.
- `backend/app/api/v1/ingestion.py` — new `/ingest/normalize-bundle` ZIP endpoint for the Layer 2 handoff.
- `backend/run_layer2.py` — local CLI runner.
- `backend/tests/test_layer2_normalization.py` — mapper/spell-check safety tests.
- `backend/LAYER2_INTEGRATION.md` — run and ownership guide.
- `backend/requirements.txt` — adds `jsonschema` used for planning contract validation.

## Verified against final Layer 1 True_data

- 50 files discovered; 12 production financial/planning files processed when qualitative audit is off.
- 99 financial records seen, 99 mapped, 0 unmapped, 0 ambiguous.
- 0 parse, unit or schema-validation errors.
- `financial_contract_ready = true`.
- `planning_contracts_ready = true`.
- `layer3_constructor_ready = true` using the final repo's `FinancialStatementsIngestionSchema`.

With `--include-qualitative`, raw entity-authored qualitative sources are audited while authoritative US GAAP / bank-directive references are not typo-flagged. Derived RAG chunks and ground-truth/test files are excluded from the financial contract.

## Layer boundary

Layer 2 does not execute Layer 3 math and does not normalize Layer 3-generated outputs. Post-Layer-3 output terminology/narrative QA remains the responsibility of the downstream intelligence/output flow.

## Standalone Layer 2 execution
The patch can be executed by itself for Layer 1 -> Layer 2 validation. The root `requirements.txt` is intentionally minimal. Metadata (client/entity, current and comparative period, currency, and scale) is inferred from the source bundle; the CLI does not require those values. Missing required metadata is reported instead of silently hard-coded.

Run from the patch root:
`python run_layer2.py <path-to-Layer1-True_data>`
