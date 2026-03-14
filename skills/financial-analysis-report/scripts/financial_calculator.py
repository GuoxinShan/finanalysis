#!/usr/bin/env python3
"""
Financial ratio calculator for finanalysis data.

Reads fs_index.json and computes standard financial ratios.
Extensible via formula registry.
"""

import json
import sys
from pathlib import Path
from typing import Any, Callable


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value for zero denominator."""
    return numerator / denominator if denominator != 0 else default


def get_metric_value(data: dict, label: str, entity: str = "group", period: str = "current") -> float:
    """
    Extract metric value from fs_index.json structure.

    Args:
        data: fs_index.json loaded as dict
        label: Metric label (lowercase, e.g., "revenue")
        entity: "group" or "company"
        period: "current" or "prior"

    Returns:
        Float value (0.0 if not found)
    """
    try:
        line_items = data.get("line_items", {})

        # Try exact match first
        if label.lower() in line_items:
            item = line_items[label.lower()]
        else:
            # Fuzzy search for label
            item = None
            for key, value in line_items.items():
                if label.lower() in key.lower() or key.lower() in label.lower():
                    item = value
                    break

            if item is None:
                return 0.0

        # Extract value based on entity and period
        # Handle both "group_current" and "groupCurrent" style keys
        period_key = period.lower()
        entity_prefix = entity.lower()

        # Try different key formats
        for key_format in [
            f"{entity_prefix}_{period_key}",  # group_current
            f"{entity_prefix}{period_key.capitalize()}",  # groupCurrent
            f"{entity_prefix}_{period_key}",  # company_current
        ]:
            if key_format in item:
                val = item[key_format]
                return float(val) if val is not None else 0.0

        return 0.0

    except (KeyError, TypeError, ValueError, AttributeError):
        return 0.0


def get_total_borrowings(data: dict, entity: str = "group", period: str = "current") -> float:
    """Get total borrowings (current + non-current)."""
    # Try to get both current and non-current borrowings
    non_current = get_metric_value(data, "bank borrowings (non-current liabilities)", entity, period)
    current = get_metric_value(data, "bank borrowings (current liabilities)", entity, period)

    # Fallback: if specific labels don't work, try generic
    if non_current == 0.0 and current == 0.0:
        # Maybe there's only one "bank borrowings" that combines both
        return get_metric_value(data, "bank borrowings", entity, period)

    return non_current + current


def get_operating_expenses(data: dict, entity: str = "group", period: str = "current") -> float:
    """Get total operating expenses."""
    # Sum all operating expense categories
    cost_of_sales = get_metric_value(data, "cost of sales", entity, period)
    distribution = get_metric_value(data, "distribution expenses", entity, period)
    administrative = get_metric_value(data, "administrative expenses", entity, period)
    other = get_metric_value(data, "other expenses", entity, period)

    # If nothing found, try generic label
    if cost_of_sales == 0.0 and distribution == 0.0 and administrative == 0.0:
        return get_metric_value(data, "operating expenses", entity, period)

    return cost_of_sales + distribution + administrative + other


def calculate_profitability_ratios(data: dict) -> dict[str, float]:
    """Calculate profitability margins and returns."""
    revenue = get_metric_value(data, "revenue")
    operating_profit = get_metric_value(data, "gross profit")  # Use gross profit as proxy
    pbt = get_metric_value(data, "profit before tax")
    pat = get_metric_value(data, "profit for the financial year")
    attributable = get_metric_value(data, "profit for the financial year attributable to: owners of the parent")
    equity = get_metric_value(data, "equity attributable to owners of the parent")

    return {
        "operating_margin": safe_divide(operating_profit, revenue) * 100,
        "pbt_margin": safe_divide(pbt, revenue) * 100,
        "pat_margin": safe_divide(pat, revenue) * 100,
        "attributable_margin": safe_divide(attributable, revenue) * 100,
        "roe": safe_divide(attributable, equity) * 100,  # Simplified (should annualize)
    }


def calculate_liquidity_ratios(data: dict) -> dict[str, float]:
    """Calculate short-term solvency ratios."""
    current_assets = get_metric_value(data, "current assets")
    current_liabilities = get_metric_value(data, "current liabilities")
    inventories = get_metric_value(data, "inventories")
    cash = get_metric_value(data, "cash and bank balances")

    quick_assets = current_assets - inventories
    working_capital = current_assets - current_liabilities

    return {
        "current_ratio": safe_divide(current_assets, current_liabilities),
        "quick_ratio": safe_divide(quick_assets, current_liabilities),
        "working_capital": working_capital,
        "cash_to_current_assets": safe_divide(cash, current_assets) * 100,
    }


def calculate_solvency_ratios(data: dict) -> dict[str, float]:
    """Calculate long-term solvency ratios."""
    total_assets = get_metric_value(data, "total assets")
    total_liabilities = get_metric_value(data, "total liabilities")
    total_borrowings = get_total_borrowings(data)
    cash = get_metric_value(data, "cash and bank balances")
    equity = get_metric_value(data, "equity attributable to owners of the parent")

    # If equity not found, try total equity
    if equity == 0.0:
        equity = get_metric_value(data, "total equity")

    net_debt = total_borrowings - cash

    return {
        "liabilities_to_assets": safe_divide(total_liabilities, total_assets) * 100,
        "borrowings_to_assets": safe_divide(total_borrowings, total_assets) * 100,
        "net_debt_to_equity": safe_divide(net_debt, equity),
        "equity_to_assets": safe_divide(equity, total_assets) * 100,
    }


def calculate_efficiency_ratios(data: dict, period_days: int = 365) -> dict[str, float]:
    """
    Calculate operating efficiency ratios.

    Args:
        data: fs_index.json data
        period_days: Reporting period (365 for annual, 182 for H1)
    """
    revenue = get_metric_value(data, "revenue")
    operating_expenses = abs(get_operating_expenses(data))  # Use absolute value
    trade_receivables = get_metric_value(data, "trade receivables")
    trade_payables = get_metric_value(data, "trade payables")

    # Days calculations
    receivables_days = safe_divide(trade_receivables * period_days, revenue)
    payables_days = safe_divide(trade_payables * period_days, operating_expenses)

    return {
        "receivables_days": receivables_days,
        "payables_days": payables_days,
        "asset_turnover": safe_divide(revenue, get_metric_value(data, "total assets")),
    }


def calculate_cashflow_ratios(data: dict) -> dict[str, float]:
    """Calculate cash flow quality metrics."""
    revenue = get_metric_value(data, "revenue")
    ocf = get_metric_value(data, "net cash from operating activities")
    icf = get_metric_value(data, "net cash from investing activities")
    total_borrowings = get_total_borrowings(data)
    finance_costs = get_metric_value(data, "finance costs")

    # Approximate FCF (OCF - capex, where capex ≈ negative ICF)
    capex = -icf if icf < 0 else 0
    fcf = ocf - capex

    return {
        "ocf_to_revenue": safe_divide(ocf, revenue) * 100,
        "free_cash_flow": fcf,
        "ocf_interest_coverage": safe_divide(ocf, finance_costs),
        "ocf_to_debt": safe_divide(ocf, total_borrowings) * 100,
    }


def calculate_growth_metrics(current: dict, prior: dict) -> dict[str, float]:
    """
    Calculate YoY growth rates.

    Args:
        current: Current period fs_index.json data
        prior: Prior period fs_index.json data
    """
    metrics = [
        "revenue",
        "profit from operations",
        "profit before tax",
        "profit for the financial year",
        "profit attributable to owners of the company",
        "basic earnings per share",
        "total assets",
    ]

    growth = {}
    for metric in metrics:
        curr_val = get_metric_value(current, metric)
        prior_val = get_metric_value(prior, metric)

        if prior_val > 0:
            growth_rate = ((curr_val - prior_val) / prior_val) * 100
        else:
            growth_rate = 0.0

        # Clean metric name for key
        key = metric.replace(" ", "_") + "_growth"
        growth[key] = growth_rate

    return growth


def calculate_all_ratios(data: dict, period_days: int = 365) -> dict[str, dict[str, float]]:
    """
    Calculate all standard financial ratios.

    Returns:
        Dict with keys: profitability, liquidity, solvency, efficiency, cashflow
    """
    return {
        "profitability": calculate_profitability_ratios(data),
        "liquidity": calculate_liquidity_ratios(data),
        "solvency": calculate_solvency_ratios(data),
        "efficiency": calculate_efficiency_ratios(data, period_days),
        "cashflow": calculate_cashflow_ratios(data),
    }


def calculate_enhanced_growth_analysis(current: dict, prior: dict) -> dict[str, dict]:
    """
    Calculate YoY growth with enhanced analysis including absolute changes and insights.

    Args:
        current: Current period fs_index.json data
        prior: Prior period fs_index.json data

    Returns:
        Dict with growth rates, absolute changes, and significance flags
    """
    metrics = {
        "revenue": {"label": "Revenue", "unit": "RM'000"},
        "gross profit": {"label": "Gross Profit", "unit": "RM'000"},
        "profit before tax": {"label": "PBT", "unit": "RM'000"},
        "profit for the financial year": {"label": "PAT", "unit": "RM'000"},
        "profit for the financial year attributable to: owners of the parent": {
            "label": "Attributable Profit",
            "unit": "RM'000",
        },
        "basic earnings per share": {"label": "EPS", "unit": "sen"},
        "total assets": {"label": "Total Assets", "unit": "RM'000"},
        "equity attributable to owners of the parent": {"label": "Equity", "unit": "RM'000"},
    }

    growth_analysis = {}

    for metric_key, meta in metrics.items():
        curr_val = get_metric_value(current, metric_key)
        prior_val = get_metric_value(prior, metric_key)
        abs_change = curr_val - prior_val

        if prior_val > 0:
            growth_rate = (abs_change / prior_val) * 100
        else:
            growth_rate = 0.0

        # Flag significant changes (>15%)
        is_significant = abs(growth_rate) > 15.0

        growth_analysis[meta["label"]] = {
            "current": curr_val,
            "prior": prior_val,
            "absolute_change": abs_change,
            "growth_rate": growth_rate,
            "is_significant": is_significant,
            "unit": meta["unit"],
            "direction": "▲" if growth_rate > 0 else "▼" if growth_rate < 0 else "—",
        }

    return growth_analysis


def calculate_ratio_changes(current_ratios: dict, prior_ratios: dict) -> dict[str, dict]:
    """
    Calculate changes in financial ratios between periods.

    Args:
        current_ratios: Current period ratios (from calculate_all_ratios)
        prior_ratios: Prior period ratios

    Returns:
        Dict with ratio changes and significance flags
    """
    ratio_changes = {}

    for category in current_ratios.keys():
        ratio_changes[category] = {}

        for ratio_name, current_value in current_ratios[category].items():
            prior_value = prior_ratios[category].get(ratio_name, 0.0)
            abs_change = current_value - prior_value

            # For ratios, calculate percentage point change
            if "margin" in ratio_name or "to_assets" in ratio_name or "to_revenue" in ratio_name:
                change_metric = "pp"  # percentage points
                is_significant = abs(abs_change) > 2.0  # 2pp threshold
            elif "ratio" in ratio_name or "coverage" in ratio_name or "turnover" in ratio_name:
                change_metric = "x"  # times
                is_significant = abs(abs_change) > 0.2  # 0.2x threshold
            else:
                change_metric = "units"
                is_significant = abs(abs_change) > 5.0  # Generic threshold

            ratio_changes[category][ratio_name] = {
                "current": current_value,
                "prior": prior_value,
                "absolute_change": abs_change,
                "change_metric": change_metric,
                "is_significant": is_significant,
                "direction": "▲" if abs_change > 0 else "▼" if abs_change < 0 else "—",
            }

    return ratio_changes


def calculate_trend_analysis(datasets: list[tuple[str, dict]]) -> dict[str, dict]:
    """
    Analyze 3+ year trends for key metrics.

    Args:
        datasets: List of (period_label, fs_index_data) tuples in chronological order
                 e.g., [("2022", data_2022), ("2023", data_2023), ("2024", data_2024)]

    Returns:
        Dict with trend metrics: CAGR, volatility, direction
    """
    if len(datasets) < 2:
        return {"error": "Need at least 2 periods for trend analysis"}

    key_metrics = [
        "revenue",
        "profit before tax",
        "profit for the financial year",
        "total assets",
        "equity attributable to owners of the parent",
    ]

    trends = {}

    for metric in key_metrics:
        values = []
        periods = []

        for period_label, data in datasets:
            val = get_metric_value(data, metric)
            values.append(val)
            periods.append(period_label)

        # Calculate CAGR (Compound Annual Growth Rate)
        if len(values) >= 2 and values[0] > 0:
            years = len(values) - 1
            cagr = ((values[-1] / values[0]) ** (1 / years) - 1) * 100
        else:
            cagr = 0.0

        # Calculate volatility (standard deviation of year-over-year growth)
        if len(values) >= 3:
            yoy_growth = []
            for i in range(1, len(values)):
                if values[i - 1] > 0:
                    growth = ((values[i] - values[i - 1]) / values[i - 1]) * 100
                    yoy_growth.append(growth)

            if yoy_growth:
                mean_growth = sum(yoy_growth) / len(yoy_growth)
                variance = sum((x - mean_growth) ** 2 for x in yoy_growth) / len(yoy_growth)
                volatility = variance**0.5
            else:
                volatility = 0.0
        else:
            volatility = 0.0

        # Determine trend direction
        if cagr > 10:
            direction = "Strong Growth"
        elif cagr > 3:
            direction = "Moderate Growth"
        elif cagr > -3:
            direction = "Stable"
        elif cagr > -10:
            direction = "Moderate Decline"
        else:
            direction = "Sharp Decline"

        # Consistency: Are all YoY changes in same direction?
        if len(values) >= 3:
            yoy_directions = []
            for i in range(1, len(values)):
                yoy_directions.append(values[i] > values[i - 1])

            consistency = "Consistent" if all(yoy_directions) or not any(yoy_directions) else "Volatile"
        else:
            consistency = "Insufficient Data"

        trends[metric] = {
            "periods": periods,
            "values": values,
            "cagr": cagr,
            "volatility": volatility,
            "direction": direction,
            "consistency": consistency,
        }

    return trends


def compare_to_industry_benchmarks(
    company_ratios: dict[str, dict[str, float]], industry_benchmarks: dict | None = None
) -> dict[str, dict]:
    """
    Compare company ratios against industry benchmarks.

    Args:
        company_ratios: Ratios from calculate_all_ratios()
        industry_benchmarks: Optional dict of industry benchmark ratios
                           If None, uses generic healthy company benchmarks

    Returns:
        Dict with comparison results and flags
    """
    # Default healthy company benchmarks (generic, should be customized by industry)
    default_benchmarks = {
        "profitability": {
            "operating_margin": 15.0,  # 15% is healthy
            "pbt_margin": 10.0,
            "roe": 15.0,
        },
        "liquidity": {
            "current_ratio": 1.5,  # 1.5x is healthy
            "quick_ratio": 1.0,  # 1.0x is healthy
        },
        "solvency": {
            "liabilities_to_assets": 60.0,  # <60% is healthy
            "equity_to_assets": 25.0,  # >25% is healthy
        },
        "efficiency": {
            "receivables_days": 90.0,  # <90 days is good
            "payables_days": 60.0,  # 60 days is reasonable
        },
        "cashflow": {"ocf_to_revenue": 10.0},  # >10% is healthy},
    }

    benchmarks = industry_benchmarks or default_benchmarks
    comparisons = {}

    for category, ratios in company_ratios.items():
        comparisons[category] = {}

        for ratio_name, company_value in ratios.items():
            benchmark_value = benchmarks.get(category, {}).get(ratio_name)

            if benchmark_value is not None:
                # Determine if better/worse based on ratio type
                # Higher is better for: margins, returns, liquidity, coverage
                # Lower is better for: leverage ratios, days
                higher_is_better = any(
                    keyword in ratio_name
                    for keyword in ["margin", "roe", "ratio", "coverage", "turnover", "equity_to"]
                )

                if higher_is_better:
                    status = "Above" if company_value >= benchmark_value else "Below"
                    delta = company_value - benchmark_value
                else:
                    # Lower is better (leverage, days)
                    status = "Better" if company_value <= benchmark_value else "Worse"
                    delta = benchmark_value - company_value

                # Flag significant deviations (>20% from benchmark)
                is_significant = (
                    abs(delta / benchmark_value) > 0.2 if benchmark_value != 0 else False
                )

                comparisons[category][ratio_name] = {
                    "company_value": company_value,
                    "benchmark": benchmark_value,
                    "delta": delta,
                    "status": status,
                    "is_significant": is_significant,
                }

    return comparisons


def format_ratio_table(ratios: dict[str, float], title: str) -> str:
    """Format ratios as Markdown table."""
    lines = [
        f"**{title}**",
        "| Ratio | Value |",
        "|---|---:|",
    ]

    # Metrics that should be formatted as absolute values (not percentages or ratios)
    absolute_value_keys = ["working_capital", "free_cash_flow"]

    # Metrics that should be formatted as days
    days_keys = ["receivables_days", "payables_days"]

    for key, value in ratios.items():
        # Format based on key type
        if any(abs_key in key.lower() for abs_key in absolute_value_keys):
            # Absolute value in RM'000
            formatted = f"RM{value:,.0f}'000"
        elif any(day_key in key.lower() for day_key in days_keys):
            # Days
            formatted = f"{value:.1f} days"
        elif "ratio" in key or "coverage" in key or "turnover" in key:
            # Ratio (x times)
            formatted = f"{value:.2f}x"
        elif abs(value) >= 100:
            # Large percentage
            formatted = f"{value:,.1f}%"
        else:
            # Small percentage
            formatted = f"{value:.2f}%"

        # Clean key for display
        display_key = key.replace("_", " ").title()
        lines.append(f"| {display_key} | {formatted} |")

    return "\n".join(lines)


def main(
    fs_index: str,
    output_format: str = "json",
    prior_index: str | None = None,
    trend_years: list[str] | None = None,
    benchmark: bool = False,
):
    """
    Main function with enhanced analysis capabilities.

    Args:
        fs_index: Path to current period fs_index.json
        output_format: "json" or "markdown"
        prior_index: Path to prior period fs_index.json (for YoY growth)
        trend_years: List of fs_index.json paths for trend analysis (chronological)
        benchmark: Whether to include industry benchmark comparison
    """
    path = Path(fs_index)
    if not path.exists():
        print(f"Error: {fs_index} not found", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        current_data = json.load(f)

    # Detect period
    period_days = 182 if "Q" in path.stem or "H1" in path.stem else 365

    # Calculate current period ratios
    current_ratios = calculate_all_ratios(current_data, period_days)

    results = {"ratios": current_ratios}

    # YoY Growth Analysis
    if prior_index:
        prior_path = Path(prior_index)
        if prior_path.exists():
            with open(prior_path) as f:
                prior_data = json.load(f)

            prior_ratios = calculate_all_ratios(prior_data, period_days)
            growth_analysis = calculate_enhanced_growth_analysis(current_data, prior_data)
            ratio_changes = calculate_ratio_changes(current_ratios, prior_ratios)

            results["yoy_growth"] = growth_analysis
            results["ratio_changes"] = ratio_changes
        else:
            print(f"Warning: Prior file {prior_index} not found, skipping YoY analysis", file=sys.stderr)

    # Trend Analysis (3+ years)
    if trend_years and len(trend_years) >= 2:
        datasets = []
        for year_path in trend_years:
            p = Path(year_path)
            if p.exists():
                with open(p) as f:
                    datasets.append((p.stem, json.load(f)))
            else:
                print(f"Warning: Trend file {year_path} not found, skipping", file=sys.stderr)

        if len(datasets) >= 2:
            results["trends"] = calculate_trend_analysis(datasets)

    # Industry Benchmarking
    if benchmark:
        results["benchmarks"] = compare_to_industry_benchmarks(current_ratios)

    # Output
    if output_format == "json":
        print(json.dumps(results, indent=2))
    else:
        # Markdown output
        print("# Financial Analysis Report\n")

        # 1. Current Ratios
        print("## Current Period Ratios\n")
        for category, ratios in current_ratios.items():
            print(format_ratio_table(ratios, category.replace("_", " ").title()))
            print()

        # 2. YoY Growth
        if "yoy_growth" in results:
            print("## Year-over-Year Growth\n")
            print("| Metric | Current | Prior | Change | Growth | Sig |")
            print("|---|---:|---:|---:|---:|---|")
            for metric, data in results["yoy_growth"].items():
                sig_flag = "✓" if data["is_significant"] else ""
                print(
                    f"| {metric} | {data['current']:,.0f} | {data['prior']:,.0f} | "
                    f"{data['direction']} {abs(data['absolute_change']):,.0f} | "
                    f"{data['growth_rate']:+.1f}% | {sig_flag} |"
                )
            print()

        # 3. Ratio Changes
        if "ratio_changes" in results:
            print("## Ratio Changes\n")
            for category, ratios in results["ratio_changes"].items():
                print(f"**{category.replace('_', ' ').title()}**")
                print("| Ratio | Current | Prior | Change | Sig |")
                print("|---|---:|---:|---:|---|")
                for ratio_name, data in ratios.items():
                    sig_flag = "✓" if data["is_significant"] else ""
                    display_name = ratio_name.replace("_", " ").title()
                    print(
                        f"| {display_name} | {data['current']:.2f} | {data['prior']:.2f} | "
                        f"{data['direction']} {abs(data['absolute_change']):.2f} | {sig_flag} |"
                    )
                print()

        # 4. Trend Analysis
        if "trends" in results:
            print("## Multi-Year Trend Analysis\n")
            for metric, trend_data in results["trends"].items():
                if "error" in trend_data:
                    continue

                print(f"**{metric.replace('_', ' ').title()}**")
                print(f"- **CAGR**: {trend_data['cagr']:.2f}%")
                print(f"- **Direction**: {trend_data['direction']}")
                print(f"- **Consistency**: {trend_data['consistency']}")
                print(f"- **Volatility**: {trend_data['volatility']:.2f}%")
                print()

        # 5. Benchmarks
        if "benchmarks" in results:
            print("## Industry Benchmark Comparison\n")
            for category, comparisons in results["benchmarks"].items():
                print(f"**{category.replace('_', ' ').title()}**")
                print("| Ratio | Company | Benchmark | Status |")
                print("|---|---:|---:|---|")
                for ratio_name, data in comparisons.items():
                    display_name = ratio_name.replace("_", " ").title()
                    print(
                        f"| {display_name} | {data['company_value']:.2f} | "
                        f"{data['benchmark']:.2f} | {data['status']} |"
                    )
                print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Calculate financial ratios from finanalysis output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic ratio calculation
  python financial_calculator.py output/2024/fs_index.json --format markdown

  # With YoY growth analysis
  python financial_calculator.py output/2024/fs_index.json --prior output/2023/fs_index.json

  # Multi-year trend analysis
  python financial_calculator.py output/2024/fs_index.json --trend 2022 2023 2024

  # Full analysis with benchmarking
  python financial_calculator.py output/2024/fs_index.json --prior output/2023/fs_index.json --benchmark
        """,
    )

    parser.add_argument("fs_index", help="Path to current period fs_index.json")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format")
    parser.add_argument("--prior", help="Path to prior period fs_index.json (for YoY growth)")
    parser.add_argument(
        "--trend",
        nargs="+",
        metavar="YEAR_PATH",
        help="Paths to fs_index.json files for trend analysis (in chronological order)",
    )
    parser.add_argument("--benchmark", action="store_true", help="Compare against industry benchmarks")

    args = parser.parse_args()

    main(
        args.fs_index,
        args.format,
        args.prior,
        args.trend,
        args.benchmark,
    )
