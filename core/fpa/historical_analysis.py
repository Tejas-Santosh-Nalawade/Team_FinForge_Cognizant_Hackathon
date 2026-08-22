from typing import Dict

import pandas as pd


class HistoricalFinancialAnalysis:
    """
    Calculates historical financial movements from source-loaded
    current and prior financial statements.

    No financial values or growth assumptions are hard-coded.
    """

    def __init__(
        self,
        current_data: Dict[str, pd.DataFrame],
        prior_data: Dict[str, pd.DataFrame],
    ):
        self.current_data = current_data
        self.prior_data = prior_data

    @staticmethod
    def _prepare_statement(
        statement: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert the source financial statement into a normalized
        two-column structure:

            Line Item | Value

        The unit remains in the source column name.
        """

        if statement.shape[1] < 2:
            raise ValueError(
                "Financial statement must contain at least "
                "a line-item column and a value column."
            )

        df = statement.iloc[:, :2].copy()

        df.columns = ["line_item", "value"]

        df["line_item"] = (
            df["line_item"]
            .astype(str)
            .str.strip()
        )

        df["value"] = pd.to_numeric(
            df["value"],
            errors="coerce",
        )

        df = df.dropna(
            subset=["line_item", "value"]
        )

        return df

    def compare_statement(
        self,
        statement_name: str,
    ) -> pd.DataFrame:
        """
        Compare the same financial statement across
        prior and current periods.
        """

        current = self._prepare_statement(
            self.current_data[statement_name]
        )

        prior = self._prepare_statement(
            self.prior_data[statement_name]
        )

        comparison = current.merge(
            prior,
            on="line_item",
            how="outer",
            suffixes=("_current", "_prior"),
        )

        comparison["absolute_change"] = (
            comparison["value_current"]
            - comparison["value_prior"]
        )

        comparison["percentage_change"] = (
            comparison["absolute_change"]
            / comparison["value_prior"].abs()
        ) * 100

        return comparison

    def income_statement_analysis(self) -> pd.DataFrame:
        """
        Produce historical analysis for the income statement.
        """

        return self.compare_statement(
            "Income Statement"
        )