from typing import Dict

import pandas as pd


class DriverAnalysis:
    """
    Derives FP&A driver metrics from source data.

    The class does not hard-code financial values.
    Calculated metrics are derived from the supplied source data.
    """

    def __init__(
        self,
        income_statement: pd.DataFrame,
        ar_aging: pd.DataFrame,
        debt_maturity: pd.DataFrame,
        ppe_schedule: pd.DataFrame,
    ):
        self.income_statement = self._normalize_table(
            income_statement
        )

        self.ar_aging = self._normalize_table(
            ar_aging
        )

        self.debt_maturity = self._normalize_table(
            debt_maturity
        )

        self.ppe_schedule = self._normalize_table(
            ppe_schedule
        )

    @staticmethod
    def _normalize_table(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Normalize a two-column source table into:

            line_item | value
        """

        df = dataframe.iloc[:, :2].copy()

        df.columns = [
            "line_item",
            "value",
        ]

        df["line_item"] = (
            df["line_item"]
            .astype(str)
            .str.strip()
        )

        df["value"] = pd.to_numeric(
            df["value"],
            errors="coerce",
        )

        return df.dropna(
            subset=["value"]
        )

    def _get_value(
        self,
        dataframe: pd.DataFrame,
        line_item: str,
    ) -> float:
        """
        Retrieve a numeric source value by its source label.
        """

        matches = dataframe.loc[
            dataframe["line_item"].str.casefold()
            == line_item.casefold(),
            "value",
        ]

        if matches.empty:
            raise KeyError(
                f"Source line item not found: {line_item}"
            )

        return float(matches.iloc[0])

    def calculate_source_derived_metrics(self) -> pd.DataFrame:
        """
        Calculate operationally useful ratios from source data.
        """

        revenue = self._get_value(
            self.income_statement,
            "Revenue",
        )

        gross_ar = self._get_value(
            self.ar_aging,
            "Gross Accounts Receivable",
        )

        total_debt = self._get_value(
            self.debt_maturity,
            "Total Debt",
        )

        capex = self._get_value(
            self.ppe_schedule,
            "Additions / CapEx",
        )

        depreciation = self._get_value(
            self.ppe_schedule,
            "Depreciation Expense",
        )

        gross_ppe = self._get_value(
            self.ppe_schedule,
            "Gross PP&E",
        )

        metrics = [
            {
                "driver": "AR_to_Revenue",
                "value": gross_ar / revenue,
                "source": "AR Aging + Income Statement",
                "type": "calculated",
            },
            {
                "driver": "Debt_to_Revenue",
                "value": total_debt / revenue,
                "source": "Debt Maturity + Income Statement",
                "type": "calculated",
            },
            {
                "driver": "CapEx_to_Revenue",
                "value": capex / revenue,
                "source": "PP&E Schedule + Income Statement",
                "type": "calculated",
            },
            {
                "driver": "Depreciation_to_Gross_PPE",
                "value": abs(depreciation) / gross_ppe,
                "source": "PP&E Schedule",
                "type": "calculated",
            },
        ]

        return pd.DataFrame(metrics)