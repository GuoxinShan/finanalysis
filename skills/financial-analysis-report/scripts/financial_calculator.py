#!/usr/bin/env python3
"""
Financial ratio calculator for finanalysis data.

Reads fs_index.json and computes standard financial ratios.
Outputs JSON to stdout.

Usage:
    python financial_calculator.py <fs_index.json>                           # All ratios
    python financial_calculator.py <fs_index.json> --category profitability  # Specific category
    python financial_calculator.py <fs_index.json> --prior <prior.json>       # YoY growth
    python financial_calculator.py <fs_index.json> --trend 2022:<f1> 2023:<f2>  # Multi-year
"""

import argparse
import json
import sys
from pathlib import Path


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value for zero denominator."""
    return numerator / denominator if denominator != 0 else default


def _normalize_label(label: str) -> str:
    """Normalize a financial statement label for fuzzy matching."""
    s = label.lower()
    # Normalize cash flow direction markers: (used in)/from, from/(used in)
    s = s.replace("(used in)/from", "from")
    s = s.replace("from/(used in)", "from")
    s = s.replace("from/", "")
    s = s.replace("/(used in)", "")
    # Remove extra whitespace
    s = " ".join(s.split())
    return s


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
            # Fuzzy search: normalize both sides and compare
            norm_label = _normalize_label(label)
            item = None
            for key, value in line_items.items():
                norm_key = _normalize_label(key)
                if norm_label in norm_key or norm_key in norm_label:
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
        ]:
            if key_format in item:
                val = item[key_format]
                return float(val) if val is not None else 0.0

        return 0.0

    except (KeyError, TypeError, ValueError, AttributeError):
        return 0.0


def get_total_borrowings(data: dict, entity: str = "group", period: str = "current") -> float:
    """Get total borrowings (current + non-current)."""
    line_items = data.get("line_items", {})

    non_current = 0.0
    current = 0.0
    generic_borrowings = 0.0

    for key, value in line_items.items():
        norm = _normalize_label(key)
        if "borrowings" not in norm:
            continue
        if "non-current" in norm:
            non_current = get_metric_value(data, key, entity, period)
        elif "current" in norm:
            current = get_metric_value(data, key, entity, period)
        else:
            generic_borrowings = get_metric_value(data, key, entity, period)

    if non_current > 0.0 or current > 0.0:
        return non_current + current
    return generic_borrowings


def get_operating_expenses(data: dict, entity: str = "group", period: str = "current") -> float:
    """Get total operating expenses."""
    cost_of_sales = get_metric_value(data, "cost of sales", entity, period)
    distribution = get_metric_value(data, "distribution expenses", entity, period)
    administrative = get_metric_value(data, "administrative expenses", entity, period)
    other = get_metric_value(data, "other expenses", entity, period)

    if cost_of_sales == 0.0 and distribution == 0.0 and administrative == 0.0:
        return get_metric_value(data, "operating expenses", entity, period)

    return cost_of_sales + distribution + administrative + other


# ── Category calculators ─────────────────────────────────────────────────────

CATEGORIES = ["profitability", "liquidity", "solvency", "efficiency", "cashflow"]


def calculate_profitability_ratios(data: dict) -> dict[str, float]:
    """Calculate profitability margins and returns."""
    revenue = get_metric_value(data, "revenue")
    gross_profit = get_metric_value(data, "gross profit")
    pbt = get_metric_value(data, "profit before tax")
    pat = get_metric_value(data, "profit for the financial year")
    attributable = get_metric_value(data, "profit for the financial year attributable to: owners of the parent")
    equity = get_metric_value(data, "equity attributable to owners of the parent")
    total_assets = get_metric_value(data, "total assets")

    return {
        "gross_margin": safe_divide(gross_profit, revenue) * 100,
        "pbt_margin": safe_divide(pbt, revenue) * 100,
        "pat_margin": safe_divide(pat, revenue) * 100,
        "attributable_margin": safe_divide(attributable, revenue) * 100,
        "roe": safe_divide(attributable, equity) * 100,
        "roa": safe_divide(attributable, total_assets) * 100,
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
    operating_expenses = abs(get_operating_expenses(data))
    trade_receivables = get_metric_value(data, "trade receivables")
    trade_payables = get_metric_value(data, "trade payables")

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

    capex = -icf if icf < 0 else 0
    fcf = ocf - capex

    return {
        "ocf_to_revenue": safe_divide(ocf, revenue) * 100,
        "free_cash_flow": fcf,
        "ocf_interest_coverage": safe_divide(ocf, finance_costs),
        "ocf_to_debt": safe_divide(ocf, total_borrowings) * 100,
    }


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


# ── Growth & trend analysis ──────────────────────────────────────────────────

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

        is_significant = abs(growth_rate) > 15.0

        growth_analysis[meta["label"]] = {
            "current": curr_val,
            "prior": prior_val,
            "absolute_change": abs_change,
            "growth_rate": growth_rate,
            "is_significant": is_significant,
            "unit": meta["unit"],
            "direction": "+" if growth_rate > 0 else "-" if growth_rate < 0 else "=",
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

            if "margin" in ratio_name or "to_assets" in ratio_name or "to_revenue" in ratio_name:
                change_metric = "pp"
                is_significant = abs(abs_change) > 2.0
            elif "ratio" in ratio_name or "coverage" in ratio_name or "turnover" in ratio_name:
                change_metric = "x"
                is_significant = abs(abs_change) > 0.2
            else:
                change_metric = "units"
                is_significant = abs(abs_change) > 5.0

            ratio_changes[category][ratio_name] = {
                "current": current_value,
                "prior": prior_value,
                "absolute_change": abs_change,
                "change_metric": change_metric,
                "is_significant": is_significant,
                "direction": "+" if abs_change > 0 else "-" if abs_change < 0 else "=",
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

        if len(values) >= 2 and values[0] > 0:
            years = len(values) - 1
            cagr = ((values[-1] / values[0]) ** (1 / years) - 1) * 100
        else:
            cagr = 0.0

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


# ── CLI ───────────────────────────────────────────────────────────────────────

CATEGORY_CALCULATORS = {
    "profitability": calculate_profitability_ratios,
    "liquidity": calculate_liquidity_ratios,
    "solvency": calculate_solvency_ratios,
    "efficiency": calculate_efficiency_ratios,
    "cashflow": calculate_cashflow_ratios,
}


def main():
    parser = argparse.ArgumentParser(
        description="Calculate financial ratios from finanalysis fs_index.json output.",
    )
    parser.add_argument("fs_index", help="Path to fs_index.json")
    parser.add_argument(
        "--category",
        choices=CATEGORIES,
        help="Compute ratios for a single category (flat dict output)",
    )
    parser.add_argument("--prior", help="Path to prior period fs_index.json for YoY growth analysis")
    parser.add_argument(
        "--trend",
        nargs="+",
        metavar="YEAR:FILE",
        help="Multi-year trend: YEAR:<path> pairs in chronological order",
    )

    args = parser.parse_args()

    fs_path = Path(args.fs_index)
    if not fs_path.exists():
        print(f"Error: {args.fs_index} not found", file=sys.stderr)
        sys.exit(1)

    with open(fs_path) as f:
        current_data = json.load(f)

    # Detect half-year vs full-year from filename
    period_days = 182 if "Q" in fs_path.stem or "H1" in fs_path.stem else 365

    # ── Calculate ratios ──────────────────────────────────────────────────
    if args.category:
        calc_fn = CATEGORY_CALCULATORS[args.category]
        if args.category == "efficiency":
            result = calc_fn(current_data, period_days)
        else:
            result = calc_fn(current_data)
    else:
        result = calculate_all_ratios(current_data, period_days)

    # ── YoY growth ────────────────────────────────────────────────────────
    if args.prior:
        prior_path = Path(args.prior)
        if not prior_path.exists():
            print(f"Error: prior file {args.prior} not found", file=sys.stderr)
            sys.exit(1)

        with open(prior_path) as f:
            prior_data = json.load(f)

        result["yoy_growth"] = calculate_enhanced_growth_analysis(current_data, prior_data)

        # Ratio changes only when we have all categories
        if not args.category:
            current_ratios = calculate_all_ratios(current_data, period_days)
            prior_ratios = calculate_all_ratios(prior_data, period_days)
            result["ratio_changes"] = calculate_ratio_changes(current_ratios, prior_ratios)

    # ── Trend analysis ────────────────────────────────────────────────────
    if args.trend:
        datasets = []
        for spec in args.trend:
            if ":" not in spec:
                print(f"Error: --trend argument must be YEAR:<path>, got '{spec}'", file=sys.stderr)
                sys.exit(1)
            year, _, file_path = spec.partition(":")
            p = Path(file_path)
            if not p.exists():
                print(f"Error: trend file {file_path} not found", file=sys.stderr)
                sys.exit(1)
            with open(p) as f:
                datasets.append((year, json.load(f)))

        if len(datasets) >= 2:
            result["trends"] = calculate_trend_analysis(datasets)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
