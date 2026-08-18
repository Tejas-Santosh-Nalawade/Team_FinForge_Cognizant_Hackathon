from pathlib import Path
from typing import Dict

import pandas as pd


class OperationalDriverLoader:
    """
    Loads driver-related information from the existing source data.

    Values are read from source workbooks and are not hard-coded.
    """

    def __init__(
        self,
        dataset_dir: str | Path,
        data_version: str = "True_data",
    ):
        self.dataset_dir = Path(dataset_dir)
        self.data_version = data_version

        self.current_dir = (
            self.dataset_dir
            / self.data_version
            / "current_data"
        )

        self.footnotes_dir = self.current_dir / "footnotes"

        self._validate_directories()

    def _validate_directories(self) -> None:
        """Verify that the required source directory exists."""

        if not self.dataset_dir.exists():
            raise FileNotFoundError(
                f"Dataset directory does not exist: {self.dataset_dir}"
            )

        if not self.footnotes_dir.exists():
            raise FileNotFoundError(
                f"Footnotes directory does not exist: {self.footnotes_dir}"
            )

    def _load_workbook(
        self,
        file_name: str,
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all worksheets from a source workbook.
        """

        file_path = self.footnotes_dir / file_name

        if not file_path.exists():
            raise FileNotFoundError(
                f"Driver source does not exist: {file_path}"
            )

        return pd.read_excel(
            file_path,
            sheet_name=None,
            header=None,
        )

    def load_ar_aging(self) -> Dict[str, pd.DataFrame]:
        """
        Load Accounts Receivable aging data.
        """

        return self._load_workbook("ar_aging.xlsx")

    def load_debt_maturity(self) -> Dict[str, pd.DataFrame]:
        """
        Load debt maturity data.
        """

        return self._load_workbook("debt_maturity.xlsx")

    def load_ppe_schedule(self) -> Dict[str, pd.DataFrame]:
        """
        Load PP&E and CapEx data.
        """

        return self._load_workbook("ppe_sched.xlsx")

    def discover_driver_sources(self) -> list[str]:
        """
        Discover available footnote source files.

        No individual source filenames are hard-coded
        into the discovery process.
        """

        return sorted(
            file.name
            for file in self.footnotes_dir.glob("*.xlsx")
        )