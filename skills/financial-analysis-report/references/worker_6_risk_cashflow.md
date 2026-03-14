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

Write ONLY markdown for Sections IX, X, XI, XVI, XVII, XVIII in that order. Use this exact structure:

```markdown
# Ⅸ. Risk Scan - [Descriptive Title]

## Financial Risk Screening

**Table 1: Financial Risk Screening**
| Risk Category | FY2024 Disclosure Signal | Risk Implication |
|---|---|---|
| [Risk 1] | [Signal] | [Implication] |
| [Risk 2] | [Signal] | [Implication] |

**Insights**
1. [First insight on most severe financial risks]
2. [Second insight on liquidity and leverage]
3. [Third insight on sensitivity factors]
4. [Fourth insight on mitigation effectiveness]

## Non-Financial / Operating Risk Screening

**Table 2: Non-Financial and Operating Risk Screening**
| Risk Category | FY2024 Disclosure Signal | Risk Implication |
|---|---|---|
| [Risk 1] | [Signal] | [Implication] |
| [Risk 2] | [Signal] | [Implication] |

**Insights**
1. [First insight on operational risks]
2. [Second insight on concentration and execution]
3. [Third insight on regulatory factors]

**Conclusion**: [One paragraph on overall risk profile]

# Ⅹ. Analysis of Major Items in the Three Statements - [Descriptive Title]

## Balance Sheet

**Table 1: Balance Sheet Key Items**
| Item | FY2024 | FY2023 | YoY | Analytical Point |
|---|---:|---:|---:|---|
| Total assets | [Value] | [Value] | [+%] | [Point] |
| Total equity | [Value] | [Value] | [+%] | [Point] |
| Total liabilities | [Value] | [Value] | [+%] | [Point] |

**Insights**
1. [First insight on balance sheet expansion]
2. [Second insight on capital structure changes]
3. [Third insight on asset composition shifts]

## Income Statement

**Table 2: Income Statement Key Items**
| Item | FY2024 | FY2023 | YoY | Analytical Point |
|---|---:|---:|---:|---|
| Revenue | [Value] | [Value] | [+%] | [Point] |
| Gross profit | [Value] | [Value] | [+%] | [Point] |
| PBT | [Value] | [Value] | [+%] | [Point] |

**Insights**
1. [First insight on revenue quality]
2. [Second insight on operating leverage]
3. [Third insight on cost structure]

## Cash Flow Statement

**Table 3: Cash Flow Statement Key Items**
| Item | FY2024 | FY2023 | YoY | Analytical Point |
|---|---:|---:|---:|---|
| Net cash from operating activities | [Value] | [Value] | [+%] | [Point] |
| Net cash used in investing activities | [Value] | [Value] | [+%] | [Point] |
| Net cash from/(used in) financing activities | [Value] | [Value] | n.m. | [Point] |

**Insights**
1. [First insight on cash generation quality]
2. [Second insight on investment intensity]
3. [Third insight on funding hierarchy]

**Conclusion**: [One paragraph on overall statement quality]

# ⅩⅠ. Expense Analysis - [Descriptive Title]

**Table 1: Expense Structure and Cost Ratios**
| Expense Indicator | FY2024 | FY2023 | YoY / Change |
|---|---:|---:|---:|
| [Expense item] | [Value] | [Value] | [+%] |
| [Cost ratio] | [%] | [%] | [+ppt] |

**Insights**
1. [First insight on cost control effectiveness]
2. [Second insight on finance cost burden]
3. [Third insight on operating leverage potential]
4. [Fourth insight on fixed vs. variable mix]

**Conclusion**: [One paragraph on expense management quality]

# ⅩⅥ. Cash Flow Analysis - [Descriptive Title]

**Table 1: Cash Flow Indicators**
| Indicator (RM million) | FY2024 | FY2023 | YoY |
|---|---:|---:|---:|
| Operating cash flow | [Value] | [Value] | [+%] |
| Investing cash flow | [Value] | [Value] | [Direction] |
| Financing cash flow | [Value] | [Value] | [Direction] |

**Insights**
1. [First insight on operating cash generation]
2. [Second insight on investment funding]
3. [Third insight on financing reliance]

**Table 2: Cash Flow Quality Indicators**
| Indicator | FY2024 | FY2023 | Interpretation |
|---|---:|---:|---|
| OCF / revenue | [%] | [%] | [Interpretation] |
| FCF (OCF - PPE capex) | [Value] | [Value] | [Interpretation] |
| Interest paid | [Value] | [Value] | [Interpretation] |

**Insights**
1. [First insight on cash conversion quality]
2. [Second insight on internal funding capacity]
3. [Third insight on debt service capability]

**Conclusion**: [One paragraph on cash flow health]

# ⅩⅦ. Asset Quality Analysis - [Descriptive Title]

**Table 1: Asset Base Quality Indicators**
| Asset Item | FY2024 | FY2023 | Trend |
|---|---:|---:|---|
| Property, plant and equipment | [Value] | [Value] | [+%] |
| Intangible assets | [Value] | [Value] | [+%] |
| Contract assets | [Value] | [Value] | [+%] |

**Insights**
1. [First insight on asset composition]
2. [Second insight on productive vs. financial assets]
3. [Third insight on asset durability]

**Table 2: Credit Quality Indicators**
| Indicator | FY2024 | FY2023 | Trend |
|---|---:|---:|---|
| Total loss allowance | [Value] | [Value] | [Increased/Decreased] |
| Trade receivables allowance | [Value] | [Value] | [Increased/Decreased] |

**Insights**
1. [First insight on provisioning adequacy]
2. [Second insight on receivable quality]
3. [Third insight on collection risk]

**Conclusion**: [One paragraph on asset quality]

# ⅩⅧ. Future Forecast - [Descriptive Title]

[Opening paragraph explaining scenario approach]

Assumptions:
- **Optimistic**: [Assumptions]
- **Base case**: [Assumptions]
- **Conservative**: [Assumptions]

**Table 1: Scenario Forecast (FY2025E-FY2027E)**
| Scenario | Metric | FY2024 Base | FY2025E | FY2026E | FY2027E |
|---|---|---:|---:|---:|---:|
| Optimistic | Revenue (RM million) | [Value] | [Value] | [Value] | [Value] |
| Optimistic | PATMI (RM million) | [Value] | [Value] | [Value] | [Value] |
| Base case | Revenue (RM million) | [Value] | [Value] | [Value] | [Value] |
| Base case | PATMI (RM million) | [Value] | [Value] | [Value] | [Value] |
| Conservative | Revenue (RM million) | [Value] | [Value] | [Value] | [Value] |
| Conservative | PATMI (RM million) | [Value] | [Value] | [Value] | [Value] |

**Insights**
1. [First insight on scenario spread and sensitivity]
2. [Second insight on base case plausibility]
3. [Third insight on optimistic case requirements]
4. [Fourth insight on key monitoring triggers]

**Conclusion**: [One paragraph on forward-looking assessment]
```

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
