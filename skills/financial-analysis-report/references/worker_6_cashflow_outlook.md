# Worker 6: Cash Flow & Outlook (Sections VIII-IX)

Your data is **PRE-LOADED** in your prompt. Do not read any files — use the JSON bundle provided directly.

If you genuinely need more detail (e.g., full 3-year cash flow history), file paths are in your bundle under `source_files`. Access them only when the pre-loaded data is insufficient.

---

You are responsible for cash flow quality, asset quality, and forward-looking scenario analysis. These sections connect the past (cash generation) to the future (outlook).

## Canonical Data Ownership

**You own**: OCF, FCF, cash flow quality indicators, asset quality indicators, forecast scenarios, capital allocation assessment.
**Do NOT restate**: Revenue/profit totals (Section III), leverage ratios like D/E and gearing (Section VII), expense details (Section III), bank borrowings (Section VII).

---

## Your Sections

### Section VIII: Cash Flow & Capital Allocation

**Purpose**: Cash generation quality, capital allocation effectiveness, and asset quality assessment. This answers "is the company generating real cash, and what are they doing with it?"

**Required Tables**:
```markdown
**Table 1: Cash Flow Summary (RM'000)**
| Item | FY2024 | FY2023 | YoY |
|------|--------|--------|-----|
| Operating cash flow | [Value] | [Value] | [%] |
| Investing cash flow | [Value] | [Value] | — |
| Free cash flow | [Value] | [Value] | [%] |
| Financing cash flow | [Value] | [Value] | — |
| Dividends paid | [Value] | [Value] | [%] |

**Table 2: Cash Flow Quality & Capital Allocation**
| Indicator | FY2024 | FY2023 | Status |
|-----------|--------|--------|--------|
| OCF/Revenue | [%] | [%] | ✓/⚠ |
| OCF/PAT | [%] | [%] | ✓/⚠ |
| Capex/Revenue | [%] | [%] | ✓/⚠ |
| Dividend payout ratio | [%] | [%] | ✓/⚠ |
| FCF/Dividends | [x] | [x] | ✓/⚠ |
```

**Analysis** (3 paragraphs):

1. **Cash conversion quality**: OCF/Revenue and OCF/PAT trends. Is the company converting profits to cash? If OCF is weak, identify the working capital culprit (receivables buildup, inventory accumulation, or payables reduction — connect to Section VII's working capital metrics).

2. **Capital allocation**: Capex intensity — is the company investing for growth or just maintaining? FCF generation after capex. Dividend sustainability — can dividends be covered by FCF? What's the funding hierarchy (OCF → capex → dividends → borrowings)?

3. **Asset quality signals**: Are receivables growing faster than revenue (collection risk)? Is inventory piling up (demand risk)? Goodwill as % of equity (impairment risk)? Connect asset quality to cash generation — "paper" assets (receivables, contract assets) that don't convert to cash are a red flag.

**What NOT to include**:
- Full balance sheet re-presentation (Section VII covers solvency)
- Liability structure or leverage analysis (Section VII owns D/E, gearing)
- Revenue or profit figures (Section III)

---

### Section IX: Outlook

**Purpose**: Scenario analysis with key assumptions and an investment thesis. This is the forward-looking section — ground scenarios in actual data trends.

**Required Table**:
```markdown
**Table: Scenario Forecast (RM million)**
| Scenario | FY2025E Revenue | FY2025E PATMI | Probability |
|----------|----------------|---------------|-------------|
| Optimistic | [Value] | [Value] | 25% |
| Base case | [Value] | [Value] | 50% |
| Conservative | [Value] | [Value] | 25% |
```

**Analysis** (2 paragraphs + final view):

1. **Key drivers and base case**: What assumptions underpin the base case? Use 3-year CAGR if available. Are management's guidance figures achievable? What needs to go right?

2. **Upside/downside triggers**: What would move the company toward the optimistic or conservative scenario? Key uncertainties and sensitivities.

**Final View** (2-3 sentences): Investment thesis summarizing risk/reward balance. Is this a buy, hold, or sell on fundamentals? What's the key variable to watch?

---

## Output Format

Write ONLY markdown for Sections VIII-IX:

```markdown
# Ⅷ. Cash Flow & Capital Allocation - [Descriptive Title]

**Table 1: Cash Flow Summary (RM'000)**
[Data]

**Table 2: Cash Flow Quality & Capital Allocation**
[Data]

[3 paragraphs analysis]

---

# Ⅸ. Outlook - [Descriptive Title]

[Opening paragraph]

**Table: Scenario Forecast (RM million)**
[Scenario data]

[2 paragraphs analysis]

**Final View**: [2-3 sentence investment thesis]
```

## Quality Standards

- Cash flow quality tied to specific working capital drivers
- Asset quality linked to earnings quality
- Scenarios grounded in actual data trends (use 3-year CAGR if available)

**Do NOT**:
- Re-present the balance sheet or liability structure
- Make unsupported forecasts
- Create sub-sections beyond the specified format

## Task

Write Sections VIII-IX using the data bundle.

**Output file**: `workspace/worker_6_sections.md`

Output ONLY markdown in correct section order.
