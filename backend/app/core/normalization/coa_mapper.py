"""Layer 2 canonical financial taxonomy mapper.

Maps heterogeneous Layer 1 labels to the exact Layer 3 field/code vocabulary.
No human-readable display-name layer is produced.

Matching strategy:
  1. exact canonical name/code
  2. exact alias after deterministic text normalization
  3. abbreviation-expanded exact alias
  4. controlled fuzzy match inside a caller-supplied context
  5. UNMAPPED / AMBIGUOUS instead of guessing
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


DEFAULT_TAXONOMY = Path(__file__).with_name("canonical_taxonomy.json")

CONTEXT_PATHS = {
    "balance_sheet": ("statement_fields", "balance_sheet"),
    "income_statement": ("statement_fields", "income_statement"),
    "cash_flow_statement": ("statement_fields", "cash_flow_statement"),
    "equity_statement": ("statement_fields", "equity_statement"),
    "ar_aging": ("schedule_fields", "ar_aging"),
    "ppe_sched": ("schedule_fields", "ppe_sched"),
    "debt_maturity": ("schedule_fields", "debt_maturity"),
    "budget_metric": ("budget_metric_codes",),
    "aob_driver": ("aob_driver_codes",),
    "operational_driver": ("operational_driver_types",),
    "associated_financial_metric": ("associated_financial_metrics",),
}


@dataclass(frozen=True)
class MappingResult:
    original_label: str
    canonical: Optional[str]
    status: str
    method: str
    confidence: float
    context: Optional[str]
    normalized_label: str
    alternatives: Tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


class CanonicalMapper:
    def __init__(
        self,
        taxonomy_path: str | Path = DEFAULT_TAXONOMY,
        fuzzy_threshold: float = 0.88,
        ambiguity_margin: float = 0.035,
    ) -> None:
        self.taxonomy_path = Path(taxonomy_path)
        self.taxonomy = json.loads(self.taxonomy_path.read_text(encoding="utf-8"))
        self.fuzzy_threshold = fuzzy_threshold
        self.ambiguity_margin = ambiguity_margin
        self.abbreviations = {
            self._basic_normalize(k): self._basic_normalize(v)
            for k, v in self.taxonomy.get("abbreviation_expansions", {}).items()
        }
        self._indexes = {ctx: self._build_context_index(ctx) for ctx in CONTEXT_PATHS}

    @staticmethod
    def _basic_normalize(text: str) -> str:
        text = unicodedata.normalize("NFKD", str(text))
        text = text.replace("&", " and ")
        text = text.replace("/", " ")
        text = text.replace("–", "-").replace("—", "-")
        text = text.lower().strip()
        text = re.sub(r"\((loss|expense|repayments?|decrease)\)", r" \1 ", text)
        text = re.sub(r"[^a-z0-9+><]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def normalize_label(self, label: str) -> str:
        text = self._basic_normalize(label)
        # Whole-label abbreviation first.
        if text in self.abbreviations:
            return self.abbreviations[text]
        # Then token/phrase expansion, longest keys first.
        for short in sorted(self.abbreviations, key=len, reverse=True):
            if re.search(rf"(?<![a-z0-9]){re.escape(short)}(?![a-z0-9])", text):
                text = re.sub(
                    rf"(?<![a-z0-9]){re.escape(short)}(?![a-z0-9])",
                    self.abbreviations[short],
                    text,
                )
        return re.sub(r"\s+", " ", text).strip()

    def _get_context_map(self, context: str) -> Dict[str, List[str]]:
        if context not in CONTEXT_PATHS:
            raise ValueError(
                f"Unknown context {context!r}. Expected one of: {', '.join(sorted(CONTEXT_PATHS))}"
            )
        obj = self.taxonomy
        for key in CONTEXT_PATHS[context]:
            obj = obj[key]
        return obj

    def _build_context_index(self, context: str) -> dict:
        mapping = self._get_context_map(context)
        alias_to_canonicals: Dict[str, set] = {}
        canonical_aliases: Dict[str, set] = {}

        for canonical, aliases in mapping.items():
            normalized_aliases = {self.normalize_label(canonical)}
            normalized_aliases.update(self.normalize_label(a) for a in aliases)
            canonical_aliases[canonical] = normalized_aliases
            for alias in normalized_aliases:
                alias_to_canonicals.setdefault(alias, set()).add(canonical)

        return {
            "alias_to_canonicals": alias_to_canonicals,
            "canonical_aliases": canonical_aliases,
        }

    @staticmethod
    def _token_score(a: str, b: str) -> float:
        a_tokens, b_tokens = set(a.split()), set(b.split())
        if not a_tokens or not b_tokens:
            return 0.0
        intersection = len(a_tokens & b_tokens)
        union = len(a_tokens | b_tokens)
        return intersection / union if union else 0.0

    @classmethod
    def _similarity(cls, a: str, b: str) -> float:
        seq = SequenceMatcher(None, a, b).ratio()
        token = cls._token_score(a, b)
        # Sequence score handles spelling errors; token overlap handles word reordering.
        return max(seq, 0.65 * seq + 0.35 * token, token)

    def map_label(
        self,
        label: str,
        context: str,
        *,
        allow_fuzzy: bool = True,
    ) -> MappingResult:
        original = str(label)
        normalized = self.normalize_label(original)
        idx = self._indexes[context]
        exact = idx["alias_to_canonicals"].get(normalized, set())

        if len(exact) == 1:
            canonical = next(iter(exact))
            method = "canonical_exact" if normalized == self.normalize_label(canonical) else "alias_exact"
            return MappingResult(original, canonical, "MAPPED", method, 1.0, context, normalized)

        if len(exact) > 1:
            alts = tuple(sorted(exact))
            return MappingResult(original, None, "AMBIGUOUS", "alias_collision", 1.0, context, normalized, alts)

        if not allow_fuzzy or not normalized:
            return MappingResult(original, None, "UNMAPPED", "none", 0.0, context, normalized)

        scored: List[Tuple[float, str, str]] = []
        for canonical, aliases in idx["canonical_aliases"].items():
            best_alias = ""
            best_score = 0.0
            for alias in aliases:
                score = self._similarity(normalized, alias)
                if score > best_score:
                    best_score, best_alias = score, alias
            scored.append((best_score, canonical, best_alias))

        scored.sort(reverse=True)
        best_score, best_canonical, _ = scored[0]
        second_score = scored[1][0] if len(scored) > 1 else 0.0

        if best_score < self.fuzzy_threshold:
            alternatives = tuple(c for s, c, _ in scored[:3] if s >= self.fuzzy_threshold - 0.08)
            return MappingResult(original, None, "UNMAPPED", "fuzzy_below_threshold", round(best_score, 4), context, normalized, alternatives)

        if second_score >= self.fuzzy_threshold and (best_score - second_score) < self.ambiguity_margin:
            alternatives = tuple(c for s, c, _ in scored[:3] if (best_score - s) < self.ambiguity_margin)
            return MappingResult(original, None, "AMBIGUOUS", "fuzzy_ambiguous", round(best_score, 4), context, normalized, alternatives)

        return MappingResult(original, best_canonical, "MAPPED", "fuzzy_alias", round(best_score, 4), context, normalized)

    def map_many(self, labels: Iterable[str], context: str, *, allow_fuzzy: bool = True) -> List[dict]:
        return [self.map_label(x, context, allow_fuzzy=allow_fuzzy).to_dict() for x in labels]

    def canonical_values(self, context: str) -> Tuple[str, ...]:
        return tuple(self._get_context_map(context).keys())


def map_to_canonical(label: str, context: str, taxonomy_path: str | Path = DEFAULT_TAXONOMY) -> Optional[str]:
    """Convenience function returning only the exact Layer 3 canonical value or None."""
    result = CanonicalMapper(taxonomy_path).map_label(label, context)
    return result.canonical if result.status == "MAPPED" else None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Map a financial label to Layer 3 canonical vocabulary.")
    parser.add_argument("label")
    parser.add_argument("--context", required=True, choices=sorted(CONTEXT_PATHS))
    parser.add_argument("--no-fuzzy", action="store_true")
    args = parser.parse_args()

    result = CanonicalMapper().map_label(args.label, args.context, allow_fuzzy=not args.no_fuzzy)
    print(json.dumps(result.to_dict(), indent=2))


# ---------------------------------------------------------------------------
# Backward-compatible API used by the existing Excel parser.
# ---------------------------------------------------------------------------
_DEFAULT_MAPPER = None

def _get_default_mapper():
    global _DEFAULT_MAPPER
    if _DEFAULT_MAPPER is None:
        _DEFAULT_MAPPER = CanonicalMapper()
    return _DEFAULT_MAPPER

def map_to_canonical_coa(raw_label: str, context: Optional[str] = None) -> Tuple[Optional[str], float]:
    """Map a raw financial label to an exact Layer 3 field.

    If context is supplied, mapping is restricted to that statement/schedule.
    Without context, the label is evaluated across financial contexts and is
    accepted only when all successful context matches agree on one canonical
    field.
    """
    mapper = _get_default_mapper()
    if context:
        result = mapper.map_label(raw_label, context)
        return (result.canonical, result.confidence) if result.status == "MAPPED" else (None, result.confidence)

    financial_contexts = (
        "balance_sheet", "income_statement", "cash_flow_statement",
        "equity_statement", "ar_aging", "ppe_sched", "debt_maturity",
    )
    matches = []
    for ctx in financial_contexts:
        result = mapper.map_label(raw_label, ctx)
        if result.status == "MAPPED" and result.canonical:
            matches.append(result)
    canonicals = {m.canonical for m in matches}
    if len(canonicals) == 1:
        best = max(matches, key=lambda x: x.confidence)
        return best.canonical, best.confidence
    return None, 0.0
