from dataclasses import dataclass, asdict
from typing import Optional

import pandas as pd


@dataclass
class ForwardAssumption:
    """
    Represents one forward-looking FP&A input.

    Every assumption carries provenance so that the forecast
    can distinguish source-derived values from generated assumptions.
    """

    driver: str
    value: Optional[float]
    unit: str
    period: str
    source: str
    source_type: str
    method: str
    status: str


class AssumptionEngine:
    """
    Builds a structured registry of forward-looking assumptions.

    No financial assumption values are hard-coded here.
    """

    def __init__(
        self,
        calculated_drivers: pd.DataFrame,
    ):
        self.calculated_drivers = calculated_drivers.copy()

    def build_source_derived_assumptions(
        self,
        forecast_period: str,
    ) -> pd.DataFrame:
        """
        Convert calculated historical drivers into explicitly
        labelled forward-looking reference assumptions.

        These are NOT forecasts by themselves. They are historical
        driver references that can be used by a forecast policy.
        """

        assumptions = []

        for _, row in self.calculated_drivers.iterrows():

            assumptions.append(
                ForwardAssumption(
                    driver=row["driver"],
                    value=float(row["value"]),
                    unit="ratio",
                    period=forecast_period,
                    source=row["source"],
                    source_type="calculated",
                    method="historical_source_ratio",
                    status="reference",
                )
            )

        return pd.DataFrame(
            [asdict(item) for item in assumptions]
        )

    def register_missing_operational_drivers(
        self,
        drivers: list[str],
        forecast_period: str,
    ) -> pd.DataFrame:
        """
        Register operational drivers that are not present in the
        available source data.

        Values remain empty until a documented source or approved
        assumption policy supplies them.
        """

        assumptions = []

        for driver in drivers:

            assumptions.append(
                ForwardAssumption(
                    driver=driver,
                    value=None,
                    unit="not_specified",
                    period=forecast_period,
                    source="not_present_in_available_dataset",
                    source_type="missing_source",
                    method="requires_explicit_assumption_policy",
                    status="pending",
                )
            )

        return pd.DataFrame(
            [asdict(item) for item in assumptions]
        )