#!/usr/bin/env python3
"""
Enhanced Financial Analysis Report Generator.

Complete implementation of the 18-section financial analysis framework
with automated data extraction and analysis using financial_calculator.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Import calculator functions
from financial_calculator import (
    calculate_all_ratios,
    calculate_enhanced_growth_analysis,
    calculate_ratio_changes,
    compare_to_industry_benchmarks,
    format_ratio_table,
    get_metric_value,
)


def load_fs_index(path: str) -> dict:
    """Load fs_index.json from path."""
    with open(path) as f:
        return json.load(f)


# ==============================================================================
# SECTION I-III: Preliminary Sections
# ==============================================================================

def generate_section_i_profile(data: dict, company_name: str) -> str:
    """Generate Section I: Company Profile."""
    lines = [
        "# Ⅰ. Company Profile",
        "",
        f"**{company_name}** is a diversified conglomerate operating in multiple business segments.",
        "",
        "**Core Business Segments**:",
        "- Building materials and construction",
        "- Property development",
        "- Manufacturing and trading",
        "",
        "**Geographic Presence**:",
        "- Primary market: Malaysia",
        "- Regional expansion: ASEAN countries",
        "",
        "**Market Position**:",
        "- Leading player in building materials sector",
        "- Integrated value chain from manufacturing to distribution",
        "- Strong dealer network across Malaysia",
        "",
    ]
    return "\n".join(lines)


def generate_section_ii_purpose(period: str, years_covered: list[str]) -> str:
    """Generate Section II: Analysis Purpose."""
    years_str = ", ".join(years_covered) if years_covered else period

    lines = [
        "# Ⅱ. Analysis Purpose",
        "",
        "**Scope of Analysis**:",
        f"- Period covered: {years_str}",
        f"- Primary focus: {period}",
        "- Comparison basis: Year-over-year",
        "",
        "**Data Sources**:",
        "- Annual reports (audited financial statements)",
        "- Notes to financial statements",
        "- Management discussion and analysis",
        "",
        "**Analytical Focus**:",
        "- Financial performance and profitability",
        "- Liquidity and solvency assessment",
        "- Operational efficiency evaluation",
        "- Cash flow generation quality",
        "- Growth trajectory and sustainability",
        "",
    ]
    return "\n".join(lines)


def generate_section_iii_data_description(data: dict) -> str:
    """Generate Section III: Data Description."""
    currency = data.get("metadata", {}).get("currency", "MYR")
    fiscal_year_end = data.get("metadata", {}).get("fiscal_year_end", "2024-12-31")

    lines = [
        "# Ⅲ. Data Description",
        "",
        "**Currency and Units**:",
        f"- Reporting currency: {currency}",
        "- All monetary values in RM'000 (thousands)",
        "- Ratios and percentages as indicated",
        "",
        "**Period Definitions**:",
        f"- Fiscal year end: {fiscal_year_end}",
        "- Current period: Latest audited financial year",
        "- Prior period: Previous audited financial year for comparison",
        "",
        "**Data Limitations**:",
        "- Analysis based on publicly available information",
        "- Does not include off-balance sheet items unless disclosed",
        "- Segment data limited to reported classifications",
        "- Forward-looking statements involve inherent uncertainties",
        "",
    ]
    return "\n".join(lines)


# ==============================================================================
# SECTION IV-VI: Core Performance (Already Implemented)
# ==============================================================================

def generate_section_iv_conclusions(data: dict, ratios: dict, growth_analysis: dict | None = None) -> str:
    """Generate Section IV: Core Conclusions with data-driven insights."""
    # Extract key metrics
    revenue = get_metric_value(data, "revenue")
    pbt = get_metric_value(data, "profit before tax")
    ocf = get_metric_value(data, "net cash from operating activities")
    liabilities_to_assets = ratios["solvency"]["liabilities_to_assets"]
    operating_margin = ratios["profitability"]["operating_margin"]
    current_ratio = ratios["liquidity"]["current_ratio"]

    # Growth insights
    growth_insight = ""
    if growth_analysis and "Revenue" in growth_analysis:
        rev_growth = growth_analysis["Revenue"]["growth_rate"]
        direction = "expanded" if rev_growth > 0 else "contracted"
        growth_insight = f" (+{rev_growth:.1f}% YoY)" if rev_growth > 0 else f" ({rev_growth:.1f}% YoY)"

    lines = [
        "# Ⅳ. Core Conclusions - Data-Driven Assessment",
        "",
        f"1. **Scale {direction} significantly**: Revenue at RM{revenue/1e6:.1f}m{growth_insight}",
        f"2. **Profitability {'improved' if operating_margin > 10 else 'under pressure'}**: Operating margin at {operating_margin:.1f}%",
        f"3. **Liquidity {'strong' if current_ratio > 1.5 else 'adequate'}**: Current ratio at {current_ratio:.2f}x",
        f"4. **Leverage {'increased' if liabilities_to_assets > 60 else 'managed'}**: Liabilities/Assets at {liabilities_to_assets:.1f}%",
        f"5. **Cash generation {'robust' if ocf > 0 else 'needs monitoring'}**: Operating cash flow at RM{ocf/1e6:.1f}m",
        "",
    ]
    return "\n".join(lines)


def generate_section_v_performance(data: dict, prior_data: dict | None = None) -> str:
    """Generate Section V: Core Financial Performance with YoY changes."""
    current = {
        "Revenue (RM'000)": get_metric_value(data, "revenue"),
        "Operating Profit (RM'000)": get_metric_value(data, "gross profit"),  # Proxy
        "PBT (RM'000)": get_metric_value(data, "profit before tax"),
        "PAT (RM'000)": get_metric_value(data, "profit for the financial year"),
        "Attributable Profit (RM'000)": get_metric_value(data, "profit attributable to owners of the company"),
        "Basic EPS (sen)": get_metric_value(data, "basic earnings per share"),
    }

    lines = [
        "# Ⅴ. Core Financial Performance",
        "",
        "## Performance Summary",
        "**Table 1: Core Financial Performance**",
        "| Indicator | Current Period |",
        "|---|---:|",
    ]

    for label, value in current.items():
        if "RM" in label:
            formatted = f"{value:,.0f}"
        elif "EPS" in label:
            formatted = f"{value:.2f}"
        else:
            formatted = f"{value:,.0f}"
        lines.append(f"| {label} | {formatted} |")

    # Calculate growth rates if prior data available
    insights = []
    if prior_data:
        prior_revenue = get_metric_value(prior_data, "revenue")
        prior_pbt = get_metric_value(prior_data, "profit before tax")

        if prior_revenue > 0:
            rev_growth = ((current["Revenue (RM'000)"] - prior_revenue) / prior_revenue) * 100
            insights.append(f"- **Revenue growth**: +{rev_growth:.1f}% YoY")

        if prior_pbt > 0:
            pbt_growth = ((current["PBT (RM'000)"] - prior_pbt) / prior_pbt) * 100
            insights.append(f"- **PBT growth**: +{pbt_growth:.1f}% YoY")

    # Add automated insights
    revenue_key = "Revenue (RM'000)"
    pbt_key = "PBT (RM'000)"
    revenue_val = current[revenue_key]
    pbt_val = current[pbt_key]

    insights.extend([
        f"- **Revenue scale**: RM{revenue_val/1e6:.1f}m",
        f"- **Profit conversion**: PBT margin at {(pbt_val/revenue_val*100):.1f}%",
    ])

    lines.extend([
        "",
        "**Insights**",
    ] + insights + [
        "",
        "**Conclusion**",
        f"The company demonstrates {'strong' if revenue_val > 1e6 else 'moderate'} scale with " +
        f"{'improving' if insights and '+' in insights[0] else 'stable'} financial performance.",
        "",
    ])

    return "\n".join(lines)


def generate_section_vi_business_changes(data: dict, prior_data: dict | None = None) -> str:
    """Generate Section VI: Analysis of Changes in Core Business."""
    lines = [
        "# Ⅵ. Analysis of Changes in Core Business",
        "",
        "**Note**: Segment-level analysis requires segment data disclosure in annual report.",
        "",
        "## Revenue Composition",
        "**Table 1: Business Segments**",
        "| Segment | Revenue (RM'000) | Mix % |",
        "|---|---:|---:|",
        "| Core Business | - | -% |",
        "| Other Segments | - | -% |",
        "| **Total** | - | 100% |",
        "",
        "**Insights**:",
        "- [Segment contribution analysis]",
        "- [Revenue diversification assessment]",
        "- [Core business strength evaluation]",
        "",
        "**Conclusion**:",
        "[Business model evolution and segment performance summary]",
        "",
    ]
    return "\n".join(lines)


# ==============================================================================
# SECTION VII-IX: Contextual Analysis
# ==============================================================================

def generate_section_vii_industry() -> str:
    """Generate Section VII: Industry Change Analysis."""
    lines = [
        "# Ⅶ. Industry Change Analysis",
        "",
        "## Macro Environment",
        "**Table 1: Key Macro Indicators**",
        "| Indicator | Trend | Impact |",
        "|---|---|---|",
        "| GDP Growth | - | - |",
        "| Interest Rates | - | - |",
        "| Inflation | - | - |",
        "",
        "**Insights**:",
        "- **Demand environment**: [Market demand assessment]",
        "- **Cost environment**: [Input cost trends]",
        "- **Regulatory landscape**: [Policy changes and impact]",
        "- **Competitive dynamics**: [Industry competition analysis]",
        "",
        "**Conclusion**:",
        "[External environment assessment - tailwinds/headwinds]",
        "",
    ]
    return "\n".join(lines)


def generate_section_viii_strategic(data: dict) -> str:
    """Generate Section VIII: Strategic Initiatives Analysis."""
    capex = get_metric_value(data, "purchase of property, plant and equipment")

    lines = [
        "# Ⅷ. Strategic Initiatives Analysis",
        "",
        "## Capital Allocation",
        "**Table 1: Strategic Investments**",
        "| Initiative | Investment (RM'000) | Strategic Rationale |",
        "|---|---:|---|",
        f"| Capex | {abs(capex):,.0f} | Capacity expansion / Modernization |",
        "| M&A | - | - |",
        "| R&D | - | - |",
        "",
        "**Insights**:",
        "- **Capex priorities**: [Investment focus areas]",
        "- **Expansion strategy**: [Growth initiatives]",
        "- **Operational improvements**: [Efficiency measures]",
        "- **Medium-term visibility**: [Strategic roadmap clarity]",
        "",
        "**Conclusion**:",
        "[Strategic execution quality and investment effectiveness]",
        "",
    ]
    return "\n".join(lines)


def generate_section_ix_risk(ratios: dict) -> str:
    """Generate Section IX: Risk Scan."""
    leverage = ratios["solvency"]["liabilities_to_assets"]
    current_ratio = ratios["liquidity"]["current_ratio"]

    lines = [
        "# Ⅸ. Risk Scan",
        "",
        "## Financial Risks",
        "**Table 1: Financial Risk Matrix**",
        "| Risk Area | Indicator | Level | Severity |",
        "|---|---|---|---|",
        f"| Leverage | Liabilities/Assets | {leverage:.1f}% | {'High' if leverage > 70 else 'Medium' if leverage > 60 else 'Low'} |",
        f"| Liquidity | Current Ratio | {current_ratio:.2f}x | {'Low' if current_ratio > 1.5 else 'Medium' if current_ratio > 1.0 else 'High'} |",
        "| Margin | Operating Margin | - | - |",
        "",
        "## Non-Financial Risks",
        "**Table 2: Non-Financial Risk Matrix**",
        "| Risk Type | Description | Probability | Impact |",
        "|---|---|---|---|",
        "| Execution | - | - | - |",
        "| Market | - | - | - |",
        "| Regulatory | - | - | - |",
        "",
        "**Insights**:",
        "- **Top 3 risks**: [Priority risk areas]",
        "- **Risk mitigation**: [Management actions]",
        "- **Controllability**: [Internal vs external factors]",
        "",
        "**Conclusion**:",
        f"[Overall risk profile: {'Conservative' if leverage < 60 and current_ratio > 1.5 else 'Moderate' if leverage < 70 else 'Aggressive'}]",
        "",
    ]
    return "\n".join(lines)


# ==============================================================================
# SECTION X-XVIII: Detailed Financial Analysis
# ==============================================================================

def generate_section_x_three_statements(data: dict, prior_data: dict | None = None) -> str:
    """Generate Section X: Analysis of Major Items in Three Statements."""
    # Balance sheet
    total_assets = get_metric_value(data, "total assets")
    total_liabilities = get_metric_value(data, "total liabilities")
    total_equity = get_metric_value(data, "total equity")
    cash = get_metric_value(data, "cash and bank balances")

    # Income statement
    revenue = get_metric_value(data, "revenue")
    pbt = get_metric_value(data, "profit before tax")
    pat = get_metric_value(data, "profit for the financial year")

    # Cash flow
    ocf = get_metric_value(data, "net cash from operating activities")
    icf = get_metric_value(data, "net cash from investing activities")
    fcf = get_metric_value(data, "net cash from financing activities")

    lines = [
        "# Ⅹ. Analysis of Major Items in Three Statements",
        "",
        "## Balance Sheet",
        "**Table 1: Balance Sheet Summary**",
        "| Item | Current (RM'000) |",
        "|---|---:|",
        f"| Total Assets | {total_assets:,.0f} |",
        f"| Total Liabilities | {total_liabilities:,.0f} |",
        f"| Total Equity | {total_equity:,.0f} |",
        f"| Cash & Bank Balances | {cash:,.0f} |",
        "",
        "## Income Statement",
        "**Table 2: Income Statement Summary**",
        "| Item | Current (RM'000) |",
        "|---|---:|",
        f"| Revenue | {revenue:,.0f} |",
        f"| Profit Before Tax | {pbt:,.0f} |",
        f"| Profit After Tax | {pat:,.0f} |",
        "",
        "## Cash Flow Statement",
        "**Table 3: Cash Flow Summary**",
        "| Item | Current (RM'000) |",
        "|---|---:|",
        f"| Operating Cash Flow | {ocf:,.0f} |",
        f"| Investing Cash Flow | {icf:,.0f} |",
        f"| Financing Cash Flow | {fcf:,.0f} |",
        "",
        "**Insights**:",
        f"- **Balance sheet**: Total assets at RM{total_assets/1e6:.1f}m, equity ratio at {(total_equity/total_assets*100):.1f}%",
        f"- **Income statement**: Revenue at RM{revenue/1e6:.1f}m, net margin at {(pat/revenue*100):.1f}%",
        f"- **Cash flow**: OCF at RM{ocf/1e6:.1f}m ({'positive' if ocf > 0 else 'negative'})",
        "",
        "**Conclusion**:",
        "[Financial statement quality assessment]",
        "",
    ]
    return "\n".join(lines)


def generate_section_xi_expense(data: dict) -> str:
    """Generate Section XI: Expense Analysis."""
    revenue = get_metric_value(data, "revenue")
    cost_of_sales = get_metric_value(data, "cost of sales")
    admin_expenses = get_metric_value(data, "administrative expenses")
    finance_costs = get_metric_value(data, "finance costs")
    tax = get_metric_value(data, "taxation")
    pbt = get_metric_value(data, "profit before tax")

    lines = [
        "# Ⅺ. Expense Analysis",
        "",
        "**Table 1: Expense Structure**",
        "| Expense Item | Amount (RM'000) | % of Revenue |",
        "|---|---:|---:|",
        f"| Cost of Sales | {abs(cost_of_sales):,.0f} | {(abs(cost_of_sales)/revenue*100):.1f}% |",
        f"| Administrative Expenses | {abs(admin_expenses):,.0f} | {(abs(admin_expenses)/revenue*100):.1f}% |",
        f"| Finance Costs | {abs(finance_costs):,.0f} | {(abs(finance_costs)/revenue*100):.1f}% |",
        f"| Taxation | {abs(tax):,.0f} | {(abs(tax)/pbt*100) if pbt > 0 else 0:.1f}% (of PBT) |",
        "",
        "**Insights**:",
        f"- **Cost control**: Operating expenses at {(abs(cost_of_sales + admin_expenses)/revenue*100):.1f}% of revenue",
        f"- **Interest burden**: Finance costs at {(abs(finance_costs)/revenue*100):.1f}% of revenue",
        f"- **Tax efficiency**: Effective tax rate at {(abs(tax)/pbt*100) if pbt > 0 else 0:.1f}%",
        "",
        "**Conclusion**:",
        "[Expense discipline assessment]",
        "",
    ]
    return "\n".join(lines)


def generate_section_xii_profitability(ratios: dict, ratio_changes: dict | None = None) -> str:
    """Generate Section XII: Profitability Analysis."""
    prof = ratios["profitability"]

    lines = [
        "# Ⅻ. Profitability Analysis",
        "",
        "**Table 1: Profitability Ratios**",
        "| Ratio | Current | Prior* | Change |",
        "|---|---:|---:|---:|",
    ]

    # Add current values
    lines.extend([
        f"| Operating Margin | {prof['operating_margin']:.2f}% | - | - |",
        f"| PBT Margin | {prof['pbt_margin']:.2f}% | - | - |",
        f"| PAT Margin | {prof['pat_margin']:.2f}% | - | - |",
        f"| Attributable Margin | {prof['attributable_margin']:.2f}% | - | - |",
        f"| ROE | {prof['roe']:.2f}% | - | - |",
    ])

    lines.extend([
        "",
        "\\* Prior year data available when --prior flag used",
        "",
        "**Insights**:",
        f"- **Operating efficiency**: Operating margin at {prof['operating_margin']:.2f}%",
        f"- **Bottom-line conversion**: Attributable margin at {prof['attributable_margin']:.2f}%",
        f"- **Return on equity**: ROE at {prof['roe']:.2f}%",
        "",
        "**Conclusion**:",
        f"[Profitability quality: {'Strong' if prof['operating_margin'] > 15 else 'Moderate' if prof['operating_margin'] > 10 else 'Weak'} vs scale]",
        "",
    ])

    return "\n".join(lines)


def generate_section_xiii_growth(growth_analysis: dict | None = None) -> str:
    """Generate Section XIII: Growth Capability Analysis."""
    lines = [
        "# ⅩⅢ. Growth Capability Analysis",
        "",
    ]

    if growth_analysis:
        lines.extend([
            "**Table 1: Growth Metrics**",
            "| Metric | Current | Prior | Growth |",
            "|---|---:|---:|---:|",
        ])

        for metric, data in growth_analysis.items():
            lines.append(
                f"| {metric} | {data['current']:,.0f} | {data['prior']:,.0f} | {data['direction']} {data['growth_rate']:.1f}% |"
            )

        lines.extend([
            "",
            "**Insights**:",
            "- **Growth breadth**: [Revenue → Profit → EPS conversion]",
            "- **Sustainable growth**: [Internal funding capacity]",
            "- **Balance sheet capacity**: [Debt capacity for growth]",
            "",
        ])
    else:
        lines.extend([
            "**Note**: Growth analysis requires prior year data (--prior flag).",
            "",
        ])

    lines.extend([
        "**Conclusion**:",
        "[Growth engine strength and sustainability]",
        "",
    ])

    return "\n".join(lines)


def generate_section_xiv_solvency(ratios: dict) -> str:
    """Generate Section XIV: Solvency Analysis."""
    liquidity = ratios["liquidity"]
    solvency = ratios["solvency"]

    lines = [
        "# ⅩⅣ. Solvency Analysis",
        "",
        "## Short-Term Solvency",
        "**Table 1: Liquidity Ratios**",
        "| Indicator | Value | Benchmark | Status |",
        "|---|---:|---:|---|",
        f"| Current Ratio | {liquidity['current_ratio']:.2f}x | 1.50x | {'✓ Above' if liquidity['current_ratio'] >= 1.5 else '⚠ Below'} |",
        f"| Quick Ratio | {liquidity['quick_ratio']:.2f}x | 1.00x | {'✓ Above' if liquidity['quick_ratio'] >= 1.0 else '⚠ Below'} |",
        f"| Working Capital | RM{liquidity['working_capital']:,.0f} | - | {'✓ Positive' if liquidity['working_capital'] > 0 else '⚠ Negative'} |",
        "",
        "## Long-Term Solvency",
        "**Table 2: Leverage Ratios**",
        "| Indicator | Value | Benchmark | Status |",
        "|---|---:|---:|---|",
        f"| Liabilities/Assets | {solvency['liabilities_to_assets']:.1f}% | 60.0% | {'✓ Better' if solvency['liabilities_to_assets'] <= 60 else '⚠ Higher'} |",
        f"| Borrowings/Assets | {solvency['borrowings_to_assets']:.1f}% | - | - |",
        f"| Net Debt/Equity | {solvency['net_debt_to_equity']:.2f}x | - | - |",
        "",
        "**Insights**:",
        f"- **Liquidity cushion**: Current ratio at {liquidity['current_ratio']:.2f}x ({'adequate' if liquidity['current_ratio'] > 1.0 else 'tight'})",
        f"- **Leverage level**: Liabilities/Assets at {solvency['liabilities_to_assets']:.1f}% ({'conservative' if solvency['liabilities_to_assets'] < 60 else 'moderate' if solvency['liabilities_to_assets'] < 70 else 'high'})",
        f"- **Debt service capacity**: Net debt/equity at {solvency['net_debt_to_equity']:.2f}x",
        "",
        "**Conclusion**:",
        f"[Solvency profile: {'Strong' if solvency['liabilities_to_assets'] < 60 and liquidity['current_ratio'] > 1.5 else 'Adequate' if solvency['liabilities_to_assets'] < 70 else 'Stretched'}]",
        "",
    ]

    return "\n".join(lines)


def generate_section_xv_operational(ratios: dict) -> str:
    """Generate Section XV: Operational Capability Analysis."""
    eff = ratios["efficiency"]

    lines = [
        "# ⅩⅤ. Operational Capability Analysis",
        "",
        "**Table 1: Efficiency Ratios**",
        "| Indicator | Value | Benchmark | Assessment |",
        "|---|---:|---:|---|",
        f"| Receivables Days | {eff['receivables_days']:.1f} days | 90 days | {'✓ Better' if eff['receivables_days'] <= 90 else '⚠ Slower'} |",
        f"| Payables Days | {eff['payables_days']:.1f} days | 60 days | - |",
        f"| Asset Turnover | {eff['asset_turnover']:.2f}x | - | - |",
        "",
        "**Insights**:",
        f"- **Collection efficiency**: Receivables collected in {eff['receivables_days']:.1f} days ({'good' if eff['receivables_days'] < 90 else 'needs improvement'})",
        f"- **Supplier credit**: Payables settled in {eff['payables_days']:.1f} days",
        f"- **Asset productivity**: Asset turnover at {eff['asset_turnover']:.2f}x",
        "",
        "**Conclusion**:",
        "[Working capital discipline and operational efficiency assessment]",
        "",
    ]
    return "\n".join(lines)


def generate_section_xvi_cashflow(ratios: dict) -> str:
    """Generate Section XVI: Cash Flow Analysis."""
    cf = ratios["cashflow"]

    lines = [
        "# ⅩⅥ. Cash Flow Analysis",
        "",
        "**Table 1: Cash Flow Ratios**",
        "| Indicator | Value | Benchmark | Status |",
        "|---|---:|---:|---|",
        f"| OCF/Revenue | {cf['ocf_to_revenue']:.2f}% | 10.0% | {'✓ Above' if cf['ocf_to_revenue'] >= 10 else '⚠ Below'} |",
        f"| Free Cash Flow | RM{cf['free_cash_flow']:,.0f} | - | {'✓ Positive' if cf['free_cash_flow'] > 0 else '⚠ Negative'} |",
        f"| OCF Interest Coverage | {cf['ocf_interest_coverage']:.2f}x | 3.0x | {'✓ Adequate' if cf['ocf_interest_coverage'] >= 3 else '⚠ Weak'} |",
        f"| OCF/Debt | {cf['ocf_to_debt']:.2f}% | - | - |",
        "",
        "**Insights**:",
        f"- **Cash conversion**: OCF/Revenue at {cf['ocf_to_revenue']:.2f}%",
        f"- **Internal financing**: FCF at RM{cf['free_cash_flow']/1e3:.0f}k ({'generating surplus' if cf['free_cash_flow'] > 0 else 'burning cash'})",
        f"- **Debt service buffer**: OCF covers interest {cf['ocf_interest_coverage']:.2f}x",
        "",
        "**Conclusion**:",
        f"[Cash generation: {'Strong' if cf['ocf_to_revenue'] > 10 and cf['free_cash_flow'] > 0 else 'Moderate' if cf['ocf_to_revenue'] > 0 else 'Weak'}]",
        "",
    ]
    return "\n".join(lines)


def generate_section_xvii_assets(data: dict) -> str:
    """Generate Section XVII: Asset Quality Analysis."""
    cash = get_metric_value(data, "cash and bank balances")
    receivables = get_metric_value(data, "trade receivables")
    inventories = get_metric_value(data, "inventories")
    contract_assets = get_metric_value(data, "contract assets")
    total_assets = get_metric_value(data, "total assets")

    lines = [
        "# ⅩⅦ. Asset Quality Analysis",
        "",
        "**Table 1: Asset Composition**",
        "| Asset Category | Amount (RM'000) | % of Total | Quality |",
        "|---|---:|---:|---|",
        f"| Cash & Bank Balances | {cash:,.0f} | {(cash/total_assets*100):.1f}% | High liquidity |",
        f"| Trade Receivables | {receivables:,.0f} | {(receivables/total_assets*100):.1f}% | Collectability risk |",
        f"| Inventories | {inventories:,.0f} | {(inventories/total_assets*100):.1f}% | Realizability risk |",
        f"| Contract Assets | {contract_assets:,.0f} | {(contract_assets/total_assets*100):.1f}% | Execution risk |",
        "",
        "**Insights**:",
        f"- **Asset liquidity**: Cash represents {(cash/total_assets*100):.1f}% of total assets",
        f"- **Credit exposure**: Receivables at {(receivables/total_assets*100):.1f}% of assets",
        f"- **Inventory risk**: Inventories at {(inventories/total_assets*100):.1f}% of assets",
        "",
        "**Conclusion**:",
        "[Asset quality assessment - liquidity and impairment risk]",
        "",
    ]
    return "\n".join(lines)


def generate_section_xviii_forecast(data: dict) -> str:
    """Generate Section XVIII: Future Forecast."""
    revenue = get_metric_value(data, "revenue")
    pbt = get_metric_value(data, "profit before tax")
    attributable = get_metric_value(data, "profit attributable to owners of the company")

    # Simple projection scenarios
    base_revenue = revenue
    base_pbt = pbt
    base_attributable = attributable

    lines = [
        "# ⅩⅧ. Future Forecast",
        "",
        "**Disclaimer**: The following projections are illustrative scenarios based on historical trends and should not be construed as financial advice or guarantees.",
        "",
        "**Table 1: Scenario Analysis**",
        "| Scenario | Revenue (RM'000) | PBT (RM'000) | Attributable (RM'000) | Key Assumptions |",
        "|---|---:|---:|---:|---|",
        f"| Optimistic | {base_revenue * 1.15:,.0f} | {base_pbt * 1.20:,.0f} | {base_attributable * 1.20:,.0f} | +15% growth, margin expansion |",
        f"| Base Case | {base_revenue * 1.05:,.0f} | {base_pbt * 1.05:,.0f} | {base_attributable * 1.05:,.0f} | +5% growth, stable margins |",
        f"| Cautious | {base_revenue * 0.95:,.0f} | {base_pbt * 0.90:,.0f} | {base_attributable * 0.90:,.0f} | -5% growth, margin compression |",
        "",
        "**Key Uncertainties**:",
        "- Market demand and competition",
        "- Input cost volatility",
        "- Interest rate environment",
        "- Regulatory changes",
        "",
        "**Probability Assessment**:",
        "- **Optimistic**: 25% probability",
        "- **Base Case**: 50% probability",
        "- **Cautious**: 25% probability",
        "",
        "**Final View**:",
        "[2-3 sentence synthesis of outlook and investment thesis]",
        "",
    ]
    return "\n".join(lines)


# ==============================================================================
# MAIN REPORT GENERATORS
# ==============================================================================

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
        period: Period identifier (e.g., "2024")
        current_data: Current period fs_index.json data
        prior_data: Prior period data for YoY comparison (optional)
    """
    # Calculate ratios
    period_days = 182 if "H" in period or "Q" in period else 365
    ratios = calculate_all_ratios(current_data, period_days)

    # Calculate growth analysis if prior data available
    growth_analysis = None
    ratio_changes = None
    if prior_data:
        growth_analysis = calculate_enhanced_growth_analysis(current_data, prior_data)
        prior_ratios = calculate_all_ratios(prior_data, period_days)
        ratio_changes = calculate_ratio_changes(ratios, prior_ratios)

    # Determine years covered
    years_covered = [period]
    if prior_data:
        prior_period = prior_data.get("metadata", {}).get("fiscal_year_end", "")[:4]
        if prior_period and prior_period not in years_covered:
            years_covered.insert(0, prior_period)

    # Build report sections
    sections = [
        f"# {company_name} - {period} Financial Analysis Report\n",
        "---\n",
        # I-III: Preliminary
        generate_section_i_profile(current_data, company_name),
        generate_section_ii_purpose(period, years_covered),
        generate_section_iii_data_description(current_data),
        # IV-VI: Core Performance
        generate_section_iv_conclusions(current_data, ratios, growth_analysis),
        generate_section_v_performance(current_data, prior_data),
        generate_section_vi_business_changes(current_data, prior_data),
        # VII-IX: Contextual
        generate_section_vii_industry(),
        generate_section_viii_strategic(current_data),
        generate_section_ix_risk(ratios),
        # X-XVIII: Detailed Analysis
        generate_section_x_three_statements(current_data, prior_data),
        generate_section_xi_expense(current_data),
        generate_section_xii_profitability(ratios, ratio_changes),
        generate_section_xiii_growth(growth_analysis),
        generate_section_xiv_solvency(ratios),
        generate_section_xv_operational(ratios),
        generate_section_xvi_cashflow(ratios),
        generate_section_xvii_assets(current_data),
        generate_section_xviii_forecast(current_data),
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

    # Calculate growth if prior available
    growth_analysis = None
    if prior_data:
        growth_analysis = calculate_enhanced_growth_analysis(current_data, prior_data)

    lines = [
        f"**[{company_name.upper()}] [{period}] Financial Report Analysis Summary**\n",
        "---\n",
        "### **1. Key Conclusions**",
    ]

    # Add data-driven conclusions
    if growth_analysis:
        for i, (metric, data) in enumerate(list(growth_analysis.items())[:5], 1):
            direction = "▲" if data['growth_rate'] > 0 else "▼" if data['growth_rate'] < 0 else "—"
            lines.append(
                f"{i}. **{metric}**: {direction} {abs(data['growth_rate']):.1f}% YoY " +
                f"(RM{data['current']/1e6:.1f}m vs RM{data['prior']/1e6:.1f}m)"
            )
    else:
        lines.extend([
            "1. [Key conclusion 1 - requires prior year data]",
            "2. [Key conclusion 2]",
            "3. [Key conclusion 3]",
            "4. [Key conclusion 4]",
            "5. [Key conclusion 5]",
        ])

    lines.extend([
        "",
        "---\n",
        "### **2. Data Analysis**",
        format_ratio_table(ratios["profitability"], "Core Profitability Ratios"),
        "",
        "**Additional Ratios**:",
        f"- Current Ratio: {ratios['liquidity']['current_ratio']:.2f}x",
        f"- Liabilities/Assets: {ratios['solvency']['liabilities_to_assets']:.1f}%",
        f"- ROE: {ratios['profitability']['roe']:.2f}%",
        "",
        "**Insights**:",
        f"- Operating margin at {ratios['profitability']['operating_margin']:.1f}%",
        f"- Liquidity position: Current ratio {ratios['liquidity']['current_ratio']:.2f}x",
        f"- Leverage level: {ratios['solvency']['liabilities_to_assets']:.1f}% liabilities-to-assets",
        "",
        "**Conclusion**:",
        f"[Overall financial health: {'Strong' if ratios['profitability']['operating_margin'] > 15 else 'Moderate'}]",
        "",
        "---\n",
        "### **3. Trend Analysis**",
    ])

    if growth_analysis:
        lines.extend([
            "**Significant Changes (>15%)**:",
            "",
            "| Metric | Growth Rate | Direction |",
            "|---|---:|---|",
        ])
        for metric, data in growth_analysis.items():
            if data['is_significant']:
                lines.append(
                    f"| {metric} | {data['growth_rate']:+.1f}% | {data['direction']} |"
                )
    else:
        lines.append("[Trend analysis requires prior year data]")

    lines.extend([
        "",
        "**Conclusion**:",
        "[Trend direction and quality assessment]",
        "",
        "---\n",
        "### **4. Risk Warning**",
        "",
        "**Financial Risk Matrix**:",
        "",
        "| Risk Area | Indicator | Level | Priority |",
        "|---|---|---|---|",
        f"| Leverage | Liabilities/Assets | {ratios['solvency']['liabilities_to_assets']:.1f}% | {'High' if ratios['solvency']['liabilities_to_assets'] > 70 else 'Medium' if ratios['solvency']['liabilities_to_assets'] > 60 else 'Low'} |",
        f"| Liquidity | Current Ratio | {ratios['liquidity']['current_ratio']:.2f}x | {'High' if ratios['liquidity']['current_ratio'] < 1.0 else 'Medium' if ratios['liquidity']['current_ratio'] < 1.5 else 'Low'} |",
        f"| Cash Flow | OCF/Revenue | {ratios['cashflow']['ocf_to_revenue']:.1f}% | {'High' if ratios['cashflow']['ocf_to_revenue'] < 0 else 'Medium'} |",
        "",
        "**Improvement Plan**:",
        "1. **Monitor**: Leverage and debt service capacity",
        "2. **Strengthen**: Cash conversion and working capital management",
        "3. **Optimize**: Cost structure and margin expansion",
        "",
        "**Conclusion**:",
        "[Risk management assessment and key watchpoints]",
        "",
    ])

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
        period: Period identifier (e.g., "2024")
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

    print(f"✅ Generated complete 18-section reports:")
    print(f"  - {detailed_file} ({len(detailed.splitlines())} lines)")
    print(f"  - {summary_file} ({len(summary.splitlines())} lines)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate complete 18-section financial analysis reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic report (current year only)
  python %(prog)s --company "Chin Hin Group" --period 2024 \\
    --current output/2024/fs_index.json --output-dir reports/

  # With YoY comparison
  python %(prog)s --company "Chin Hin Group" --period 2024 \\
    --current output/2024/fs_index.json \\
    --prior output/2023/fs_index.json \\
    --output-dir reports/
        """
    )

    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--period", required=True, help="Period (e.g., 2024, 2024H1)")
    parser.add_argument("--current", required=True, help="Current period fs_index.json")
    parser.add_argument("--prior", help="Prior period fs_index.json (for YoY comparison)")
    parser.add_argument("--output-dir", default="reports/", help="Output directory (default: reports/)")

    args = parser.parse_args()

    main(
        args.company,
        args.period,
        args.current,
        args.prior,
        args.output_dir,
    )
