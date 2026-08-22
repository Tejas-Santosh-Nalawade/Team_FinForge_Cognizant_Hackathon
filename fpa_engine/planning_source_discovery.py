from pathlib import Path
from typing import Dict

import pandas as pd

from FPA_ENGINE.source_catalog import build_source_catalog


class PlanningSourceDiscovery:
    """
    Discovers forward-looking planning workbooks from the dataset.

    The classifier uses source metadata from the central registry and
    content-based evidence from the workbook.

    It does not generate or hard-code financial values.
    """

    def __init__(
        self,
        dataset_dir: str | Path,
        data_version: str = "True_data",
    ):
        self.dataset_dir = Path(dataset_dir)
        self.data_version = data_version

        self.data_dir = (
            self.dataset_dir
            / self.data_version
        )

        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Data directory does not exist: {self.data_dir}"
            )

        self.source_registry = build_source_catalog()

    def discover_workbooks(self) -> list[Path]:
        """
        Discover all Excel workbooks recursively.
        """

        extensions = {
            ".xlsx",
            ".xls",
            ".xlsm",
        }

        return sorted(
            file
            for file in self.data_dir.rglob("*")
            if file.is_file()
            and file.suffix.lower() in extensions
        )

    @staticmethod
    def _normalize_text(value: object) -> str:
        """
        Normalize text for reliable content matching.
        """

        return (
            str(value)
            .lower()
            .replace("_", " ")
            .replace("-", " ")
            .replace("/", " ")
            .replace("(", " ")
            .replace(")", " ")
            .replace(",", " ")
            .replace(".", " ")
            .strip()
        )

    @classmethod
    def _text_from_workbook(
        cls,
        file_path: Path,
    ) -> str:
        """
        Extract searchable text from:

        1. Workbook filename
        2. Worksheet names
        3. Workbook cell contents
        """

        parts = [
            cls._normalize_text(file_path.name)
        ]

        try:
            sheets = pd.read_excel(
                file_path,
                sheet_name=None,
                header=None,
            )

            for sheet_name, dataframe in sheets.items():

                parts.append(
                    cls._normalize_text(sheet_name)
                )

                for value in dataframe.astype(str).to_numpy().flatten():
                    if value and value.lower() != "nan":
                        parts.append(
                            cls._normalize_text(value)
                        )

        except Exception:
            # Filename evidence is still available even if
            # workbook contents cannot be read.
            pass

        return " ".join(parts)

    @staticmethod
    def _meaningful_tokens(text: str) -> list[str]:
        """
        Return meaningful tokens.

        Very short/common connector words are excluded so that
        words such as 'and' cannot become classification evidence.
        """

        ignored = {
            "and",
            "the",
            "for",
            "with",
            "from",
            "into",
            "that",
            "this",
            "are",
            "was",
            "were",
            "not",
            "one",
            "two",
            "three",
        }

        return [
            token
            for token in text.split()
            if len(token) >= 3
            and token not in ignored
        ]

    def _source_search_terms(
        self,
        source_id: str,
        source_category: str,
        description: str,
    ) -> Dict[str, list[str]]:
        """
        Build evidence terms from registered source metadata.

        The important distinction is that single generic words are
        not sufficient evidence.

        The method derives phrases and meaningful tokens from the
        central source registry rather than maintaining a separate
        hard-coded keyword dictionary.
        """

        metadata_values = [
            source_id,
            source_category,
            description,
        ]

        phrases = set()
        tokens = set()

        for value in metadata_values:

            normalized = self._normalize_text(value)

            if normalized:
                phrases.add(normalized)

            tokens.update(
                self._meaningful_tokens(normalized)
            )

        return {
            "phrases": sorted(
                phrases,
                key=len,
                reverse=True,
            ),
            "tokens": sorted(
                tokens,
                key=len,
                reverse=True,
            ),
        }

    def _score_source(
        self,
        text: str,
        source_id: str,
        source_category: str,
        description: str,
    ) -> Dict[str, object]:
        """
        Calculate content evidence for one source category.

        Exact metadata phrases receive stronger evidence than
        individual words.

        A single generic token is never sufficient.
        """

        search_terms = self._source_search_terms(
            source_id=source_id,
            source_category=source_category,
            description=description,
        )

        matched_phrases = [
            phrase
            for phrase in search_terms["phrases"]
            if len(phrase.split()) >= 2
            and phrase in text
        ]

        matched_tokens = [
            token
            for token in search_terms["tokens"]
            if token in text
        ]

        # Exact multi-word metadata phrase is strong evidence.
        phrase_score = len(matched_phrases) * 3

        # Multiple meaningful tokens provide supporting evidence.
        token_score = len(matched_tokens)

        score = phrase_score + token_score

        # A planning source needs more than one piece of evidence.
        is_candidate = (
            len(matched_phrases) >= 1
            or len(matched_tokens) >= 2
        )

        return {
            "score": score,
            "matched_phrases": matched_phrases,
            "matched_tokens": matched_tokens,
            "is_candidate": is_candidate,
        }

    def classify_workbook(
        self,
        file_path: Path,
    ) -> Dict[str, object]:
        """
        Classify a workbook using content-based evidence.

        Historical financial workbooks located inside the existing
        current_data/prior_data structure are not treated as
        forward-looking planning sources merely because they contain
        generic words such as 'operating'.
        """

        text = self._text_from_workbook(file_path)

        matches = {}

        planning_categories = {
            source.source_category
            for source in self.source_registry.to_dataframe().itertuples()
            if source.source_category in {
                "AOB",
                "4Q_rolling_forecast",
                "8Q_rolling_forecast",
                "operational_drivers",
            }
        }

        for source in self.source_registry.to_dataframe().itertuples():

            source_category = source.source_category

            if source_category not in planning_categories:
                continue

            evidence = self._score_source(
                text=text,
                source_id=source.source_id,
                source_category=source.source_category,
                description=source.description,
            )

            if evidence["is_candidate"]:

                matches[source_category] = evidence

        return {
            "file": str(file_path),
            "matches": matches,
        }

    def discover_planning_sources(
        self,
    ) -> pd.DataFrame:
        """
        Discover forward-looking planning source candidates.

        Returns only sources for which sufficient content evidence
        exists.
        """

        records = []

        for file_path in self.discover_workbooks():

            result = self.classify_workbook(
                file_path
            )

            for category, evidence in result["matches"].items():

                matched_evidence = (
                    evidence["matched_phrases"]
                    + evidence["matched_tokens"]
                )

                records.append(
                    {
                        "file": result["file"],
                        "category": category,
                        "matched_evidence": ", ".join(
                            sorted(set(matched_evidence))
                        ),
                        "evidence_score": evidence["score"],
                        "status": "candidate",
                    }
                )

        columns = [
            "file",
            "category",
            "matched_evidence",
            "evidence_score",
            "status",
        ]

        return pd.DataFrame(
            records,
            columns=columns,
        )