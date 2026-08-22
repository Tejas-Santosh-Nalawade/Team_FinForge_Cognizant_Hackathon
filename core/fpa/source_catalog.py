from core.fpa.source_registry import SourceRegistry


def build_source_catalog() -> SourceRegistry:
    """
    Build the source-category registry.

    Only source metadata is defined here.
    Financial values are never stored here.
    """

    registry = SourceRegistry()

    registry.register(
        source_id="financial_actuals",
        source_category="historical_financials",
        description="Historical financial statements and supporting schedules.",
        authority_level="company_source",
        required=True,
    )

    registry.register(
        source_id="annual_operating_budget",
        source_category="AOB",
        description="Annual Operating Budget.",
        authority_level="management_approved",
        required=False,
    )

    registry.register(
        source_id="rolling_forecast_4q",
        source_category="4Q_rolling_forecast",
        description="Four-quarter rolling forecast.",
        authority_level="management_approved",
        required=False,
    )

    registry.register(
        source_id="rolling_forecast_8q",
        source_category="8Q_rolling_forecast",
        description="Eight-quarter rolling forecast.",
        authority_level="management_approved",
        required=False,
    )

    registry.register(
        source_id="operational_drivers",
        source_category="operational_drivers",
        description="Operational volume and headcount assumptions.",
        authority_level="management_approved",
        required=False,
    )

    registry.register(
        source_id="us_gaap",
        source_category="US_GAAP",
        description="US GAAP / ASC authoritative literature.",
        authority_level="authoritative",
        required=False,
    )

    registry.register(
        source_id="ifrs",
        source_category="IFRS",
        description="IFRS Accounting Standards and related authoritative material.",
        authority_level="authoritative",
        required=False,
    )

    registry.register(
        source_id="credit_risk_directives",
        source_category="credit_risk",
        description="Applicable bank credit-risk regulatory directives.",
        authority_level="regulatory",
        required=False,
    )

    registry.register(
        source_id="prior_mdna",
        source_category="MD&A",
        description="Prior-period management discussion and analysis.",
        authority_level="company_source",
        required=False,
    )

    registry.register(
        source_id="board_memos",
        source_category="board_oversight",
        description="Board oversight and governance memoranda.",
        authority_level="company_source",
        required=False,
    )

    return registry