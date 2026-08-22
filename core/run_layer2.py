from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.normalization.layer2_service import normalize_layer1_bundle


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run Layer 2 normalization on Layer 1 data. Metadata is inferred from the source files."
    )
    ap.add_argument("input_path", help="Layer 1 folder or supported source file")
    ap.add_argument("--output-dir", default="layer2_output")
    ap.add_argument("--include-qualitative", action="store_true")
    args = ap.parse_args()

    result = normalize_layer1_bundle(
        [args.input_path],
        include_qualitative=args.include_qualitative,
        output_dir=args.output_dir,
    )

    summary = result["normalization_report"]["summary"]
    print(json.dumps(summary, indent=2))
    print("Detected metadata:")
    print(json.dumps(result["financial_statements"].get("metadata", {}), indent=2))
    print("Layer 3 payload:", Path(args.output_dir) / "financial_statements.json")


if __name__ == "__main__":
    main()
