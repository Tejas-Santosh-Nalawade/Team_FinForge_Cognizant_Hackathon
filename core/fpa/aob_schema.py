from dataclasses import dataclass, asdict
from typing import Optional

import pandas as pd


@dataclass
class AOBInput:
    """
    Represents one Annual Operating Budget input.

    Values may come from an authoritative source, an approved
    planning document, or remain pending when no source exists.
    """

    period: str
    driver: str
    value: Optional[float]
    unit: str
    source: str
    source_type: str
    methodology: str
    status: str


class AOBInputRegistry:
    """
    Registry for Annual Operating Budget inputs.

    The registry does not invent financial values.
    """

    def __init__(self):
        self._inputs: list[AOBInput] = []

    def add(
        self,
        period: str,
        driver: str,
        value: Optional[float],
        unit: str,
        source: str,
        source_type: str,
        methodology: str,
        status: str,
    ) -> None:

        self._inputs.append(
            AOBInput(
                period=period,
                driver=driver,
                value=value,
                unit=unit,
                source=source,
                source_type=source_type,
                methodology=methodology,
                status=status,
            )
        )

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            [asdict(item) for item in self._inputs]
        )