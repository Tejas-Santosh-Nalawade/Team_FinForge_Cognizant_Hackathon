# Final Layer 2 Integration

This patch implements the pre-computation Layer 2 defined in the architecture:

- Canonical Chart of Accounts mapping
- Financial spelling / terminology / light grammar audit
- Sign normalization
- Currency and scale normalization
- Ambiguous/unmapped protection
- Source traceability
- Layer 3 schema/constructor validation
- Multi-entity additive consolidation

## Multi-entity behavior

Layer 2 detects entity names from explicit Entity/Company/Subsidiary headers and common folder conventions such as `entities/<entity_name>/...`.

If one entity is detected, behavior is unchanged.

If multiple entities are detected, canonical financial fields are normalized per entity and then summed. Explicit elimination/consolidation-adjustment entities are included at the sign supplied in the source. Layer 2 never fabricates intercompany eliminations; when multiple entities are present without an explicit elimination entity, a medium-severity consolidation quality issue is emitted.

## Run after merging into the team repository

From the team repository root:

```powershell
python .\run_layer2.py "C:\Users\Admin\Desktop\Cogzi\Cognizant-main\DATASET\True_data"
```

No company name, date, currency, scale, or framework is required on the command line. Layer 2 extracts metadata from Layer 1 inputs and flags missing metadata instead of silently defaulting it.

## Tests

```powershell
python -m pytest .\backend\tests\test_layer2_normalization.py -v
```

The test suite includes context-aware mapping, typo/unknown-label safety, spelling/grammar checks, and synthetic multi-entity consolidation.
