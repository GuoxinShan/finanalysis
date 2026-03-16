# Worker 4: Operational Health

## Data Access

Your data is **PRE-LOADED** in your prompt. All financial metrics you need are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

---

## Canonical Data Ownership

**You own**: D/E ratio, gearing ratio, current ratio, quick ratio, bank borrowings, working capital metrics.
**Do NOT restate**: Revenue or profit figures (Section V), OCF (Section XVI), expense details (Section XI).

---

## Your Task

Write your sections using the data bundle.

**Output file**: `workspace/worker_4_sections.md`

Output ONLY markdown for your assigned sections.

---

**Role:** Analyze solvency, capital structure, working capital efficiency, and operational metrics.

**Tone:** Professional, objective, specific. See [writing_guidelines.md](writing_guidelines.md).

---

## Section XIV: Solvency & Capital Structure

### XIV.1 Debt Structure & Scale

**Debt Profile**

| Component | FY2024 (RM'000) | FY2023 (RM'000) | Change |
|-----------|-----------------|-----------------|--------|
| Bank borrowings non-current | [value] | [value] | [%] |
| Bank borrowings current | [value] | [value] | [%] |
| Lease liabilities non-current | [value] | [value] | [%] |
| Lease liabilities current | [value] | [value] | [%] |
| **Total debt** | **[sum]** | **[sum]** | **[%]** |
| Cash & bank balances | [value] | [value] | [%] |
| **Net debt** | **[total debt - cash]** | **[total debt - cash]** | **[%]** |

**Insight:** [2-3 sentences analyzing the net cash/net debt position, debt composition between bank borrowings and lease liabilities, maturity profile between current and non-current, and any YoY shifts in the overall debt posture. Explain why the debt position changed.]

### XIV.2 Short-term Liquidity

**Liquidity Position**

| Metric | FY2024 | FY2023 | Change | Benchmark |
|--------|--------|--------|--------|-----------|
| Current ratio | X.XXx | Y.YYx | +/-Z | >1.0x healthy |
| Quick ratio | X.XXx | Y.YYx | +/-Z | >0.8x healthy |
| Cash to current assets | X% | Y% | +/-Zpp | — |
| Working capital (RM'000) | [value] | [value] | [%] | — |

**Insight:** [2-3 sentences analyzing liquidity adequacy, the balance between current assets and current liabilities, cash as a proportion of short-term assets, and whether working capital is strengthening or eroding. Address any near-term funding pressure.]

### XIV.3 Long-term Solvency

**Capital Structure**

| Metric | FY2024 | FY2023 | Change | Interpretation |
|--------|--------|--------|--------|----------------|
| Total liabilities to assets | X% | Y% | +/-Zpp | [Leverage level: conservative / moderate / aggressive] |
| Bank borrowings to assets | X% | Y% | +/-Zpp | [Debt intensity] |
| Net debt to equity | X.XXx | Y.YYx | +/-Z | [Leverage direction: deleveraging / steady / increasing] |
| Equity to assets | X% | Y% | +/-Zpp | [Financial cushion: strong / adequate / thin] |

**Interest Coverage**

| Metric | FY2024 | FY2023 | Change | Signal |
|--------|--------|--------|--------|--------|
| OCF / Finance costs | X.XXx | Y.YYx | +/-Z | [Adequate / Tight / Insufficient] |
| PBT / Finance costs | X.XXx | Y.YYx | +/-Z | [Comfortable / Stressed / Critical] |

**Insight:** [2-3 sentences analyzing capital structure direction, leverage sustainability, interest coverage comfort level, and the relationship between operating cash flow and debt service burden. Flag any structural risk from rising leverage or weakening coverage.]

### XIV.4 Key Findings & Tracking

**Key Findings**

| Finding | Data | Interpretation |
|---------|------|----------------|
| [e.g., "Liquidity position"] | [Current ratio: X.XX -> Y.YY] | [Improving / Deteriorating -- why?] |
| [e.g., "Leverage direction"] | [D/E or gearing + change] | [Debt-funded growth or deleveraging?] |
| [e.g., "Interest burden"] | [Finance costs + coverage ratios] | [Comfortable / Stretched] |
| [e.g., "Refinancing risk"] | [Current borrowings as % of total debt] | [Near-term pressure?] |

**Chart: Leverage Profile**

```mermaid
xychart-beta
    title "Key Solvency Ratios"
    x-axis [FY2023, FY2024]
    y-axis "Ratio / %" 0 --> [max_rounded_up]
    bar [current_ratio_fy2023, current_ratio_fy2024]
    bar [debt_to_assets_fy2023_pct, debt_to_assets_fy2024_pct]
    bar [gearing_fy2023_pct, gearing_fy2024_pct]
```

[1 sentence on overall financial health.]

**Tracking Recommendations:**
- [Specific item to monitor related to debt or liquidity, e.g., "Monitor bank borrowing maturity profile for refinancing needs in the next 12 months"]
- [Specific item related to leverage trends, e.g., "Track net debt-to-equity trajectory against industry benchmarks"]
- [Specific item related to interest coverage, e.g., "Watch OCF-to-finance-costs ratio for early warning of debt service stress"]

---

## Section XV: Working Capital Efficiency

### XV.1 Cash Conversion Cycle

**Working Capital Days**

| Metric | FY2024 | FY2023 | Change | Direction |
|--------|--------|--------|--------|-----------|
| Receivables days | X days | Y days | +/-Z days | Faster / Slower collection |
| Payables days | X days | Y days | +/-Z days | Stretching / Paying faster |
| Inventory days | X days | Y days | +/-Z days | Leaner / Building stock |
| **Cash conversion cycle** | **X days** | **Y days** | **+/-Z days** | **Improving / Worsening** |

**Chart: Working Capital Cycle (Days)**

```mermaid
xychart-beta
    title "Working Capital Cycle"
    x-axis [FY2023, FY2024]
    y-axis "Days" 0 --> [max_days_rounded_up]
    bar [receivables_days_fy2023, receivables_days_fy2024]
    bar [payables_days_fy2023, payables_days_fy2024]
    bar [inventory_days_fy2023, inventory_days_fy2024]
```

**Insight:** [2-3 sentences analyzing cash conversion cycle direction, what is driving the change (collection efficiency, supplier payment timing, inventory build-up), and whether the cycle is improving capital efficiency or tying up more cash in operations.]

### XV.2 Working Capital Components

**Working Capital Components**

| Component | FY2024 (RM'000) | FY2023 (RM'000) | Change | % of Revenue |
|-----------|-----------------|-----------------|--------|-------------|
| Trade receivables | [value] | [value] | [%] | [%] |
| Trade payables | [value] | [value] | [%] | [%] |
| Inventories | [value] | [value] | [%] | [%] |
| **Net working capital** | **[receivables + inventories - payables]** | **[value]** | **[%]** | **[%]** |

**Receivables Quality**

| Metric | FY2024 | FY2023 | Change | Signal |
|--------|--------|--------|--------|--------|
| Trade receivables / Revenue | X% | Y% | +/-Zpp | [Normal / Elevated / Concerning] |
| Receivables growth vs Revenue growth | [X%] | [Y%] | — | [Aligned / Outpacing revenue] |

**Insight:** [2-3 sentences analyzing working capital component changes, receivables quality (whether receivables are growing in line with or faster than revenue suggesting collection risk), inventory management, and net working capital adequacy.]

### XV.3 Efficiency Assessment & Tracking

**Efficiency Assessment**

| Metric | FY2024 | FY2023 | Trend | Signal |
|--------|--------|--------|-------|--------|
| Collection efficiency | [Receivables days] | [Receivables days] | [improving / deteriorating] | [Faster / Slower collection] |
| Inventory management | [Inventory days] | [Inventory days] | [improving / deteriorating] | [Leaner / Building stock] |
| Supplier credit utilization | [Payables days] | [Payables days] | [improving / deteriorating] | [Stretching / Paying faster] |
| Cash conversion cycle | [Sum of above] | [Sum of above] | [improving / deteriorating] | [Improving / Worsening] |

[1 sentence on working capital dynamics.]

**Tracking Recommendations:**
- [Specific item to monitor related to receivables, e.g., "Monitor trade receivables-to-revenue ratio for signs of collection deterioration"]
- [Specific item related to inventory, e.g., "Track inventory days against revenue growth to detect unwanted stock build-up"]
- [Specific item related to cash conversion cycle, e.g., "Watch cash conversion cycle trend for impact on operating cash flow generation"]

---

## Output Format Summary

This worker produces two sections, each structured into sub-sections with layered analysis:

### Section XIV: Solvency & Capital Structure
1. **XIV.1 Debt Profile Table** — Component-level debt breakdown with cash offset and net debt
2. **Insight** — 2-3 sentence analysis of debt position and composition
3. **XIV.2 Liquidity Position Table** — Current ratio, quick ratio, cash ratio, working capital with benchmarks
4. **Insight** — 2-3 sentence analysis of short-term liquidity adequacy
5. **XIV.3 Capital Structure Table** — Leverage and solvency ratios with interpretation
6. **XIV.3 Interest Coverage Table** — OCF and PBT coverage of finance costs
7. **Insight** — 2-3 sentence analysis of long-term solvency and debt service capacity
8. **XIV.4 Key Findings Table** — 4 rows: Finding / Data / Interpretation
9. **Leverage Profile Chart** — Mermaid `xychart-beta` grouped bar chart (current ratio, debt-to-assets, gearing)
10. **1-sentence overall health summary**
11. **Tracking Recommendations** — 3 specific monitoring items

### Section XV: Working Capital Efficiency
1. **XV.1 Working Capital Days Table** — Receivables, payables, inventory days, cash conversion cycle
2. **Working Capital Cycle Chart** — Mermaid `xychart-beta` grouped bar chart
3. **Insight** — 2-3 sentence analysis of cash conversion dynamics
4. **XV.2 Working Capital Components Table** — Absolute values with % of revenue
5. **XV.2 Receivables Quality Table** — Receivables-to-revenue and growth alignment
6. **Insight** — 2-3 sentence analysis of working capital component trends
7. **XV.3 Efficiency Assessment Table** — 4 rows: Metric / FY2024 / FY2023 / Trend / Signal
8. **1-sentence working capital dynamics summary**
9. **Tracking Recommendations** — 3 specific monitoring items

### Formatting Rules
- All monetary values in RM'000 in tables
- Percentages to 1 decimal place, bps for small changes (<1pp)
- Ratios to 2 decimal places with "x" suffix (e.g., 1.67x)
- Trend arrows: `improving` / `deteriorating` (no ambiguous symbols)
- Tables use `✅` for healthy signals, `⚠️` for concerns, `❌` for critical issues
- Mermaid charts use actual computed data values, never placeholders
- Reference [writing_guidelines.md](writing_guidelines.md) for tone and precision rules
