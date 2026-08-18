from pathlib import Path
from typing import Dict

import pandas as pd


class FinancialSourceLoader:
    """
    Loads existing financial statement files from the DATASET directory.

    This class does not generate or modify financial values.
    It only reads the source data that already exists in the project.
    """

    def __init__(
        self,
        dataset_dir: str | Path,
        data_version: str = "True_data",
    ):
        self.dataset_dir = Path(dataset_dir)
        self.data_version = data_version

        self.data_version_dir = self.dataset_dir / self.data_version

        self.current_dir = self.data_version_dir / "current_data"
        self.prior_dir = self.data_version_dir / "prior_data"

        self._validate_directories()

    def _validate_directories(self) -> None:
        """Verify that the expected source directories exist."""

        if not self.dataset_dir.exists():
            raise FileNotFoundError(
                f"Dataset directory does not exist: {self.dataset_dir}"
            )

        if not self.data_version_dir.exists():
            raise FileNotFoundError(
                f"Data version directory does not exist: {self.data_version_dir}"
            )

        if not self.current_dir.exists():
            raise FileNotFoundError(
                f"Current-data directory does not exist: {self.current_dir}"
            )

        if not self.prior_dir.exists():
            raise FileNotFoundError(
                f"Prior-data directory does not exist: {self.prior_dir}"
            )

    def _load_workbook(self, file_path: Path) -> Dict[str, pd.DataFrame]:
        """
        Load every worksheet from an Excel workbook.

        The source workbooks may contain title/metadata rows before
        the actual financial table. The loader detects the row
        containing the 'Line Item' marker and uses it as the header.
        """

        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {file_path}"
            )

        if file_path.suffix.lower() not in {".xlsx", ".xls", ".xlsm"}:
            raise ValueError(
                f"Unsupported Excel file type: {file_path.suffix}"
            )

        raw_sheets = pd.read_excel(
            file_path,
            sheet_name=None,
            header=None,
        )

        normalized_sheets = {}

        for sheet_name, raw_df in raw_sheets.items():

            header_row = None

            for row_index, row in raw_df.iterrows():
                values = row.astype(str).str.strip().str.lower()

                if values.eq("line item").any():
                    header_row = row_index
                    break

            if header_row is None:
                normalized_sheets[sheet_name] = raw_df
                continue

            df = raw_df.iloc[header_row:].copy()

            df.columns = df.iloc[0].astype(str).str.strip()

            df = df.iloc[1:].reset_index(drop=True)

            df = df.dropna(how="all")

            normalized_sheets[sheet_name] = df

        return normalized_sheets

    def load_statement(
        self,
        statement_name: str,
        period_type: str,
    ) -> Dict[str, pd.DataFrame]:
        """
        Load one financial statement workbook.
        """

        directory_map = {
            "current": self.current_dir,
            "prior": self.prior_dir,
        }

        if period_type not in directory_map:
            raise ValueError(
                f"Unsupported period_type: {period_type}. "
                f"Expected one of: {sorted(directory_map)}"
            )

        file_path = directory_map[period_type] / f"{statement_name}.xlsx"

        return self._load_workbook(file_path)

    def load_income_statements(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Load current and prior income statements.
        """

        return {
            "current": self.load_statement(
                "income_statement",
                "current",
            ),
            "prior": self.load_statement(
                "income_statement",
                "prior",
            ),
        }

    def discover_source_files(self) -> Dict[str, list[str]]:
        """
        Discover available Excel files instead of hard-coding
        the complete list of source files.
        """

        return {
            "current": sorted(
                file.name
                for file in self.current_dir.glob("*.xlsx")
            ),
            "prior": sorted(
                file.name
                for file in self.prior_dir.glob("*.xlsx")
            ),
        }