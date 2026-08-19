from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


PRODUCTION_EXCLUDES = {
    "guardrail_results.csv",
    "injected_flaws_ground_truth.json",
    "duplicate_audit.json",
    "final_quality_audit.json",
    "corpus_manifest.json",
    "handoff_summary.json",
    "qualitative_rag_handoff.jsonl",
}
DERIVED_QUALITATIVE_DIRS = {"normalized_chunks", "processed_chunks", "rag_handoff"}


@dataclass(frozen=True)
class SourceRoute:
    channel: str  # financial | planning | qualitative | generic | ignored
    reason: str
    period_kind: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def route_source(path: str | Path, *, include_qualitative: bool = False) -> SourceRoute:
    p = Path(path)
    parts = [x.lower() for x in p.parts]
    name = p.name.lower()

    if name in PRODUCTION_EXCLUDES:
        return SourceRoute("ignored", "test/reference artifact excluded from production ingestion")

    if "qualitative_corpus" in parts:
        if any(d in parts for d in DERIVED_QUALITATIVE_DIRS):
            return SourceRoute("ignored", "derived qualitative artifact; raw source corpus is preferred")
        if not include_qualitative:
            return SourceRoute("ignored", "qualitative ingestion disabled")
        return SourceRoute("qualitative", "raw qualitative corpus source")

    if "planning_inputs" in parts or name in {"planning_inputs.xlsx", "planning_inputs.xlsm"}:
        return SourceRoute("planning", "planning input workbook")

    if "current_data" in parts:
        return SourceRoute("financial", "current-period financial source", "current")
    if "prior_data" in parts:
        return SourceRoute("financial", "prior-period financial source", "prior")

    return SourceRoute("generic", "dashboard file outside known Layer 1 folder structure")
