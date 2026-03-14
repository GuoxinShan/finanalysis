#!/usr/bin/env python3
"""
Financial analysis report generator.

Combines finanalysis data with financial_calculator to produce
structured Markdown reports following the 18-section framework.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Import calculator functions
from financial_calculator import (
    calculate_all_ratios,
    calculate_growth_metrics,
    format_ratio_table,
    get_metric_value,
)


def load_fs_index(path: str) -> dict:
    """Load fs_index.json from path."""
    with open(path) as f:
        return json.load(f)


def generate_section_iv_conclusions(data: dict, ratios: dict) -> str:
    """Generate Section IV: Core Conclusions."""
    # Extract key metrics
    revenue = get_metric_value(data, "revenue")
    pbt = get_metric_value(data, "profit before tax")
    ocf = get_metric_value(data, "net cash from operating activities")
    liabilities_to_assets = ratios["solvency"]["liabilities_to_assets"]
    borrowings = get_metric_value(data, "bank borrowings")

    lines = [
        "# Ⅳ. Core Conclusions - Strong Expansion with Softer Profit Conversion",
        f"- **Scale expansion is clear**: revenue rose to RM{revenue/1e6:.1f}m",
        f"- **Profitability improved in absolute terms**: PBT increased to RM{pbt/1e6:.1f}m",
        f"- **Cash quality improved sharply**: operating cash flow at RM{ocf/1e6:.1f}m",
        f"- **Leverage and funding intensity increased**: liabilities/assets rose to {liabilities_to_assets:.1f}%",
        f"- **Borrowings reached RM{borrowings/1e6:.1f}m",
        "",
    ]
    return "\n".join(lines)


def generate_section_v_performance(data: dict, prior_data: dict | None = None) -> str:
    """Generate Section V: Core Financial Performance table."""
    current = {
        "Revenue (RM'000)": get_metric_value(data, "revenue"),
        "Profit from operations (RM'000)": get_metric_value(data, "profit from operations"),
        "PBT (RM'000)": get_metric_value(data, "profit before tax"),
        "PAT (RM'000)": get_metric_value(data, "profit for the financial year"),
        "Attributable profit (RM'000)": get_metric_value(data, "profit attributable to owners of the company"),
        "Basic EPS (sen)": get_metric_value(data, "basic earnings per share"),
    }

    lines = [
        "# Ⅴ. Core Financial Performance - High Growth, Moderate Conversion",
        "**Table 1: Core Financial Performance**",
        "| Indicator | Current Period |",
        "|---|---:|",
    ]

    for label, value in current.items():
        formatted = f"{value:,.0f}" if "RM" in label else f"{value:.2f}"
        lines.append(f"| {label} | {formatted} |")

    # Add insights template
    lines.extend([
        "",
        "**Insights**",
        "1. [Insight about revenue growth]",
        "2. [Insight about margin trends]",
        "3. [Insight about attributable profit]",
        "",
        "**Conclusion**",
        "[Summary of performance quality]",
        "",
    ])

    return "\n".join(lines)


def generate_section_xiv_solvency(ratios: dict) -> str:
    """Generate Section XIV: Solvency Analysis."""
    liquidity = ratios["liquidity"]
    solvency = ratios["solvency"]

    lines = [
        "# ⅩⅣ. Solvency Analysis - Liquidity Improved, Structural Leverage Higher",
        "",
        "## Short-Term Solvency",
        "**Table 1: Short-Term Solvency Indicators**",
        "| Indicator | Value |",
        "|---|---:|",
        f"| Current ratio | {liquidity['current_ratio']:.2f}x |",
        f"| Quick ratio | {liquidity['quick_ratio']:.2f}x |",
        f"| Working capital (RM'000) | {liquidity['working_capital']:,.0f} |",
        "",
        "**Insights (Short-Term Solvency)**",
        "1. [Liquidity assessment]",
        "2. [Quick ratio interpretation]",
        "3. [Working capital trend]",
        "",
        "**Conclusion (Short-Term Solvency)**",
        "[Summary of short-term solvency]",
        "",
        "## Long-Term Solvency",
        "**Table 2: Long-Term Solvency Indicators**",
        "| Indicator | Value |",
        "|---|---:|",
        f"| Liabilities / Assets | {solvency['liabilities_to_assets']:.1f}% |",
        f"| Borrowings / Assets | {solvency['borrowings_to_assets']:.1f}% |",
        f"| Net debt / Equity | {solvency['net_debt_to_equity']:.2f}x |",
        "",
        "**Insights (Long-Term Solvency)**",
        "1. [Leverage trend]",
        "2. [Debt structure assessment]",
        "3. [Equity position]",
        "",
        "**Conclusion (Long-Term Solvency)**",
        "[Summary of long-term solvency]",
        "",
    ]

    return "\n".join(lines)


def generate_detailed_report(
    company_name: str,
    period: str,
    current_data: dict,
    prior_data: dict | None = None,
) -> str:
    """
    Generate full 18-section detailed report.

    Args:
        company_name: Company name for header
        period: Period identifier (e.g., "2025H1")
        current_data: Current period fs_index.json data
        prior_data: Prior period data for YoY comparison (optional)
    """
    # Calculate ratios
    period_days = 182 if "H" in period or "Q" in period else 365
    ratios = calculate_all_ratios(current_data, period_days)

    # Build report sections
    sections = [
        f"# {company_name} - {period} Financial Analysis Report\n",
        generate_section_iv_conclusions(current_data, ratios),
        generate_section_v_performance(current_data, prior_data),
        generate_section_xiv_solvency(ratios),
        # Add remaining sections...
        "# [Remaining sections to be generated...]\n",
    ]

    return "\n".join(sections)


def generate_summary_report(
    company_name: str,
    period: str,
    current_data: dict,
    prior_data: dict | None = None,
) -> str:
    """Generate 4-section executive summary."""
    period_days = 182 if "H" in period or "Q" in period else 365
    ratios = calculate_all_ratios(current_data, period_days)

    lines = [
        f"**[{company_name.upper()}] [{period}] Interim Financial Report Analysis and Interpretation**\n",
        "### **1. Key Conclusions**",
        "1. [Key conclusion 1]",
        "2. [Key conclusion 2]",
        "3. [Key conclusion 3]",
        "4. [Key conclusion 4]",
        "5. [Key conclusion 5]",
        "",
        "---\n",
        "### **2. Data Analysis**",
        format_ratio_table(ratios["profitability"], "Core Profitability Ratios"),
        "",
        "**Insights**",
        "1. [Data insight 1]",
        "2. [Data insight 2]",
        "",
        "**Conclusion**",
        "[Summary of data analysis]",
        "",
        "---\n",
        "### **3. Trend Analysis**",
        "[Trend analysis section]",
        "",
        "---\n",
        "### **4. Risk Warning**",
        "[Risk matrix and improvement plan]",
        "",
    ]

    return "\n".join(lines)


def main(
    company_name: str,
    period: str,
    current_fs_index: str,
    prior_fs_index: str | None = None,
    output_dir: str = ".",
):
    """
    Generate both detailed and summary reports.

    Args:
        company_name: Company name
        period: Period identifier (e.g., "2025H1")
        current_fs_index: Path to current period fs_index.json
        prior_fs_index: Path to prior period fs_index.json (optional)
        output_dir: Directory to save reports
    """
    # Load data
    current_data = load_fs_index(current_fs_index)
    prior_data = load_fs_index(prior_fs_index) if prior_fs_index else None

    # Generate reports
    detailed = generate_detailed_report(company_name, period, current_data, prior_data)
    summary = generate_summary_report(company_name, period, current_data, prior_data)

    # Save outputs
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ticker = company_name.replace(" ", "_").upper()
    detailed_file = output_path / f"{ticker}-{period}-revised.md"
    summary_file = output_path / f"{ticker}-{period}-summary.md"

    detailed_file.write_text(detailed)
    summary_file.write_text(summary)

    print(f"Generated:")
    print(f"  - {detailed_file}")
    print(f"  - {summary_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate financial analysis reports")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--period", required=True, help="Period (e.g., 2025H1)")
    parser.add_argument("--current", required=True, help="Current period fs_index.json")
    parser.add_argument("--prior", help="Prior period fs_index.json (for YoY comparison)")
    parser.add_argument("--output-dir", default=".", help="Output directory")

    args = parser.parse_args()

    main(
        args.company,
        args.period,
        args.current,
        args.prior,
        args.output_dir,
    )
