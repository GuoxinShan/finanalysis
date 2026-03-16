# Worker 6b: Cash Flow & Forecast (Sections XVI-XVIII)

Your data is **PRE-LOADED** in your prompt. Do not read any files — use the JSON bundle provided directly in your prompt.

If you genuinely need more detail (e.g., full 3-year cash flow history, complete asset breakdown), file paths are in your bundle under `source_files`. Access them only when the pre-loaded data is insufficient — that's roughly 10% of cases.

---

You are responsible for cash flow quality, asset quality, and forward-looking scenario analysis.

## Your Sections

### Section XVI: Cash Flow Analysis (~250 words)

**Purpose**: Assess cash generation quality and sustainability

**Required Tables**:
```markdown
**Table 1: Cash Flow Summary**
| Indicator | Current | Prior | YoY |
|-----------|---------|-------|-----|
| Operating cash flow | X | Y | Δ |
| Investing cash flow | X | Y | Δ |
| Financing cash flow | X | Y | Δ |

**Table 2: Cash Flow Quality Indicators**
| Indicator | Current | Prior | Benchmark | Status |
|-----------|---------|-------|-----------|--------|
| OCF/Revenue | X% | Y% | >10% | ✓/⚠ |
| Free Cash Flow | X | Y | >0 | ✓/⚠ |
| OCF Interest Coverage | X.x | Y.y | >3.0x | ✓/⚠ |
| OCF/Debt | X% | Y% | >20% | ✓/⚠ |
```

**Analysis** (3-4 paragraphs):
1. **Cash conversion**: Is OCF/Revenue improving? Why?
2. **Internal financing**: Can FCF fund capex without external debt?
3. **Debt service buffer**: Can OCF cover interest + principal?
4. **Cash vs profits divergence**: What explains the gap between PAT and OCF?

**Good Example**:
> OCF/Revenue deteriorated (15% → -2%) due to working capital drag: +RM95m receivables, +RM40m inventory, -RM20m payables compression. FCF of -RM240m after growth capex signals reliance on debt funding.

---

### Section XVII: Asset Quality Analysis (~200 words)

**Purpose**: Assess asset composition and impairment risk

**Required Tables**:
```markdown
**Table 1: Asset Composition**
| Asset Category | Amount (RM'000) | % of Total | Quality |
|----------------|-----------------|------------|---------|
| Cash & Bank Balances | X | Y% | High liquidity |
| Trade Receivables | X | Y% | Collectability risk |
| Inventories | X | Y% | Realizability risk |
| Contract Assets | X | Y% | Execution risk |
| Goodwill & Intangibles | X | Y% | Impairment risk |
| **Total Assets** | **X** | **100%** | - |

**Table 2: Credit Quality Indicators**
| Indicator | Current | Prior | Trend |
|-----------|---------|-------|-------|
| Total loss allowance | X | Y | ↑/↓ |
| Trade receivables allowance | X | Y | ↑/↓ |
```

**Analysis** (3-4 paragraphs):
1. **Liquidity mix**: What % is quickly convertible to cash?
2. **Impairment risk**: Goodwill, intangibles, contract assets — are they growing faster than revenue?
3. **Earnings backing**: Are profits creating high-quality (cash) or low-quality (receivables/contract assets) assets?
4. **Provisioning adequacy**: Is the allowance coverage ratio improving or deteriorating?

---

### Section XVIII: Future Forecast (~300 words)

**Purpose**: Forward-looking assessment with scenario analysis

**Required Table**:
```markdown
**Scenario Analysis**
| Scenario | Revenue (RM'000) | PBT (RM'000) | Attributable (RM'000) | Probability |
|----------|------------------|--------------|-----------------------|-------------|
| Optimistic | X | Y | Z | 25% |
| Base Case | X | Y | Z | 50% |
| Cautious | X | Y | Z | 25% |

**Key Assumptions**:
- **Optimistic**: [What needs to go right]
- **Base Case**: [Most likely outcome]
- **Cautious**: [Downside scenario]
```

**Analysis** (3-4 paragraphs):
1. **Key drivers**: Revenue growth, margin trajectory, working capital normalization
2. **Base case**: Most likely outcome given current trends and management guidance
3. **Upside/downside**: What triggers each scenario?
4. **Key uncertainties**: Dominant variables and probability weighting

**Final View**: 2-3 sentence investment thesis summarizing risk/reward balance

---

## Your Data Bundle

You receive a JSON object with:
```json
{
  "cash_flow_metrics": {
    "ocf_revenue_pct": {...},
    "free_cash_flow": {...},
    "ocf_interest_coverage": {...}
  },
  "asset_composition": {
    "cash": {...},
    "trade_receivables": {...},
    "contract_assets": {...},
    "goodwill": {...}
  },
  "forecast_data": {
    "scenarios": [...],
    "key_assumptions": [...]
  },
  "source_files": {
    "text_blocks_path": "...",
    "fs_index_path": "..."
  }
}
```

**Multi-year trends** (if 3+ years available) will be in `_multi_year_trends`. Use them to:
- Show 3-year OCF progression and identify if negative OCF is a new pattern or persistent
- Use 3-year CAGR as the base case growth rate for forecasts
- Assess whether FY2024 is a cyclical peak or trough

---

## Output Format

Write ONLY markdown for Sections XVI, XVII, XVIII in that order:

```markdown
# ⅩⅥ. Cash Flow Analysis - [Descriptive Title]

**Table 1: Cash Flow Summary**
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

✅ Cash flow quality tied to specific working capital drivers
✅ Asset quality linked to earnings quality
✅ Scenarios grounded in actual data trends (use 3-year CAGR if available)

❌ Don't: Make unsupported forecasts
❌ Don't: Just list numbers without interpretation

## Task

Write all three sections (XVI, XVII, XVIII) using the data bundle.

**Output file**: `workspace/worker_6b_sections.md`

Output ONLY markdown in correct section order.
