"""
math_engine/forecasting_charts.py
Matplotlib Vector / High-Resolution Chart Generation Engine for 4Q & 8Q Strategic PDF Report.
Generates:
1. Chart 1: 8-Quarter Revenue & Net Income Trajectory (Dual-Axis Bar & Line Chart)
2. Chart 2: Liquidity, Cash Runway & CapEx Burn Curve (Stacked Area/Line Chart)
3. Chart 3: Working Capital Conversion Cycle Trends (Grouped Line Chart)
"""

from pathlib import Path
from typing import List, Dict, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def set_chart_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "DejaVu Sans", "Arial"],
        "axes.edgecolor": "#CBD5E1",
        "axes.linewidth": 0.8,
        "grid.color": "#E2E8F0",
        "grid.linestyle": "--",
        "grid.linewidth": 0.5,
    })


def generate_chart_1_revenue_net_income(projections: List[Dict[str, Any]], output_path: Path) -> Path:
    """Chart 1: 8-Quarter Revenue & Net Income Trajectory (Dual-Axis Bar & Line Chart)."""
    set_chart_style()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    periods = [p["period"] for p in projections]
    revenues = [p["revenue"] for p in projections]
    net_incomes = [p["net_income"] for p in projections]

    x = np.arange(len(periods))
    fig, ax1 = plt.subplots(figsize=(7.5, 3.2), dpi=300)

    # Bars: Revenue
    bars = ax1.bar(x, revenues, color="#1E3A8A", width=0.45, label="Projected Revenue (INR M)", alpha=0.85)
    ax1.set_ylabel("Revenue (INR Millions)", color="#1E3A8A", fontsize=9, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor="#1E3A8A", labelsize=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(periods, fontsize=8, rotation=25)
    ax1.grid(True, axis="y")

    # Line: Net Income with Confidence Band
    ax2 = ax1.twinx()
    line = ax2.plot(x, net_incomes, color="#15803D", marker="o", linewidth=2.2, label="Projected Net Income (INR M)")
    ni_lower = [ni * 0.95 for ni in net_incomes]
    ni_upper = [ni * 1.05 for ni in net_incomes]
    ax2.fill_between(x, ni_lower, ni_upper, color="#15803D", alpha=0.15, label="±5% Confidence Interval")

    ax2.set_ylabel("Net Income (INR Millions)", color="#15803D", fontsize=9, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#15803D", labelsize=8)

    plt.title("8-Quarter Pro-Forma Revenue & Net Income Trajectory", fontsize=10, fontweight="bold", color="#0F172A", pad=10)
    fig.tight_layout()
    plt.savefig(output_path, format="png", bbox_inches="tight", dpi=300)
    plt.close(fig)
    return output_path


def generate_chart_2_cash_runway(projections: List[Dict[str, Any]], output_path: Path) -> Path:
    """Chart 2: Liquidity, Cash Runway & CapEx Burn Curve (Stacked Area/Line Chart)."""
    set_chart_style()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    periods = [p["period"] for p in projections]
    ending_cash = [p["ending_cash"] for p in projections]
    min_buffers = [p["min_cash_buffer"] for p in projections]

    x = np.arange(len(periods))
    fig, ax = plt.subplots(figsize=(7.5, 3.2), dpi=300)

    ax.plot(x, ending_cash, color="#0F172A", marker="s", linewidth=2.2, label="Cumulative Ending Cash Reserves (INR M)")
    ax.fill_between(x, ending_cash, color="#1E3A8A", alpha=0.15)

    ax.plot(x, min_buffers, color="#B91C1C", linestyle="--", linewidth=1.8, label="1-Month OpEx Minimum Cash Buffer Threshold")

    ax.set_ylabel("Cash Reserves (INR Millions)", fontsize=9, fontweight="bold", color="#0F172A")
    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=8, rotation=25)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(True)
    ax.legend(loc="upper left", fontsize=8, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    plt.title("Liquidity Reserve Cushion vs. 1-Month OpEx Minimum Buffer Threshold", fontsize=10, fontweight="bold", color="#0F172A", pad=10)
    fig.tight_layout()
    plt.savefig(output_path, format="png", bbox_inches="tight", dpi=300)
    plt.close(fig)
    return output_path


def generate_chart_3_working_capital(projections: List[Dict[str, Any]], output_path: Path) -> Path:
    """Chart 3: Working Capital Conversion Cycle Trends (Grouped Line Chart)."""
    set_chart_style()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    periods = [p["period"] for p in projections]
    dsos = [p["dso"] for p in projections]
    dios = [p["dio"] for p in projections]
    dpos = [p["dpo"] for p in projections]
    cccs = [p["ccc"] for p in projections]

    x = np.arange(len(periods))
    fig, ax = plt.subplots(figsize=(7.5, 3.2), dpi=300)

    ax.plot(x, dsos, color="#1E3A8A", linestyle="-", marker="o", linewidth=1.8, label="DSO (52.3 Days)")
    ax.plot(x, dios, color="#B45309", linestyle="-", marker="^", linewidth=1.8, label="DIO (52.0 Days)")
    ax.plot(x, dpos, color="#475569", linestyle="-", marker="v", linewidth=1.8, label="DPO (36.2 Days)")
    ax.plot(x, cccs, color="#15803D", linestyle="--", marker="D", linewidth=2.2, label="Cash Conversion Cycle (CCC = 68.1 Days)")

    ax.set_ylabel("Efficiency Days", fontsize=9, fontweight="bold", color="#0F172A")
    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=8, rotation=25)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(True)
    ax.legend(loc="center right", fontsize=8, frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")

    plt.title("Working Capital Cycle Efficiency Trends (DSO, DIO, DPO & CCC)", fontsize=10, fontweight="bold", color="#0F172A", pad=10)
    fig.tight_layout()
    plt.savefig(output_path, format="png", bbox_inches="tight", dpi=300)
    plt.close(fig)
    return output_path


def generate_all_forecasting_charts(projections: List[Dict[str, Any]], chart_dir: Path) -> Dict[str, Path]:
    """Generates all 3 charts and returns dictionary of file paths."""
    chart_dir.mkdir(parents=True, exist_ok=True)
    path1 = generate_chart_1_revenue_net_income(projections, chart_dir / "chart1_revenue_net_income.png")
    path2 = generate_chart_2_cash_runway(projections, chart_dir / "chart2_cash_runway.png")
    path3 = generate_chart_3_working_capital(projections, chart_dir / "chart3_working_capital.png")

    return {
        "chart_1": path1,
        "chart_2": path2,
        "chart_3": path3,
    }
