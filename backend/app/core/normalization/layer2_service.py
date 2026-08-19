"""Layer 2 service boundary: Layer 1 inputs -> normalized Layer 3 contract."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Any

from pydantic import ValidationError

from backend.app.core.assurance_engine.schemas import FinancialStatementsIngestionSchema
from backend.app.core.normalization.layer2_gateway import Layer2Gateway, write_outputs


def normalize_layer1_bundle(
    inputs: Iterable[str | Path],
    *,
    client_name: str | None = None,
    period: str | None = None,
    comparative_period: str | None = None,
    currency: str | None = None,
    scale: str | None = None,
    framework: str | None = None,
    include_qualitative: bool = False,
    output_dir: str | Path | None = None,
    fuzzy_threshold: float = 0.88,
) -> dict[str, Any]:
    """Normalize heterogeneous Layer 1 files without executing Layer 3 computations."""
    result = Layer2Gateway(fuzzy_threshold=fuzzy_threshold).run(
        inputs,
        client_name=client_name,
        period=period,
        comparative_period=comparative_period,
        currency=currency,
        scale=scale,
        framework=framework,
        include_qualitative=include_qualitative,
    )

    # The actual Layer 3 constructor is the final financial contract authority.
    constructor_errors = []
    try:
        FinancialStatementsIngestionSchema(**result["financial_statements"])
        # Validate against the real Layer 3 constructor, but preserve the Layer 2
        # payload exactly as detected/normalized. This prevents Layer 3 Pydantic
        # defaults from being mistaken for metadata extracted by Layer 2.
        result["normalization_report"]["summary"]["layer3_constructor_ready"] = True
    except ValidationError as exc:
        constructor_errors = [
            {"path": ".".join(str(x) for x in err.get("loc", [])), "message": err.get("msg", "validation error")}
            for err in exc.errors()
        ]
        result["normalization_report"]["layer3_constructor_errors"] = constructor_errors
        result["normalization_report"]["summary"]["layer3_constructor_ready"] = False
        result["normalization_report"]["summary"]["financial_contract_ready"] = False

    if output_dir is not None:
        result["written_files"] = write_outputs(result, output_dir)
    return result
