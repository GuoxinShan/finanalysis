# Worker 6: Risk & Cash Flow Analysis (Sections IX-XI, XVI-XVIII)

You handle 6 sections covering risk, cash flow, and forward forecast. Be thorough but concise - focus on actionable insights.

## Your Sections

### Section IX: Risk Scan (250 words)

**Purpose**: Identify and assess key risks

**Required Tables**:
```markdown
**Table 1: Financial Risks**
| Risk Area | Current Level | Threshold | Severity |
|-----------|---------------|-----------|----------|
| Leverage | Liabilities/Assets: 65% | Covenant: 70% | Medium |
| Liquidity | Current Ratio: 1.32x | Min: 1.0x | Low |
| Margin | Attributable: 3.5% | Breakeven: 2% | Medium |

**Table 2: Non-Financial Risks**
| Risk Type | Description | Probability | Impact |
|-----------|-------------|-------------|--------|
| Execution | East Malaysia receivables | High | Medium |
| Market | Steel price volatility | Medium | High |
| Regulatory | Environmental compliance | Low | High |
```

**Analysis** (3-4 paragraphs):
- Top 3-5 risks by severity and controllability
- Internal (execution, credit) vs external (macro, commodity)
- Mitigation measures and early warning indicators
- Overall risk profile (conservative/moderate/aggressive)

**Good Example**:
> Leverage (65% vs 70% covenant) and margin compression (3.5% attributable) are the most severe risks. While liquidity appears adequate (1.32x current ratio), receivables quality in new markets is the early warning indicator - DSO increased from 45 to 72 days in East Malaysia.

---

### Section X: Major Items in Three Statements (300 words)

**Purpose**: Deep dive into balance sheet, income statement, and cash flow

**Required Tables**:
```markdown
**Balance Sheet Summary**
| Item | Current | Prior | YoY % |
|------|---------|-------|-------|
| Total Assets | X | Y | +Z% |
| Total Liabilities | X | Y | +Z% |
| Total Equity | X | Y | +Z% |
| Net Debt | X | Y | Δ |

**Income Statement Summary**
| Item | Current | Prior | YoY % |
|------|---------|-------|-------|
| Revenue | X | Y | +Z% |
| Operating Expenses | X | Y | +Z% |
| PBT | X | Y | +Z% |
| PAT | X | Y | +Z% |

**Cash Flow Summary**
| Item | Current | Prior | Δ |
|------|---------|-------|---|
| Operating Cash Flow | X | Y | Δ |
| Investing Cash Flow | X | Y | Δ |
| Financing Cash Flow | X | Y | Δ |
| Net Cash Change | X | Y | Δ |
```

**Analysis** (1 paragraph per statement):
- **Balance sheet**: Asset/liability growth balance, capital structure changes
- **Income statement**: Revenue quality, cost structure, margin drivers
- **Cash flow**: Operating cash generation, investment intensity, financing needs
- **Synthesis**: Are profits backed by cash? Is growth funded sustainably?

**Good Example**:
> Despite PAT of RM215m, OCF was negative (-RM60m) due to RM95m receivables buildup and RM40m inventory expansion. FCF (after RM180m growth capex) was -RM240m, requiring debt funding.

---

### Section XI: Expense Analysis (200 words)

**Purpose**: Understand cost structure and efficiency

**Required Table**:
```markdown
| Expense Item | Amount (RM'000) | % of Revenue | YoY Change |
|--------------|-----------------|--------------|------------|
| Cost of Sales | X | Y% | Δ |
| Distribution Expenses | X | Y% | Δ |
| Administrative Expenses | X | Y% | Δ |
| Finance Costs | X | Y% | Δ |
| Taxation | X | Z% (of PBT) | Δ |
```

**Analysis** (3-4 paragraphs):
1. **Cost control**: Are expenses growing slower than revenue?
2. **Interest burden**: Are finance costs manageable?
3. **Tax efficiency**: Effective vs statutory rate
4. **Fixed vs variable mix**: Operating leverage potential

**Good Example**:
> Cost of sales (84% of revenue) rose 2pp YoY from steel prices (+20% input, 12% passed through) and lower-margin East Malaysian sales (85% COS vs 80% Peninsula). Admin expenses grew slower than revenue (12% vs 58%), demonstrating operating leverage.

---

### Section XVI: Cash Flow Analysis (250 words)

**Purpose**: Assess cash generation quality

**Required Table**:
```markdown
| Indicator | Current | Prior | Benchmark | Status |
|-----------|---------|-------|-----------|--------|
| OCF/Revenue | X% | Y% | >10% | ✓/⚠ |
| Free Cash Flow (RM'000) | X | Y | >0 | ✓/⚠ |
| OCF Interest Coverage | X.xXx | Y.yYy | >3.0x | ✓/⚠ |
| OCF/Debt | X% | Y% | >20% | ✓/⚠ |
```

**Analysis** (3-4 paragraphs):
1. **Cash conversion**: Is OCF/Revenue improving?
2. **Internal financing**: Can FCF fund capex?
3. **Debt service buffer**: Can OCF cover interest + principal?
4. **Cash vs profits divergence**: Why is OCF different from PAT?

**Good Example**:
> OCF/Revenue deteriorated (15% → -2%) due to working capital drag: +RM95m receivables, +RM40m inventory, -RM20m payables compression. FCF of -RM240m after growth capex signals reliance on debt funding.

---

### Section XVII: Asset Quality Analysis (200 words)

**Purpose**: Assess asset composition and impairment risk

**Required Table**:
```markdown
| Asset Category | Amount (RM'000) | % of Total | Quality |
|----------------|-----------------|------------|---------|
| Cash & Bank Balances | X | Y% | High liquidity |
| Trade Receivables | X | Y% | Collectability risk |
| Inventories | X | Y% | Realizability risk |
| Contract Assets | X | Y% | Execution risk |
| Goodwill & Intangibles | X | Y% | Impairment risk |
| **Total Assets** | **X** | **100%** | - |
```

**Analysis** (3-4 paragraphs):
1. **Liquidity mix**: What % is quickly convertible to cash?
2. **Impairment risk**: Goodwill, intangibles, contract assets
3. **Earnings backing**: Profits creating high-quality (cash) or low-quality (receivables) assets?
4. **Age analysis**: Receivables aging, inventory turnover

**Conclusion**: Asset quality and risk assessment

---

### Section XVIII: Future Forecast (300 words)

**Purpose**: Forward-looking assessment with scenarios

**Required Table**:
```markdown
**Scenario Analysis**
| Scenario | Revenue (RM'000) | PBT (RM'000) | Attributable (RM'000) | Probability |
|----------|------------------|--------------|-----------------------|-------------|
| Optimistic | X | Y | Z | 25% |
| Base Case | X | Y | Z | 50% |
| Cautious | X | Y | Z | 25% |

**Key Assumptions**:
- **Optimistic**: [Assumptions for upside case]
- **Base Case**: [Most likely outcome]
- **Cautious**: [Downside scenario assumptions]
```

**Analysis** (3-4 paragraphs):
1. **Key drivers**: Revenue growth, margin trajectory, working capital
2. **Base case**: Most likely outcome given current trends
3. **Upside/downside**: What needs to go right/wrong?
4. **Key uncertainties**: Dominant variables and probability weighting

**Final View**: 2-3 sentence investment thesis

---

## Your Data Bundle

You receive a JSON object with:
```json
{
  "risks": {
    "financial_risks": [...],
    "non_financial_risks": [...]
  },
  "balance_sheet": {...},
  "income_statement": {...},
  "cash_flow_statement": {...},
  "expenses": {...},
  "cash_flow_metrics": {...},
  "asset_composition": {...},
  "forecast_data": {
    "scenarios": [...],
    "key_assumptions": [...]
  }
}
```

## Output Format

Write ONLY markdown for Sections IX, X, XI, XVI, XVII, XVIII in that order. Use proper section headers.

## Quality Checklist

✅ Comprehensive risk assessment
✅ Connect cash flow to profitability
✅ Develop realistic scenarios
✅ Be forward-looking

❌ Don't: Ignore negative risks
❌ Don't: Make unsupported forecasts
❌ Don't: Just list numbers

## Task

Write all six sections using the data bundle. Output ONLY markdown in correct section order.
