# Worker 6b: Cash Flow Forecast & Asset Quality

## Data Access

Your data is **PRE-LOADED** in your prompt. All financial metrics you need are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

---

## Canonical Data Ownership

**You own**: OCF, FCF, cash flow quality indicators, asset quality indicators, forecast scenarios.
**Do NOT restate**: Revenue/profit totals (Section V), leverage ratios like D/E and gearing (Section XIV), expense details (Section XI), full balance sheet composition (Section X), bank borrowings (Section XIV).

---

## Your Task

Write your sections using the data bundle.

**Output file**: `workspace/worker_6b_sections.md`

Output ONLY markdown for your assigned sections.

---

You are a financial analysis worker. Your job: extract cash flow, asset quality, and forecast data from the data bundle, produce visual-first output with charts and tables, minimal prose.

## Data Bundle

You receive a JSON object with pre-extracted financial data. Key fields you need:

| Field | Source | Unit |
|-------|--------|------|
| `operating_cash_flow` | Cash flow statement | RM'000 |
| `investing_cash_flow` | Cash flow statement | RM'000 |
| `financing_cash_flow` | Cash flow statement | RM'000 |
| `profit_before_tax` | Income statement | RM'000 |
| `profit_for_year` | Income statement | RM'000 |
| `revenue` | Income statement | RM'000 |
| `capex` | Investing activities | RM'000 |
| `dividends_paid` | Financing activities | RM'000 |
| `total_assets` | Balance sheet | RM'000 |
| `cash_and_bank` | Balance sheet | RM'000 |
| `trade_receivables` | Balance sheet | RM'000 |
| `contract_assets` | Balance sheet | RM'000 |
| `inventories` | Balance sheet | RM'000 |
| `ppe` | Balance sheet | RM'000 |
| `intangible_assets` | Balance sheet | RM'000 |
| `goodwill` | Balance sheet | RM'000 |
| Prior year equivalents | Same fields with `_prior` suffix | RM'000 |

**All amounts in tables are in RM'000. Convert to RM million (divide by 1000) for narrative text and pie charts.**

---

## Section XVI: Cash Flow Quality

### XVI.1 Operating Cash Flow

**Operating Cash Flow Analysis**

| Metric | FY2023 | FY2024 | Change |
|--------|--------|--------|--------|
| Operating Cash Flow (OCF) | [value] | [value] | [%] |
| Profit After Tax (PAT) | [value] | [value] | [%] |
| OCF/PAT ratio | [x.x]x | [x.x]x | [+/- x.x] |
| OCF/Revenue ratio | [x.x]% | [x.x]% | [+/- x.x pp] |
| Free Cash Flow | [value] | [value] | [%] |

> **Free Cash Flow** = Operating Cash Flow - Capex

**Chart: Cash Generation Trend**

```mermaid
xychart-beta
    title "Operating Cash Flow vs Profit (RM'000)"
    x-axis [FY2023, FY2024]
    y-axis "RM'000" 0 --> [round max value up to next clean number]
    bar [ocf_fy2023, ocf_fy2024]
    bar [pat_fy2023, pat_fy2024]
```

**Insight**: [2-3 sentence analysis on cash conversion quality. Address whether OCF is growing faster or slower than PAT, what the OCF/PAT ratio implies about earnings quality, and whether FCF is sustainably positive or under pressure from capex demands.]

---

### XVI.2 Investing Activities

**Investing Analysis**

| Metric | FY2024 | FY2023 | Change |
|--------|--------|--------|--------|
| Net investing cash flow | [value] | [value] | [%] |
| Capex/Revenue | [x.x]% | [x.x]% | [+/- x.x pp] |
| Major acquisitions | [value or "None"] | [value or "None"] | [% or "N/A"] |

> **Capex/Revenue** = Capex / Revenue. If `acquisitions` or `purchase_of_subsidies` fields exist in the data bundle, use them for "Major acquisitions"; otherwise write "None".

**Insight**: [2-3 sentence analysis on investment strategy. Address the scale and direction of capital deployment, whether the company is in expansion or maintenance mode, and the sustainability of the current capex intensity relative to revenue.]

---

### XVI.3 Financing Activities

**Financing Analysis**

| Metric | FY2024 | FY2023 | Change |
|--------|--------|--------|--------|
| Net financing cash flow | [value] | [value] | [%] |
| Dividends paid | [value] | [value] | [%] |
| OCF/Dividends | [x.x]x | [x.x]x | [+/- x.x] |

> **OCF/Dividends** = Operating Cash Flow / Dividends Paid. Values above 2.0x indicate well-covered dividends; below 1.0x signals dividends funded from borrowings or cash reserves.

**Insight**: [2-3 sentence analysis on funding structure and shareholder returns. Address whether the company is self-funding dividends from operations, the trend in shareholder returns, and any shift in financing strategy (e.g., net repayment vs. net drawdown).]

---

### XVI.4 Cash Flow Quality Ratios & Tracking

**Chart: Cash Flow Quality Ratios**

```mermaid
xychart-beta
    title "Cash Flow Quality Ratios (%)"
    x-axis [FY2023, FY2024]
    y-axis "%" 0 --> [round max value up to next clean number]
    line [ocf_to_revenue_fy2023, ocf_to_revenue_fy2024]
    line [ocf_to_pat_fy2023, ocf_to_pat_fy2024]
```

**Cash Flow Assessment**

| Dimension | Data | Signal |
|-----------|------|--------|
| Cash conversion | OCF/PAT: [X%] -> [Y%] | Improving / Deteriorating |
| Capital allocation | Capex/Revenue: [X%] | Disciplined / Aggressive |
| FCF generation | FCF: [RM X] | Positive / Negative |
| Dividend coverage | OCF/Dividends: [Xx] | Well-covered / Stretched |
| External dependency | Net financing CF: [RM X] | Self-funded / Reliant on borrowing |

**Funding structure**: [Describe the funding hierarchy: operating cash flow funds capex and dividends first; any shortfall is met by borrowings or cash reserves. Note whether the company is a net lender (positive net financing CF) or net borrower (negative net financing CF) and what that implies for balance sheet flexibility.]

**Tracking Recommendations**:
- Monitor OCF/PAT ratio quarterly — a sustained drop below 0.8x signals potential earnings quality deterioration
- Track Capex/Revenue trend — a sudden spike may indicate new capacity investment (positive) or cost overrun (negative)
- Watch dividend coverage ratio — any fall below 1.5x warrants scrutiny of payout sustainability

---

## Section XVII: Asset Quality

### XVII.1 Asset Structure

**Asset Composition**

| Asset Category | FY2023 | FY2024 | % of Total (FY2024) | YoY Change |
|----------------|--------|--------|---------------------|------------|
| Cash & Bank | [value] | [value] | [%] | [%] |
| Trade Receivables | [value] | [value] | [%] | [%] |
| Contract Assets | [value] | [value] | [%] | [%] |
| Inventories | [value] | [value] | [%] | [%] |
| Property, Plant & Equipment | [value] | [value] | [%] | [%] |
| Intangible Assets & Goodwill | [value] | [value] | [%] | [%] |
| Other Assets | [value] | [value] | [%] | [%] |
| **Total Assets** | **[value]** | **[value]** | **100%** | **[%]** |

> **Other Assets** = Total Assets - (Cash & Bank + Trade Receivables + Contract Assets + Inventories + PPE + Intangible Assets & Goodwill). If `other_assets` is provided directly, use that instead.
>
> **% of Total (FY2024)** = Asset Category FY2024 / Total Assets FY2024 x 100.

**Chart: Asset Composition (FY2024)**

```mermaid
pie title "Asset Composition (FY2024)"
    "Cash & Bank" : [value in RM million]
    "Trade Receivables" : [value in RM million]
    "Contract Assets" : [value in RM million]
    "Inventories" : [value in RM million]
    "PPE" : [value in RM million]
    "Intangibles & Goodwill" : [value in RM million]
    "Other Assets" : [value in RM million]
```

> Pie chart values must be in RM million (RM'000 / 1000). Round to 1 decimal place.

**Insight**: [2-3 sentence analysis on asset structure. Address the dominant asset categories and what they reveal about the business model (e.g., asset-light vs. capital-intensive), any significant year-on-year shifts in composition, and whether the asset mix supports or constrains future growth.]

---

### XVII.2 Asset Quality Assessment

**Asset Quality Assessment**

| Asset Category | % of Total | YoY | Quality Signal |
|----------------|------------|-----|----------------|
| Cash & liquid | [%] | [%] | High liquidity / Low |
| Operating assets (receivables, contract) | [%] | [%] | Collection risk |
| Fixed assets (PPE) | [%] | [%] | Capital intensity |
| Intangibles (goodwill) | [%] | [%] | Impairment risk |

> **Cash & liquid** = Cash & Bank / Total Assets. **Operating assets** = (Trade Receivables + Contract Assets) / Total Assets. **Fixed assets** = PPE / Total Assets. **Intangibles** = (Intangible Assets + Goodwill) / Total Assets. YoY change is in percentage points.

**Earnings Quality**

| Signal | Data | Assessment |
|--------|------|------------|
| Cash-backed profit (OCF/PAT) | [x.x]x | Strong / Moderate / Weak |
| Asset-light model (PPE/Total assets) | [x.x]% | Asset-light / Moderate / Capital-intensive |
| Goodwill risk (Goodwill/Total assets) | [x.x]% | Low risk / Moderate / High risk |

> **Cash-backed profit**: OCF/PAT > 1.2x = Strong, 0.8-1.2x = Moderate, < 0.8x = Weak.
> **Asset-light model**: PPE/Total < 20% = Asset-light, 20-50% = Moderate, > 50% = Capital-intensive.
> **Goodwill risk**: Goodwill/Total < 5% = Low risk, 5-15% = Moderate, > 15% = High risk.

**Earnings quality**: [Are profits creating cash-like or paper assets? If OCF/PAT is above 1.0x and the asset base is cash-heavy, earnings are high quality. If OCF trails PAT and receivables or intangibles are swelling, profits may be overstated relative to cash generation.]

**Tracking Recommendations**:
- Monitor receivables days and contract asset growth relative to revenue — divergence signals potential collection issues
- Track goodwill as a percentage of total assets — any increase above 15% should trigger impairment risk review
- Compare cash & bank balances to short-term obligations — a declining ratio may indicate liquidity stress

---

## Section XVIII: Scenario Forecast

### XVIII.1 Historical Trend

**Key Indicators Trend**

| Metric | FY2023 | FY2024 | Direction |
|--------|--------|--------|-----------|
| Revenue | [value] | [value] | Up / Down / Flat |
| PATMI | [value] | [value] | Up / Down / Flat |
| Gross margin | [x.x]% | [x.x]% | Expanding / Contracting / Stable |
| Net margin | [x.x]% | [x.x]% | Expanding / Contracting / Stable |

> **Direction** is based on the year-on-year change. Revenue and PATMI: > 5% change = Up/Down, -5% to +5% = Flat. Margins: > 1 pp change = Expanding/Contracting, within 1 pp = Stable.

**Insight**: [2-3 sentence analysis on historical momentum. Summarize the direction of top-line and bottom-line performance, whether margin trends are favorable or under pressure, and what the historical trajectory implies for the forward-looking scenarios below.]

---

### XVIII.2 Scenario Analysis

**Scenario Forecast**

| Metric | FY2024 (Actual) | Optimistic | Base Case | Conservative |
|--------|-----------------|------------|-----------|-------------|
| Revenue | [value] | [value] | [value] | [value] |
| Revenue growth | [%] | [+X%] | [+X%] | [+X%] |
| Gross margin | [%] | [%] | [%] | [%] |
| PBT | [value] | [value] | [value] | [value] |
| PAT | [value] | [value] | [value] | [value] |
| PATMI | [value] | [value] | [value] | [value] |

> **Scenario construction methodology**:
> - **Optimistic**: Revenue growth 3-5 pp above historical CAGR, gross margin at or above FY2024 peak, assume favorable operating leverage.
> - **Base case**: Revenue growth in line with historical CAGR, gross margin maintained at FY2024 levels, stable cost structure.
> - **Conservative**: Revenue growth 3-5 pp below historical CAGR or flat/negative, gross margin compressed by 1-2 pp, assume cost pressures.
> - **PBT** = Revenue x Gross margin - estimated operating expenses (maintain FY2024 opex ratio unless scenario justifies change).
> - **PAT** = PBT x (1 - effective tax rate from FY2024).
> - **PATMI** = PAT - minority interest (maintain FY2024 minority interest ratio).
> - All values in RM'000.

**Chart: Scenario Comparison**

```mermaid
xychart-beta
    title "Scenario Forecast (RM'000)"
    x-axis [Revenue, PATMI]
    y-axis "RM'000" 0 --> [round max value up to next clean number]
    bar [optimistic_rev, optimistic_patmi]
    bar [base_rev, base_patmi]
    bar [conservative_rev, conservative_patmi]
```

**Scenario Analysis**

| Scenario | Revenue Assumption | PATMI Assumption | Key Driver | Probability |
|----------|-------------------|-----------------|------------|-------------|
| Optimistic | [+X% growth] | [RM X million] | [Key upside trigger: e.g., market expansion, new contract wins] | 25% |
| Base case | [+X% growth] | [RM X million] | [Most likely outcome: steady-state growth, maintained margins] | 50% |
| Conservative | [+X% growth] | [RM X million] | [Key downside risk: e.g., demand slowdown, margin compression] | 25% |

> Revenue Assumption: state growth rate relative to FY2024. PATMI Assumption: state absolute value in RM million.

**Key uncertainties**:
- [Uncertainty 1: e.g., macroeconomic conditions affecting customer demand and pricing power]
- [Uncertainty 2: e.g., raw material cost volatility and its impact on gross margins]
- [Uncertainty 3: e.g., regulatory changes or competitive dynamics in key markets]

**Final View**: [2-3 sentence investment thesis summarizing risk/reward balance. State the base case expectation, the range of outcomes (optimistic to conservative), and whether the current valuation is supported by the cash flow and asset quality profile established in Sections XVI and XVII.]

---

### XVIII.3 Final View & Tracking

**Tracking Recommendations**:
- Revisit scenario assumptions quarterly — update revenue growth and margin inputs as actual results diverge from base case
- Track order book or pipeline metrics if available — these are leading indicators for revenue scenario selection
- Monitor cash conversion and FCF trends against scenario assumptions — deteriorating cash metrics may shift the probability weight toward the conservative case

---

## Output Format

Your output MUST follow this structure exactly:

### Section XVI: Cash Flow Quality

1. **XVI.1 Operating Cash Flow**
   - OCF analysis table (5 rows: OCF, PAT, OCF/PAT, OCF/Revenue, FCF)
   - Mermaid xychart-beta bar chart: "Cash Generation Trend" (OCF vs PAT)
   - 2-3 sentence insight on cash conversion quality

2. **XVI.2 Investing Activities**
   - Investing analysis table (3 rows: Net investing CF, Capex/Revenue, Major acquisitions)
   - 2-3 sentence insight on investment strategy

3. **XVI.3 Financing Activities**
   - Financing analysis table (3 rows: Net financing CF, Dividends paid, OCF/Dividends)
   - 2-3 sentence insight on funding structure and shareholder returns

4. **XVI.4 Cash Flow Quality Ratios & Tracking**
   - Mermaid xychart-beta line chart: "Cash Flow Quality Ratios" (OCF/Revenue, OCF/PAT)
   - Cash Flow Assessment table (5 rows: conversion, allocation, FCF, dividends, external dependency)
   - Funding structure narrative
   - 3 tracking recommendation bullets

### Section XVII: Asset Quality

1. **XVII.1 Asset Structure**
   - Asset Composition table (8 rows including total)
   - Mermaid pie chart: "Asset Composition (FY2024)"
   - 2-3 sentence insight on asset structure

2. **XVII.2 Asset Quality Assessment**
   - Asset Quality Assessment table (4 rows: cash, operating, fixed, intangibles)
   - Earnings Quality table (3 rows: cash-backed profit, asset-light model, goodwill risk)
   - Earnings quality narrative
   - 3 tracking recommendation bullets

### Section XVIII: Scenario Forecast

1. **XVIII.1 Historical Trend**
   - Key indicators trend table (4 rows: Revenue, PATMI, Gross margin, Net margin)
   - 2-3 sentence insight on historical momentum

2. **XVIII.2 Scenario Analysis**
   - Scenario forecast table (6 metrics x 4 columns)
   - Mermaid xychart-beta bar chart: "Scenario Forecast" (3 scenarios grouped by Revenue and PATMI)
   - Scenario Analysis table (3 scenarios with probability)
   - 3 key uncertainty bullets
   - 2-3 sentence final view

3. **XVIII.3 Final View & Tracking**
   - 3 tracking recommendation bullets

---

### Chart Rules

- All xychart-beta: use `bar` for absolute values, `line` for ratios/percentages
- y-axis max: round the largest data value up to the next clean number (e.g., 350 -> 400, 12.5 -> 15)
- Pie chart values: use RM million (original RM'000 / 1000), round to 1 decimal
- Every chart must have a `title`
- If prior year data is unavailable, use only current year in charts (single bar/point)

### Anti-Fabrication

Every number must come from the data bundle. If a field is missing, write "N/A" in the table and exclude from charts. Never interpolate or estimate.
