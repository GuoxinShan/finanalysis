# Financial Metrics Calculator - Implementation Plan

## Problem Statement

Currently, `fs_index.json` only contains **raw line items** from the three financial statements. We're missing:
- Profitability ratios (margins, ROE, ROA)
- Solvency ratios (current ratio, debt ratios, gearing)
- Growth metrics (YoY changes, CAGR)
- Cash flow quality metrics (OCF/revenue, FCF, coverage)
- Working capital efficiency (days ratios, turnover)
- Segment breakdowns

The YTL Corporation report (4677.KL-2024-12-31-revised.md) demonstrates the depth expected in professional analysis with 50+ calculated metrics.

---

## Proposed Solution: `MetricsCalculator` Module

### 1. Create New Module: `src/finanalysis/calculators/metrics.py`

**Purpose**: Calculate derived financial metrics from fs_index.json raw values

**Architecture**:
```python
# src/finanalysis/calculators/metrics.py
from pydantic import BaseModel
from typing import Dict, Optional, List
from pathlib import Path

class FinancialMetrics(BaseModel):
    """Container for all calculated financial metrics"""

    # Profitability
    gross_margin: Optional[float] = None  # percentage
    pbt_margin: Optional[float] = None
    pat_margin: Optional[float] = None
    attributable_margin: Optional[float] = None
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets

    # Solvency
    current_ratio: Optional[float] = None  # ratio (e.g., 1.32x)
    quick_ratio: Optional[float] = None
    debt_to_assets: Optional[float] = None  # percentage
    net_debt_to_equity: Optional[float] = None  # ratio
    gearing_ratio: Optional[float] = None  # percentage

    # Growth
    revenue_yoy_growth: Optional[float] = None  # percentage
    gross_profit_yoy_growth: Optional[float] = None
    pbt_yoy_growth: Optional[float] = None
    pat_yoy_growth: Optional[float] = None
    total_assets_yoy_growth: Optional[float] = None
    equity_yoy_growth: Optional[float] = None

    # Cash Flow Quality
    ocf_to_revenue: Optional[float] = None  # percentage
    free_cash_flow: Optional[float] = None  # absolute value
    interest_coverage: Optional[float] = None  # ratio
    ocf_to_debt: Optional[float] = None  # percentage

    # Working Capital
    receivables_days: Optional[float] = None  # days
    payables_days: Optional[float] = None  # days
    inventory_days: Optional[float] = None  # days
    asset_turnover: Optional[float] = None  # ratio

    # Growth Capability
    revenue_3yr_cagr: Optional[float] = None  # percentage
    patmi_3yr_cagr: Optional[float] = None


class MetricsCalculator:
    """Calculate derived financial metrics from FSIndex"""

    def __init__(self, fs_index: 'FSIndex', prior_fs_index: Optional['FSIndex'] = None):
        self.fs_index = fs_index
        self.prior_fs_index = prior_fs_index

    def calculate_all(self) -> FinancialMetrics:
        """Calculate all derived metrics"""
        return FinancialMetrics(
            **self.calculate_profitability(),
            **self.calculate_solvency(),
            **self.calculate_growth(),
            **self.calculate_cash_flow_quality(),
            **self.calculate_working_capital(),
        )

    def calculate_profitability(self) -> Dict:
        """Calculate profitability ratios"""
        revenue = self._get_value('revenue')
        gross_profit = self._get_value('gross profit')
        pbt = self._get_value('profit before tax')
        pat = self._get_value('profit for the financial year')
        attributable = self._get_value('attributable to owners')

        metrics = {}
        if revenue and revenue > 0:
            if gross_profit:
                metrics['gross_margin'] = round((gross_profit / revenue) * 100, 2)
            if pbt:
                metrics['pbt_margin'] = round((pbt / revenue) * 100, 2)
            if pat:
                metrics['pat_margin'] = round((pat / revenue) * 100, 2)
            if attributable:
                metrics['attributable_margin'] = round((attributable / revenue) * 100, 2)

        # ROE and ROA require average balance
        equity = self._get_value('total equity')
        assets = self._get_value('total assets')
        patmi = attributable or pat

        if patmi and equity:
            avg_equity = self._get_avg_value('total equity')
            if avg_equity and avg_equity > 0:
                metrics['roe'] = round((patmi / avg_equity) * 100, 2)

        if pat and assets:
            avg_assets = self._get_avg_value('total assets')
            if avg_assets and avg_assets > 0:
                metrics['roa'] = round((pat / avg_assets) * 100, 2)

        return metrics

    def calculate_solvency(self) -> Dict:
        """Calculate solvency ratios"""
        current_assets = self._get_value('total current assets')
        current_liabilities = self._get_value('total current liabilities')
        inventory = self._get_value('inventories')
        total_liabilities = self._get_value('total liabilities')
        total_assets = self._get_value('total assets')

        metrics = {}

        # Current ratio
        if current_assets and current_liabilities and current_liabilities > 0:
            metrics['current_ratio'] = round(current_assets / current_liabilities, 2)

        # Quick ratio
        if current_assets and inventory and current_liabilities and current_liabilities > 0:
            metrics['quick_ratio'] = round((current_assets - inventory) / current_liabilities, 2)

        # Debt ratios
        if total_liabilities and total_assets and total_assets > 0:
            metrics['debt_to_assets'] = round((total_liabilities / total_assets) * 100, 2)

        # Net debt calculations
        borrowings = self._get_value('bank borrowings') or 0
        cash = self._get_value('cash and bank balances') or 0
        equity = self._get_value('total equity')

        net_debt = borrowings - cash
        if net_debt and equity and equity > 0:
            metrics['net_debt_to_equity'] = round(net_debt / equity, 2)

        if net_debt and equity:
            total_capital = equity + net_debt
            if total_capital > 0:
                metrics['gearing_ratio'] = round((net_debt / total_capital) * 100, 2)

        return metrics

    def calculate_growth(self) -> Dict:
        """Calculate YoY growth rates"""
        if not self.prior_fs_index:
            return {}

        metrics = {}

        growth_items = [
            ('revenue', 'revenue_yoy_growth'),
            ('gross profit', 'gross_profit_yoy_growth'),
            ('profit before tax', 'pbt_yoy_growth'),
            ('profit for the financial year', 'pat_yoy_growth'),
            ('total assets', 'total_assets_yoy_growth'),
            ('total equity', 'equity_yoy_growth'),
        ]

        for label, metric_name in growth_items:
            current = self._get_value(label)
            prior = self._get_value(label, use_prior_index=True)

            if current and prior and prior > 0:
                growth = ((current - prior) / prior) * 100
                metrics[metric_name] = round(growth, 2)

        return metrics

    def calculate_cash_flow_quality(self) -> Dict:
        """Calculate cash flow quality metrics"""
        revenue = self._get_value('revenue')
        ocf = self._get_value('net cash from operating activities')

        metrics = {}

        if ocf and revenue and revenue > 0:
            metrics['ocf_to_revenue'] = round((ocf / revenue) * 100, 2)

        # Free cash flow = OCF - capex
        # Capex is usually negative in cash flow statement
        investing_cf = self._get_value('net cash used in investing activities')
        if ocf and investing_cf:
            capex = abs(investing_cf)  # Convert negative to positive
            metrics['free_cash_flow'] = round(ocf - capex, 2)

        # Interest coverage = OCF / interest_paid
        interest_paid = self._get_value('interest paid')
        if ocf and interest_paid and interest_paid > 0:
            metrics['interest_coverage'] = round(ocf / interest_paid, 2)

        # OCF to debt
        total_debt = self._get_value('bank borrowings')
        if ocf and total_debt and total_debt > 0:
            metrics['ocf_to_debt'] = round((ocf / total_debt) * 100, 2)

        return metrics

    def calculate_working_capital(self) -> Dict:
        """Calculate working capital efficiency metrics"""
        revenue = self._get_value('revenue')
        cogs = self._get_value('cost of sales')
        receivables = self._get_value('trade receivables')
        payables = self._get_value('trade payables')
        inventory = self._get_value('inventories')
        total_assets = self._get_value('total assets')

        metrics = {}

        # Receivables days
        if receivables and revenue and revenue > 0:
            metrics['receivables_days'] = round((receivables / revenue) * 365, 1)

        # Payables days
        if payables and cogs and cogs > 0:
            metrics['payables_days'] = round((payables / cogs) * 365, 1)

        # Inventory days
        if inventory and cogs and cogs > 0:
            metrics['inventory_days'] = round((inventory / cogs) * 365, 1)

        # Asset turnover
        if revenue and total_assets and total_assets > 0:
            metrics['asset_turnover'] = round(revenue / total_assets, 2)

        return metrics

    # Helper methods
    def _get_value(self, label: str, use_prior_index: bool = False) -> Optional[float]:
        """Extract value from fs_index with flexible matching"""
        index = self.prior_fs_index if use_prior_index else self.fs_index
        if not index:
            return None

        # Try exact match first
        for key, item in index.line_items.items():
            if label.lower() == key.lower():
                return item.get('group_current')

        # Try substring match
        for key, item in index.line_items.items():
            if label.lower() in key.lower():
                return item.get('group_current')

        return None

    def _get_avg_value(self, label: str) -> Optional[float]:
        """Get average of current and prior year values"""
        current = self._get_value(label, use_prior_index=False)
        prior = self._get_value(label, use_prior_index=True)

        if current and prior:
            return (current + prior) / 2
        elif current:
            return current
        elif prior:
            return prior
        return None
```

---

### 2. Add CLI Command: `finanalysis calculate`

```python
# In cli.py
@cli.command()
@click.argument('fs_index_path', type=click.Path(exists=True))
@click.option('--prior', '-p', type=click.Path(exists=True), help='Prior year fs_index.json')
@click.option('--output', '-o', default=None, help='Output JSON file')
def calculate(fs_index_path: str, prior: str, output: str):
    """Calculate derived financial metrics from fs_index.json

    Example:
        finanalysis calculate output/CHINHIN/2024/fs_index.json \\
            --prior output/CHINHIN/2023/fs_index.json \\
            --output output/CHINHIN/2024/metrics.json
    """
    from .fs_index import FSIndex
    from .calculators.metrics import MetricsCalculator

    fs_index = FSIndex.load(Path(fs_index_path))
    prior_fs_index = FSIndex.load(Path(prior)) if prior else None

    calculator = MetricsCalculator(fs_index, prior_fs_index)
    metrics = calculator.calculate_all()

    output_data = {
        "company": fs_index.company_name,
        "fiscal_year_end": fs_index.fiscal_year_end,
        "currency": fs_index.currency,
        "metrics": metrics.model_dump(exclude_none=True),
        "source_file": str(fs_index_path),
        "calculated_at": datetime.now().isoformat()
    }

    if output:
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        click.echo(f"✓ Metrics saved to {output}")
    else:
        click.echo(json.dumps(output_data, indent=2))
```

---

### 3. Integration with Pipeline

Update `pipeline.py` to automatically calculate metrics after FSIndex:

```python
# In pipeline.py, after Stage 4
if fs_index.line_items:
    fs_index.save(output / "fs_index.json")

    # Stage 4b: Calculate derived metrics
    logger.info("Calculating derived financial metrics")
    prior_fs_index_path = output.parent / str(int(output.name) - 1) / "fs_index.json"
    prior_fs_index = None
    if prior_fs_index_path.exists():
        prior_fs_index = FSIndex.load(prior_fs_index_path)

    calculator = MetricsCalculator(fs_index, prior_fs_index)
    metrics = calculator.calculate_all()
    metrics.save(output / "metrics.json")
```

---

## Metrics Coverage

With this implementation, we'll provide:

✅ **23 raw line items** from fs_index.json
✅ **30+ calculated metrics** including:
- 6 profitability ratios (margins, ROE, ROA)
- 5 solvency ratios (current, quick, debt ratios, gearing)
- 6 growth metrics (YoY changes)
- 4 cash flow quality metrics
- 4 working capital efficiency metrics

✅ **Benchmark comparison** (optional):
```python
def compare_to_benchmarks(metrics: FinancialMetrics) -> Dict:
    """Compare calculated metrics to industry benchmarks"""
    benchmarks = {
        'current_ratio': {'min': 1.0, 'good': 1.5, 'excellent': 2.0},
        'gearing_ratio': {'max': 70, 'good': 50, 'excellent': 30},
        'roe': {'min': 5, 'good': 10, 'excellent': 15},
        # ... more benchmarks
    }
    # Return comparison results
```

---

## Example Output: `metrics.json`

```json
{
  "company": "CHINHIN",
  "fiscal_year_end": "2024-12-31",
  "currency": "MYR",
  "metrics": {
    "gross_margin": 16.15,
    "pbt_margin": 8.48,
    "pat_margin": 6.63,
    "attributable_margin": 3.53,
    "roe": 14.18,
    "roa": 4.81,
    "current_ratio": 1.32,
    "quick_ratio": 0.96,
    "debt_to_assets": 64.86,
    "net_debt_to_equity": 1.57,
    "gearing_ratio": 61.0,
    "revenue_yoy_growth": 58.1,
    "gross_profit_yoy_growth": 178.7,
    "pbt_yoy_growth": 45.7,
    "pat_yoy_growth": 32.4,
    "total_assets_yoy_growth": 41.2,
    "equity_yoy_growth": 6.3,
    "ocf_to_revenue": -1.85,
    "free_cash_flow": -60018.0,
    "interest_coverage": 0.76,
    "receivables_days": 89.2,
    "payables_days": 61.7,
    "asset_turnover": 0.73
  },
  "source_file": "output/CHINHIN/2024/fs_index.json",
  "calculated_at": "2026-03-14T18:00:00"
}
```

---

## Next Steps

1. **Create module**: `src/finanalysis/calculators/metrics.py`
2. **Add CLI command**: `finanalysis calculate`
3. **Integrate with pipeline**: Auto-calculate after FSIndex extraction
4. **Add benchmarks**: Industry benchmark comparison
5. **Update workers**: Financial analysis workers can use metrics.json instead of recalculating

This will transform our system from **raw data extraction** to **comprehensive financial analysis** matching professional reports like the YTL Corporation example.
