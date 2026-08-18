from FPA_ENGINE.forecast_policy import ForecastPolicy
from FPA_ENGINE.planning_excel_ingestion import PlanningExcelIngestion


def build_current_planning_input_status(
    dataset_dir: str = "DATASET",
    data_version: str = "True_data",
) -> ForecastPolicy:
    """
    Read forward-looking FP&A planning inputs from the
    supplied Excel workbook and register them in ForecastPolicy.

    Values are taken directly from the planning Excel workbook.
    No financial values are generated or modified.

    Flow:

        Excel workbook
            ↓
        PlanningExcelIngestion
            ↓
        PlanningInput records
            ↓
        ForecastPolicy
    """

    planning_input_dir = (
        f"{dataset_dir}/{data_version}/planning_inputs"
    )

    workbook_path = (
        f"{planning_input_dir}/planning_inputs.xlsx"
    )

    ingestion = PlanningExcelIngestion(
        planning_input_dir
    )

    planning_inputs = ingestion.extract_all_planning_inputs(
        workbook_path
    )

    policy = ForecastPolicy()

    for planning_input in planning_inputs:

        if planning_input.value is not None:

            policy.register_source_input(
                metric=planning_input.metric,
                period=planning_input.period,
                value=planning_input.value,
                unit=planning_input.unit,
                source=planning_input.source_file,
                source_type=planning_input.source_type,
                method=planning_input.method,
            )

        else:

            policy.register_missing_input(
                metric=planning_input.metric,
                period=planning_input.period,
                unit=planning_input.unit,
            )

    return policy