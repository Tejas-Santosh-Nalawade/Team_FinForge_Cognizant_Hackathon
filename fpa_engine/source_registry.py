from dataclasses import dataclass, asdict
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class SourceDefinition:
    """
    Describes a source that may provide FP&A or regulatory inputs.

    This contains metadata only. It does not contain financial values.
    """

    source_id: str
    source_category: str
    description: str
    authority_level: str
    required: bool
    path: Optional[str] = None


class SourceRegistry:
    """
    Central registry for all FP&A and qualitative source categories.
    """

    def __init__(self):
        self._sources: list[SourceDefinition] = []

    def register(
        self,
        source_id: str,
        source_category: str,
        description: str,
        authority_level: str,
        required: bool,
        path: Optional[str] = None,
    ) -> None:

        self._sources.append(
            SourceDefinition(
                source_id=source_id,
                source_category=source_category,
                description=description,
                authority_level=authority_level,
                required=required,
                path=path,
            )
        )

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            [asdict(source) for source in self._sources]
        )

    def find(
        self,
        source_category: str,
    ) -> list[SourceDefinition]:

        return [
            source
            for source in self._sources
            if source.source_category == source_category
        ]