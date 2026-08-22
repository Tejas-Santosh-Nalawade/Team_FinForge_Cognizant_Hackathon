from dataclasses import dataclass, asdict
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class ForecastInput:
    """
    Represents one input used by the forecast engine.

    The value may remain None when the required planning source
    is unavailable.
    """

    metric: str
    period: str
    value: Optional[float]
    unit: str
    source: str
    source_type: str
    method: str
    status: str


class ForecastPolicy:
    """
    Controls how forward-looking inputs are treated.

    The policy never invents missing financial values.
    """

    def __init__(self):
        self.inputs: list[ForecastInput] = []

    def register_source_input(
        self,
        metric: str,
        period: str,
        value: float,
        unit: str,
        source: str,
        source_type: str,
        method: str = "direct_source_ingestion",
    ) -> None:

        self.inputs.append(
            ForecastInput(
                metric=metric,
                period=period,
                value=value,
                unit=unit,
                source=source,
                source_type=source_type,
                method=method,
                status="available",
            )
        )

    def register_missing_input(
        self,
        metric: str,
        period: str,
        unit: str,
    ) -> None:

        self.inputs.append(
            ForecastInput(
                metric=metric,
                period=period,
                value=None,
                unit=unit,
                source="not_available",
                source_type="missing_source",
                method="requires_approved_assumption",
                status="pending",
            )
        )

    def to_dataframe(self) -> pd.DataFrame:

        return pd.DataFrame(
            [asdict(item) for item in self.inputs]
        )