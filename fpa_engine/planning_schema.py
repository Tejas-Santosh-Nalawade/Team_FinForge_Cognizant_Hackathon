from dataclasses import dataclass
from typing import Optional


PLANNING_SOURCE_CATEGORIES = {
    "AOB",
    "4Q_rolling_forecast",
    "8Q_rolling_forecast",
    "operational_drivers",
}


@dataclass(frozen=True)
class PlanningInput:
    """
    Standard representation of one forward-looking FP&A input.

    The schema is fixed.
    The actual period, metric, value and source information
    come from the user's Excel workbook.
    """

    source_category: str
    period: str
    metric: str
    value: Optional[float]
    unit: str
    source_file: str
    source_sheet: str
    source_type: str
    method: str
    status: str


def validate_source_category(source_category: str) -> None:
    """
    Validate that the source belongs to a supported
    forward-looking FP&A category.
    """

    if source_category not in PLANNING_SOURCE_CATEGORIES:
        raise ValueError(
            f"Unsupported planning source category: "
            f"{source_category}. "
            f"Expected one of: "
            f"{sorted(PLANNING_SOURCE_CATEGORIES)}"
        )


def validate_planning_input(input_record: PlanningInput) -> None:
    """
    Validate one structured planning input.
    """

    validate_source_category(
        input_record.source_category
    )

    if not input_record.period:
        raise ValueError(
            "Planning input period cannot be empty."
        )

    if not input_record.metric:
        raise ValueError(
            "Planning input metric cannot be empty."
        )

    if not input_record.source_file:
        raise ValueError(
            "Planning input source_file cannot be empty."
        )

    if not input_record.source_sheet:
        raise ValueError(
            "Planning input source_sheet cannot be empty."
        )

    if not input_record.status:
        raise ValueError(
            "Planning input status cannot be empty."
        )