from pathlib import Path
import random
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

OUTPUT_DIR = Path("DATASET/True_data/planning_inputs")
OUTPUT_FILE = OUTPUT_DIR / "planning_inputs.xlsx"

COMPANY = "AsterNova Technologies Ltd."
CURRENCY = "₹ million"


# ============================================================
# HISTORICAL BASELINE
# Taken from the existing AsterNova current-year dataset
# ============================================================

HISTORICAL_REVENUE = 1354.66
HISTORICAL_COGS = 532.49
HISTORICAL_SGA = 379.27
HISTORICAL_RD = 127.30
HISTORICAL_DA = 28.45


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(SEED)


# ============================================================
# HELPER
# ============================================================

def round2(value):
    return round(float(value), 2)


# ============================================================
# AOB GENERATION
# ============================================================

def generate_aob():
    """
    Generate an Annual Operating Budget based on the
    existing historical financial baseline.

    These are MOCK management-planning values for testing.
    """

    revenue_growth = 0.08

    aob_revenue = HISTORICAL_REVENUE * (1 + revenue_growth)

    cogs_ratio = HISTORICAL_COGS / HISTORICAL_REVENUE
    sga_ratio = HISTORICAL_SGA / HISTORICAL_REVENUE
    rd_ratio = HISTORICAL_RD / HISTORICAL_REVENUE
    da_ratio = HISTORICAL_DA / HISTORICAL_REVENUE

    aob_cogs = aob_revenue * cogs_ratio
    aob_sga = aob_revenue * sga_ratio
    aob_rd = aob_revenue * rd_ratio
    aob_da = aob_revenue * da_ratio

    operating_expenses = aob_sga + aob_rd + aob_da

    return pd.DataFrame([
        [COMPANY, "FY2026", "Revenue", round2(aob_revenue), CURRENCY],
        [COMPANY, "FY2026", "COGS", round2(aob_cogs), CURRENCY],
        [COMPANY, "FY2026", "Selling, General & Administrative",
         round2(aob_sga), CURRENCY],
        [COMPANY, "FY2026", "Research & Development",
         round2(aob_rd), CURRENCY],
        [COMPANY, "FY2026", "Depreciation & Amortization",
         round2(aob_da), CURRENCY],
        [COMPANY, "FY2026", "Operating Expenses",
         round2(operating_expenses), CURRENCY],
        [COMPANY, "FY2026", "Headcount", 520, "employees"],
        [COMPANY, "FY2026", "Operating Volume", 108000, "units"],
    ], columns=[
        "Company",
        "Period",
        "Metric",
        "Value",
        "Unit",
    ])


# ============================================================
# 4Q ROLLING FORECAST
# ============================================================

def generate_4q_forecast():
    """
    Four-quarter rolling revenue forecast.

    The annual forecast is derived from the AOB revenue,
    then distributed across quarters.
    """

    aob = generate_aob()

    annual_revenue = float(
        aob.loc[
            aob["Metric"] == "Revenue",
            "Value"
        ].iloc[0]
    )

    quarterly_weights = [
        0.24,
        0.25,
        0.25,
        0.26,
    ]

    records = []

    for quarter, weight in enumerate(
        quarterly_weights,
        start=1
    ):
        records.append([
            COMPANY,
            f"FY2026-Q{quarter}",
            "Revenue",
            round2(annual_revenue * weight),
            CURRENCY,
        ])

    return pd.DataFrame(
        records,
        columns=[
            "Company",
            "Period",
            "Metric",
            "Value",
            "Unit",
        ],
    )


# ============================================================
# 8Q ROLLING FORECAST
# ============================================================

def generate_8q_forecast():
    """
    Eight-quarter rolling revenue forecast.

    FY2026 quarters are based on the AOB.
    FY2027 quarters use a modest growth assumption.
    """

    aob = generate_aob()

    annual_revenue = float(
        aob.loc[
            aob["Metric"] == "Revenue",
            "Value"
        ].iloc[0]
    )

    q_weights = [
        0.24,
        0.25,
        0.25,
        0.26,
    ]

    records = []

    # FY2026
    for quarter, weight in enumerate(
        q_weights,
        start=1
    ):
        records.append([
            COMPANY,
            f"FY2026-Q{quarter}",
            "Revenue",
            round2(annual_revenue * weight),
            CURRENCY,
        ])

    # FY2027
    fy2027_growth = 0.07
    fy2027_revenue = annual_revenue * (
        1 + fy2027_growth
    )

    for quarter, weight in enumerate(
        q_weights,
        start=1
    ):
        records.append([
            COMPANY,
            f"FY2027-Q{quarter}",
            "Revenue",
            round2(fy2027_revenue * weight),
            CURRENCY,
        ])

    return pd.DataFrame(
        records,
        columns=[
            "Company",
            "Period",
            "Metric",
            "Value",
            "Unit",
        ],
    )


# ============================================================
# OPERATIONAL DRIVERS
# ============================================================

def generate_operational_drivers():
    """
    Generate mock operational planning assumptions.

    Headcount and operating volume are explicitly separated
    from financial statement values.
    """

    records = [
        [
            COMPANY,
            "FY2026",
            "Headcount",
            520,
            "employees",
        ],
        [
            COMPANY,
            "FY2026",
            "Operating Volume",
            108000,
            "units",
        ],
        [
            COMPANY,
            "FY2027",
            "Headcount",
            550,
            "employees",
        ],
        [
            COMPANY,
            "FY2027",
            "Operating Volume",
            116000,
            "units",
        ],
    ]

    return pd.DataFrame(
        records,
        columns=[
            "Company",
            "Period",
            "Driver",
            "Value",
            "Unit",
        ],
    )


# ============================================================
# WRITE EXCEL
# ============================================================

def generate_planning_excel():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    aob = generate_aob()
    forecast_4q = generate_4q_forecast()
    forecast_8q = generate_8q_forecast()
    operational = generate_operational_drivers()

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:

        aob.to_excel(
            writer,
            sheet_name="AOB",
            index=False,
        )

        forecast_4q.to_excel(
            writer,
            sheet_name="4Q_Forecast",
            index=False,
        )

        forecast_8q.to_excel(
            writer,
            sheet_name="8Q_Forecast",
            index=False,
        )

        operational.to_excel(
            writer,
            sheet_name="Operational_Drivers",
            index=False,
        )

    print("Planning Excel generated successfully.")
    print(f"Output: {OUTPUT_FILE}")
    print()
    print("Sheets created:")
    print("  - AOB")
    print("  - 4Q_Forecast")
    print("  - 8Q_Forecast")
    print("  - Operational_Drivers")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    generate_planning_excel()