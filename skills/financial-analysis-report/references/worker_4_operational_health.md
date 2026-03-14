# Worker 4: Operational Health (Sections XIV-XV)

You are responsible for assessing the company's financial health and operational efficiency.

## Your Sections

### Section ⅩⅣ: Solvency Analysis (~250 words)

**Purpose**: Assess short-term and long-term financial health

**Two tables**:
```markdown
**Short-Term Solvency**
| Ratio | Current | Benchmark | Status |
|-------|---------|-----------|--------|
| Current Ratio | X.xXx | >1.5x | ✓/⚠ |
| Quick Ratio | X.xXx | >1.0x | ✓/⚠ |
| Working Capital (RM'000) | X | >0 | ✓/⚠ |

**Long-Term Solvency**
| Ratio | Current | Benchmark | Status |
|-------|---------|-----------|--------|
| Liabilities/Assets | X% | <60% | ✓/⚠ |
| Borrowings/Assets | X% | <40% | ✓/⚠ |
| Net Debt/Equity | X.xXx | <1.0x | ✓/⚠ |
```

**Insights to develop**:
1. **Liquidity cushion**: Can they meet short-term obligations?
2. **Refinancing risk**: Debt maturity profile and rollover needs
3. **Debt service capacity**: Cash flow vs. interest/principal payments
4. **Covenant headroom**: Breathing room before covenant breach

**Conclusion**: Overall solvency profile (strong/adequate/stretched)

---

### Section ⅩⅤ: Operational Capability Analysis (~200 words)

**Purpose**: Assess working capital efficiency

**Table**:
```markdown
| Indicator | Current | Prior | Benchmark | Status |
|-----------|---------|-------|-----------|--------|
| Receivables Days | X | Y | 90 days | ✓/⚠ |
| Payables Days | X | Y | 60 days | ✓/⚠ |
| Asset Turnover | X.xXx | Y.yYy | - | ▲/▼/— |
```

**Insights to develop**:
1. **Collection efficiency**: Are receivables days improving or deteriorating? Why?
2. **Supplier credit utilization**: Extending payables (good) or delaying payments (stress signal)?
3. **Asset productivity**: Is asset turnover improving (better utilization)?
4. **Working capital cycle**: Cash conversion efficiency

**Example**:
> Receivables days extended from 90 to 106 days, primarily in East Malaysian operations (Sabah: 130 days vs. Peninsula: 85 days), reflecting:
> - **New customer credit**: Aggressive terms to gain market share
> - **Collection delays**: Less established relationships, slower payment culture
> - **Risk signal**: Potential bad debts if economic conditions worsen
>
> This working capital drag explains negative operating cash flow despite accounting profits.

---

## Your Data Bundle

You will receive a JSON object with:

```json
{
  "solvency_ratios": {
    "current_ratio": {"current": 1.32, "benchmark": 1.5, "status": "⚠"},
    "quick_ratio": {"current": 0.89, "benchmark": 1.0, "status": "⚠"},
    "working_capital": {"current": 125000, "status": "✓"},
    "liabilities_to_assets": {"current": 65, "benchmark": 60, "status": "⚠"},
    "borrowings_to_assets": {"current": 35, "benchmark": 40, "status": "✓"},
    "net_debt_to_equity": {"current": 0.95, "benchmark": 1.0, "status": "⚠"}
  },
  "operational_metrics": {
    "receivables_days": {"current": 106, "prior": 90, "benchmark": 90, "status": "⚠"},
    "payables_days": {"current": 62, "prior": 48, "benchmark": 60, "status": "✓"},
    "asset_turnover": {"current": 0.73, "prior": 0.65, "status": "▲"}
  }
}
```

## Output Format

Write **ONLY** the markdown content for Sections XIV-XV. Use this exact structure:

```markdown
## ⅩⅣ. Solvency Analysis

**Short-Term Solvency**
[Fill in from data bundle]

**Long-Term Solvency**
[Fill in from data bundle]

### Solvency Assessment

[Your insights here]

## ⅩⅤ. Operational Capability Analysis

[Fill in from data bundle]

### Working Capital Efficiency

[Your insights here]
```

## Quality Standards

- ✅ Use actual ratios from data bundle
- ✅ Compare against benchmarks
- ✅ Explain implications for financial health
- ✅ Connect to cash flow analysis

**Do NOT**:
- ❌ Recalculate ratios (use provided values)
- ❌ Ignore warning signs
- ❌ Make generic statements

## Task

Using the data bundle provided, write Sections XIV-XV following the guidelines above. Output ONLY the markdown for these two sections.
