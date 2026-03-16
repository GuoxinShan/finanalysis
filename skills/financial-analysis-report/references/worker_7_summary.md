# Worker 7: Executive Summary & Investment View

## Data Access

Your data is **PRE-LOADED** in your prompt. All financial metrics you need are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

---

## Canonical Data Ownership

**You own**: Executive summary synthesis, investment thesis.
**Do NOT restate**: Detailed metrics — reference section numbers. Do NOT add new analysis not present in Sections I-XVIII.

---

## Your Task

Write the executive summary using the data bundle and assembled report.

**Output file**: `workspace/summary.md`

Output ONLY markdown.

---

You are a financial analysis worker. Your job: synthesize all section outputs into a concise executive summary with visual-first tables and charts, minimal prose. You receive completed section outputs from Workers 1-6b.

## Input

You receive a JSON object containing pre-extracted data from all prior workers:

| Field | Source | Unit |
|-------|--------|------|
| `revenue`, `gross_profit`, `pbt`, `pat`, `patmi` | Worker outputs | RM'000 |
| `total_assets`, `total_equity`, `total_liabilities` | Worker outputs | RM'000 |
| `operating_cash_flow`, `free_cash_flow` | Worker 6b | RM'000 |
| `eps` (sen) | Worker outputs | sen |
| `roe`, `roa`, `gross_margin`, `net_margin` | Worker outputs | % |
| `current_ratio`, `debt_to_equity` | Worker outputs | ratio |
| `revenue_growth`, `pat_growth`, `eps_growth` | Worker outputs | % |
| Prior year equivalents | Same fields with `_prior` suffix | same |
| Section summaries | Workers 1-6b | text |

**All amounts are in RM'000. Convert to RM million (divide by 1000) for display.**

---

## Section 1: Key Conclusions

### 1.1 Visual Overview

**Chart: Key Metrics Overview**

```mermaid
xychart-beta
    title "Core Metrics Comparison"
    x-axis [Revenue, Gross Profit, PBT, PAT, OCF]
    y-axis "RM million" 0 --> [round max value up to clean number]
    bar [current_values]
```

### 1.2 Headline Numbers

| Metric | FY2023 | FY2024 | Change |
|--------|--------|--------|--------|
| Revenue | [RM X] | [RM X] | [+/- X%] |
| Gross Profit | [RM X] | [RM X] | [+/- X%] |
| PATMI | [RM X] | [RM X] | [+/- X%] |
| EPS | [RM X.XX] | [RM X.XX] | [+/- X%] |
| Total Assets | [RM X] | [RM X] | [+/- X%] |
| Total Equity | [RM X] | [RM X] | [+/- X%] |
| OCF | [RM X] | [RM X] | [+/- X%] |
| Net Debt | [RM X] | [RM X] | [+/- X%] |

### 1.3 Key Takeaways

- **Revenue**: [1 sentence on growth drivers]
- **Profitability**: [1 sentence on margin trajectory]
- **Balance sheet**: [1 sentence on financial health]
- **Cash flow**: [1 sentence on cash generation quality]
- **Outlook**: [1 sentence on forward view]

---

## Section 2: Profitability Snapshot

| Ratio | FY2023 | FY2024 | Change | Signal |
|-------|--------|--------|--------|--------|
| Gross Margin | [X]% | [X]% | [+/- X pp] | Expanding / Compressing |
| PBT Margin | [X]% | [X]% | [+/- X pp] | Expanding / Compressing |
| Net Margin | [X]% | [X]% | [+/- X pp] | Expanding / Compressing |
| ROE | [X]% | [X]% | [+/- X pp] | Improving / Declining |
| ROA | [X]% | [X]% | [+/- X pp] | Improving / Declining |
| EPS Growth | [X]% | [X]% | [+/- X pp] | Accelerating / Decelerating |

**Margin quality note**: [1 sentence on whether margin changes are revenue-driven or cost-driven.]

---

## Section 3: Trend Analysis

### 3.1 Metrics Trend Table

| Metric | FY2023 | FY2024 | Direction |
|--------|--------|--------|-----------|
| Revenue | [RM X] | [RM X] | Up / Down / Flat |
| Total Assets | [RM X] | [RM X] | Up / Down / Flat |
| Total Equity | [RM X] | [RM X] | Up / Down / Flat |
| OCF | [RM X] | [RM X] | Up / Down / Flat |
| Net Debt | [RM X] | [RM X] | Up / Down / Flat |
| EPS | [RM X.XX] | [RM X.XX] | Up / Down / Flat |

### 3.2 Trend Chart

**Chart: Trend Direction**

```mermaid
xychart-beta
    title "Key Metrics Trend (RM million)"
    x-axis [Total Assets, Total Equity, OCF]
    y-axis "RM million" 0 --> [round max value up to clean number]
    bar [prior_values]
    bar [current_values]
```

---

## Section 4: Financial Health Scorecard

| Dimension | Metric | Value | Assessment |
|-----------|--------|-------|------------|
| Liquidity | Current Ratio | [X.XX]x | Strong / Adequate / Weak |
| Solvency | Debt-to-Equity | [X.XX]x | Conservative / Moderate / Leveraged |
| Cash Generation | OCF/Revenue | [X]% | Strong / Adequate / Weak |
| Dividend | Dividend Yield | [X]% | Attractive / Moderate / Low |
| Efficiency | Asset Turnover | [X.XX]x | High / Average / Low |

**Overall financial health**: [1 sentence summarizing the strongest and weakest dimensions.]

---

## Section 5: Investment Thesis

| Factor | View | Evidence |
|--------|------|----------|
| Growth | Positive / Neutral / Negative | [Key data point] |
| Profitability | Positive / Neutral / Negative | [Key data point] |
| Balance Sheet | Positive / Neutral / Negative | [Key data point] |
| Cash Flow | Positive / Neutral / Negative | [Key data point] |
| Valuation (if available) | Attractive / Fair / Expensive | [Key data point] |

**Key risks**:
- [Risk 1]
- [Risk 2]

**Catalysts**:
- [Catalyst 1]
- [Catalyst 2]

**Conclusion**: [2-3 sentence investment thesis summarizing risk/reward balance.]

---

## Section 6: Tracking Recommendations

| Priority | Metric | Current Value | Watch For |
|----------|--------|---------------|-----------|
| 1 | [Most critical metric from Section V] | [FY2024 value] | [What change would signal concern/improvement] |
| 2 | [Second most critical metric from Section XIV/XVI] | [FY2024 value] | [What change would signal concern/improvement] |
| 3 | [Third most critical metric from Section IX/XII] | [FY2024 value] | [What change would signal concern/improvement] |
| 4 | [Fourth most critical metric from Section XV] | [FY2024 value] | [What change would signal concern/improvement] |
| 5 | [Fifth most critical metric from Section XIII] | [FY2024 value] | [What change would signal concern/improvement] |

**Priority monitoring**: [1-2 sentence recommendation on which metrics deserve closest attention in the next reporting period.]

---

## Output Format

Your output MUST follow this structure exactly:

1. **Section 1: Key Conclusions**
   - 1.1 Mermaid xychart-beta: "Core Metrics Comparison" (single-series bar chart)
   - 1.2 Headline numbers table (8 metrics)
   - 1.3 5 bullet key takeaways

2. **Section 2: Profitability Snapshot**
   - Profitability ratios table (6 ratios with signals)

3. **Section 3: Trend Analysis**
   - 3.1 Metrics trend table (6 metrics with direction arrows)
   - 3.2 Mermaid xychart-beta: "Key Metrics Trend" (grouped bar: prior vs current)

4. **Section 4: Financial Health Scorecard**
   - Scorecard table (5 dimensions with assessments)

5. **Section 5: Investment Thesis**
   - Factor view table (5 factors)
   - 2 bullet key risks
   - 2 bullet catalysts
   - 2-3 sentence conclusion

6. **Section 6: Tracking Recommendations**
   - Priority metrics table (5 metrics with watch-for guidance)
   - 1-2 sentence priority monitoring recommendation

### Chart Rules

- All xychart-beta: use `bar` for absolute values
- y-axis max: round the largest data value up to the next clean number (e.g., 350 -> 400, 12.5 -> 15)
- Every chart must have a `title`
- If prior year data is unavailable, use only current year in charts (single bar/point)

### Anti-Fabrication

Every number must come from the data bundle. If a field is missing, write "N/A" in the table and exclude from charts. Never interpolate or estimate.
