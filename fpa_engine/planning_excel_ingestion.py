from pathlib import Path
from typing import Dict

import pandas as pd

from FPA_ENGINE.planning_schema import (
    PlanningInput,
    validate_planning_input,
)


class PlanningExcelIngestion:
    """
    Ingests forward-looking FP&A inputs from Excel workbooks.

    Supported source categories:
        - AOB
        - 4Q_rolling_forecast
        - 8Q_rolling_forecast
        - operational_drivers

    Responsibilities:
        - discover user-provided Excel workbooks
        - read Excel worksheets
        - inspect workbook structure
        - extract planning inputs
        - preserve values supplied by Excel
        - record workbook and worksheet provenance
        - validate structured PlanningInput records

    This class:
        - does NOT generate financial values
        - does NOT hard-code planning values
        - does NOT convert Excel to JSON
    """

    SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}

    def __init__(self, input_dir: str | Path):
        self.input_dir = Path(input_dir)

        if not self.input_dir.exists():
            raise FileNotFoundError(
                f"Planning input directory does not exist: {self.input_dir}"
            )

    # =========================================================
    # WORKBOOK DISCOVERY
    # =========================================================

    def discover_workbooks(self) -> list[Path]:
        """Discover all Excel workbooks supplied by the user."""

        return sorted(
            file
            for file in self.input_dir.rglob("*")
            if file.is_file()
            and file.suffix.lower() in self.SUPPORTED_EXTENSIONS
        )

    # =========================================================
    # WORKBOOK READING
    # =========================================================

    def read_workbook(
        self,
        file_path: str | Path,
    ) -> Dict[str, pd.DataFrame]:
        """Read every worksheet from an Excel workbook."""

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Planning workbook does not exist: {file_path}"
            )

        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported Excel file type: {file_path.suffix}"
            )

        return pd.read_excel(
            file_path,
            sheet_name=None,
            header=None,
        )

    # =========================================================
    # STRUCTURED INPUT CREATION
    # =========================================================

    def create_planning_input(
        self,
        source_category: str,
        period: str,
        metric: str,
        value: float | None,
        unit: str,
        source_file: str | Path,
        source_sheet: str,
        source_type: str,
        method: str,
        status: str,
    ) -> PlanningInput:

        planning_input = PlanningInput(
            source_category=source_category,
            period=str(period),
            metric=str(metric),
            value=value,
            unit=str(unit),
            source_file=str(source_file),
            source_sheet=str(source_sheet),
            source_type=str(source_type),
            method=str(method),
            status=str(status),
        )

        validate_planning_input(planning_input)

        return planning_input

    # =========================================================
    # HEADER DETECTION
    # =========================================================

    @staticmethod
    def _normalise_header(value) -> str:
        """Normalize an Excel cell for header comparison."""

        if pd.isna(value):
            return ""

        return str(value).strip().lower()

    @classmethod
    def _get_header_map(
        cls,
        dataframe: pd.DataFrame,
    ) -> tuple[int, dict[str, int]]:

        """
        Find the actual header row and map column names to positions.

        This does NOT assume that Period is column 0.

        For example, all of these are supported:

            Period | Metric | Value | Unit

        or:

            Company | Period | Metric | Value | Unit
        """

        for row_index in range(len(dataframe)):

            row = dataframe.iloc[row_index]

            headers = {
                cls._normalise_header(value): column_index
                for column_index, value in enumerate(row)
                if cls._normalise_header(value)
            }

            # A valid planning worksheet must contain
            # at least Metric and Value columns.
            if "metric" in headers and "value" in headers:
                return row_index, headers

            if "driver" in headers and "value" in headers:
                return row_index, headers

        raise ValueError(
            "Could not identify a valid planning worksheet header. "
            "Expected columns containing Metric/Value or Driver/Value."
        )

    @staticmethod
    def _safe_float(value) -> float | None:
        """
        Convert a source value to float.

        Blank cells remain None.

        No financial value is generated.
        """

        if pd.isna(value):
            return None

        if isinstance(value, str):

            value = value.strip()

            if not value:
                return None

        try:
            return float(value)

        except (TypeError, ValueError) as exc:

            raise ValueError(
                f"Expected a numeric planning value but found: {value!r}"
            ) from exc

    # =========================================================
    # COMMON EXTRACTION LOGIC
    # =========================================================

    def _extract_tabular_inputs(
        self,
        file_path: str | Path,
        sheet_name: str,
        source_category: str,
        metric_column_name: str = "metric",
    ) -> list[PlanningInput]:

        sheets = self.read_workbook(file_path)

        if sheet_name not in sheets:
            raise ValueError(
                f"{sheet_name} worksheet not found in planning workbook."
            )

        dataframe = sheets[sheet_name]

        header_row_index, header_map = self._get_header_map(
            dataframe
        )

        # Required columns
        if "period" not in header_map:
            raise ValueError(
                f"{sheet_name} worksheet must contain a Period column."
            )

        if "value" not in header_map:
            raise ValueError(
                f"{sheet_name} worksheet must contain a Value column."
            )

        if metric_column_name not in header_map:
            raise ValueError(
                f"{sheet_name} worksheet must contain "
                f"a {metric_column_name.title()} column."
            )

        period_column = header_map["period"]
        metric_column = header_map[metric_column_name]
        value_column = header_map["value"]

        unit_column = header_map.get("unit")
        source_type_column = header_map.get("source type")

        inputs = []

        # Start AFTER the header row.
        for row_index in range(
            header_row_index + 1,
            len(dataframe),
        ):

            row = dataframe.iloc[row_index]

            # -------------------------------------------------
            # Skip completely blank rows
            # -------------------------------------------------

            if row.isna().all():
                continue

            # -------------------------------------------------
            # Period
            # -------------------------------------------------

            if pd.isna(row.iloc[period_column]):
                continue

            period = str(
                row.iloc[period_column]
            ).strip()

            # -------------------------------------------------
            # Metric / Driver
            # -------------------------------------------------

            if pd.isna(row.iloc[metric_column]):
                continue

            metric = str(
                row.iloc[metric_column]
            ).strip()

            # -------------------------------------------------
            # Value
            # -------------------------------------------------

            value = self._safe_float(
                row.iloc[value_column]
            )

            # -------------------------------------------------
            # Unit
            # -------------------------------------------------

            if unit_column is None:

                unit = "not_specified"

            elif pd.isna(row.iloc[unit_column]):

                unit = "not_specified"

            else:

                unit = str(
                    row.iloc[unit_column]
                ).strip()

            # -------------------------------------------------
            # Source Type
            # -------------------------------------------------

            if source_type_column is None:

                source_type = "management_approved"

            elif pd.isna(row.iloc[source_type_column]):

                source_type = "management_approved"

            else:

                source_type = str(
                    row.iloc[source_type_column]
                ).strip()

            planning_input = self.create_planning_input(
                source_category=source_category,
                period=period,
                metric=metric,
                value=value,
                unit=unit,
                source_file=file_path,
                source_sheet=sheet_name,
                source_type=source_type,
                method="direct_source_ingestion",
                status=(
                    "available"
                    if value is not None
                    else "pending"
                ),
            )

            inputs.append(planning_input)

        return inputs

    # =========================================================
    # WORKBOOK INSPECTION
    # =========================================================

    def inspect_workbook(
        self,
        file_path: str | Path,
    ) -> pd.DataFrame:

        file_path = Path(file_path)

        sheets = self.read_workbook(file_path)

        records = []

        for sheet_name, dataframe in sheets.items():

            records.append(
                {
                    "source_file": str(file_path),
                    "source_sheet": str(sheet_name),
                    "rows": int(dataframe.shape[0]),
                    "columns": int(dataframe.shape[1]),
                    "status": "discovered",
                }
            )

        return pd.DataFrame(records)

    def inspect_all_workbooks(self) -> pd.DataFrame:

        records = []

        for file_path in self.discover_workbooks():

            inspection = self.inspect_workbook(
                file_path
            )

            records.append(inspection)

        if not records:

            return pd.DataFrame(
                columns=[
                    "source_file",
                    "source_sheet",
                    "rows",
                    "columns",
                    "status",
                ]
            )

        return pd.concat(
            records,
            ignore_index=True,
        )

    # =========================================================
    # AOB
    # =========================================================

    def extract_aob_inputs(
        self,
        file_path: str | Path,
    ) -> list[PlanningInput]:

        return self._extract_tabular_inputs(
            file_path=file_path,
            sheet_name="AOB",
            source_category="AOB",
            metric_column_name="metric",
        )

    # =========================================================
    # 4Q FORECAST
    # =========================================================

    def extract_4q_forecast_inputs(
        self,
        file_path: str | Path,
    ) -> list[PlanningInput]:

        return self._extract_tabular_inputs(
            file_path=file_path,
            sheet_name="4Q_Forecast",
            source_category="4Q_rolling_forecast",
            metric_column_name="metric",
        )

    # =========================================================
    # 8Q FORECAST
    # =========================================================

    def extract_8q_forecast_inputs(
        self,
        file_path: str | Path,
    ) -> list[PlanningInput]:

        return self._extract_tabular_inputs(
            file_path=file_path,
            sheet_name="8Q_Forecast",
            source_category="8Q_rolling_forecast",
            metric_column_name="metric",
        )

    # =========================================================
    # OPERATIONAL DRIVERS
    # =========================================================

    def extract_operational_driver_inputs(
        self,
        file_path: str | Path,
    ) -> list[PlanningInput]:

        return self._extract_tabular_inputs(
            file_path=file_path,
            sheet_name="Operational_Drivers",
            source_category="operational_drivers",
            metric_column_name="driver",
        )

    # =========================================================
    # COMPLETE EXTRACTION
    # =========================================================

    def extract_all_planning_inputs(
        self,
        file_path: str | Path,
    ) -> list[PlanningInput]:

        inputs = []

        inputs.extend(
            self.extract_aob_inputs(file_path)
        )

        inputs.extend(
            self.extract_4q_forecast_inputs(file_path)
        )

        inputs.extend(
            self.extract_8q_forecast_inputs(file_path)
        )

        inputs.extend(
            self.extract_operational_driver_inputs(
                file_path
            )
        )

        return inputs