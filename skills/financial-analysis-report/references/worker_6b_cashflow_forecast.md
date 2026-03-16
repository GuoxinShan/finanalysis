# Worker 6b: Cash Flow & Forecast (Sections XVI-XVIII)

Your data is **PRE-LOADED** in your prompt. Do not read any files — use the JSON bundle provided directly.

If you genuinely need more detail (e.g., full 3-year cash flow history), file paths are in your bundle under `source_files`. Access them only when the pre-loaded data is insufficient.

---

You are responsible for cash flow quality, asset quality, and forward-looking scenario analysis.

## Canonical Data Ownership

**You own**: OCF, FCF, cash flow quality indicators, asset quality indicators, forecast scenarios.
**Do NOT restate**: Revenue/profit totals (Section V), leverage ratios like D/E and gearing (Section XIV), expense details (Section XI), full balance sheet composition (Section X), bank borrowings (Section XIV).

See `references/canonical_data_registry.md` for the full ownership table.

---

## Your Sections

### Section XVI: Cash Flow Analysis (~150 words)

**Purpose**: Cash generation quality and sustainability.

**Tables**:
```markdown
**Table 1: Cash Flow Summary (RM'000)**
| Item | FY2024 | FY2023 |
|------|--------|--------|
| Operating cash flow | [Value] | [Value] |
| Investing cash flow | [Value] | [Value] |
| Financing cash flow | [Value] | [Value] |

**Table 2: Cash Flow Quality**
| Indicator | FY2024 | FY2023 | Status |
|-----------|--------|--------|--------|
| OCF/Revenue | [%] | [%] | ✓/⚠ |
| FCF (OCF - PPE capex) | [Value] | [Value] | ✓/⚠ |
```

**Analysis** (2 paragraphs, ~100 words):
1. Cash conversion: Is OCF/Revenue improving? Why? What explains OCF vs PAT divergence?
2. Debt service: Can OCF cover interest? Is the company reliant on external funding?

---

### Section XVII: Asset Quality Analysis (~100 words)

**Purpose**: Asset composition risk and credit quality — NOT a balance sheet re-presentation.

**Table**:
```markdown
**Table: Asset Quality Indicators (RM'000)**
| Asset Category | FY2024 | % of Total | Quality Signal |
|----------------|--------|------------|----------------|
| Cash & bank balances | [Value] | [%] | High liquidity |
| Trade receivables | [Value] | [%] | Collectability risk |
| Contract assets | [Value] | [%] | Execution risk |
| Goodwill & intangibles | [Value] | [%] | Impairment risk |
```

**Analysis** (1 paragraph, ~60 words): Liquidity mix, impairment risk, earnings quality (are profits creating cash-like or paper assets?).

**What NOT to include**:
- Full balance sheet re-presentation (Section X already covers this)
- Liability structure or leverage analysis (Section XIV owns D/E, gearing, borrowings)
- Detailed current asset movement tables (already in Section X)
- Sub-sections for balance sheet composition (XVII.1) or liability structure (XVII.7)

---

### Section XVIII: Future Forecast (~200 words)

**Purpose**: Scenario analysis with key assumptions.

**Table**:
```markdown
**Table: Scenario Forecast (RM million)**
| Scenario | FY2025E Revenue | FY2025E PATMI | Probability |
|----------|----------------|---------------|-------------|
| Optimistic | [Value] | [Value] | 25% |
| Base case | [Value] | [Value] | 50% |
| Conservative | [Value] | [Value] | 25% |
```

**Assumptions** (2-3 bullets per scenario, embedded in the analysis).

**Analysis** (2 paragraphs, ~130 words):
1. Key drivers and base case plausibility
2. Upside/downside triggers and key uncertainties

**Final View** (2-3 sentences): Investment thesis summarizing risk/reward balance.

---

## Output Format

Write ONLY markdown for Sections XVI, XVII, XVIII:

```markdown
# ⅩⅥ. Cash Flow Analysis - [Descriptive Title]

**Table 1: Cash Flow Summary (RM'000)**
[Cash flow data]

**Table 2: Cash Flow Quality**
[Quality indicators]

[2 paragraphs analysis]

---

# ⅩⅦ. Asset Quality Analysis - [Descriptive Title]

**Table: Asset Quality Indicators (RM'000)**
[Asset data]

[1 paragraph analysis]

---

# ⅩⅧ. Future Forecast - [Descriptive Title]

[Opening paragraph]

**Table: Scenario Forecast (RM million)**
[Scenario data]

[Assumptions + 2 paragraphs analysis]

**Final View**: [2-3 sentence investment thesis]
```

## Quality Standards

- Cash flow quality tied to specific working capital drivers
- Asset quality linked to earnings quality (cash vs paper assets)
- Scenarios grounded in actual data trends (use 3-year CAGR if available)

**Do NOT**:
- Re-present the balance sheet or liability structure
- Make unsupported forecasts
- Create sub-sections beyond what's specified above

## Task

Write Sections XVI-XVIII using the data bundle.

**Output file**: `workspace/worker_6b_sections.md`

Output ONLY markdown in correct section order.
