# Layer 2 GitHub merge patch

Overlay the contents of this folder onto the root of Team_FinForge_Cognizant_Hackathon-main.

This patch intentionally does NOT include or overwrite Layer 3 schemas or backend templates; it imports and validates against the team's existing files.

The `/api/v1/ingest/normalize-bundle` endpoint does not accept hard-coded company/currency/date/scale defaults. Metadata is inferred from the uploaded Layer 1 ZIP. Missing metadata is reported by Layer 2.

After overlay, ensure `jsonschema>=4.22.0` is present in `backend/requirements.txt`.
