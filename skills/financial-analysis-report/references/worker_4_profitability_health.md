# Worker 4: Profitability & Financial Health (Sections V, VII)

You are responsible for two critical areas: shareholder returns quality (profitability) and balance sheet resilience (financial health). These are naturally linked — profitability funds balance sheet strength, and leverage affects ROE.

## Data Access

Your data is **PRE-LOADED** in your prompt. All profitability ratios, solvency metrics, and working capital data are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

## Canonical Data Ownership

**You own**: ROE, ROA, NCI % of PAT, attributable margin trajectory, DuPont decomposition, D/E ratio, gearing ratio, current ratio, quick ratio, bank borrowings, working capital metrics (DSO, DIO, DPO), net debt.
**Do NOT restate**: Revenue totals or growth % (Section III), gross margin (Section III), segment details (Section IV), OCF (Section VIII), expense details (Section III).

---

## Your Sections

### Section V: Profitability & Growth

**Purpose**: Deep dive into shareholder returns — ROE decomposition, growth quality, and sustainability. This goes beyond surface ratios to explain WHY profitability changed.

**Required Tables**:
```markdown
**Table 1: Profitability Indicators**
| Indicator | FY2024 | FY2023 | Change |
|-----------|--------|--------|--------|
| PBT margin | [%] | [%] | [ppt] |
| PAT margin | [%] | [%] | [ppt] |
| PATMI margin | [%] | [%] | [ppt] |
| Basic EPS (sen) | [Value] | [Value] | [%] |
| Approx. ROE | [%] | [%] | [ppt] |
| Approx. ROA | [%] | [%] | [ppt] |

**Table 2: Growth Quality**
| Indicator | FY2024 | FY2023 | Observation |
|-----------|--------|--------|-------------|
| Revenue growth | [%] | [%] | [Context] |
| Gross profit growth | [%] | [%] | [Context] |
| PAT growth | [%] | [%] | [Context] |
| PATMI growth | [%] | [%] | [Context] |
| EPS growth | [%] | [%] | [Context] |
| Total assets growth | [%] | [%] | [Context] |
| Equity growth | [%] | [%] | [Context] |
```

**Analysis** (3 paragraphs):

1. **DuPont decomposition**: Break down ROE into margin × turnover × leverage. Which component drove ROE change? Is ROE improvement from genuine efficiency or just more leverage? Quantify each component's contribution.

2. **NCI dilution impact**: How much is attributable margin compressed by minority interests? Is this structural (JV-heavy model) or cyclical? What's the trend over time?

3. **Growth quality assessment**: Is revenue → gross profit → PAT → EPS growth consistent? Where does growth dilute? Can growth be funded internally (OCF from Section VIII) or does it require external financing?

**What NOT to include**:
- Gross margin analysis (owned by Section III)
- Revenue growth details (owned by Section III)
- FCF or OCF (owned by Section VIII)

---

### Section VII: Financial Health

**Purpose**: Comprehensive assessment of balance sheet resilience — short-term liquidity, long-term leverage, and working capital efficiency. Connect debt dynamics to profitability.

**Required Tables**:
```markdown
**Table 3: Solvency Metrics**
| Indicator | FY2024 | FY2023 | YoY |
|-----------|--------|--------|-----|
| Current ratio | [X.XXx] | [X.XXx] | [↑/↓] |
| Quick ratio | [X.XXx] | [X.XXx] | [↑/↓] |
| Net debt | [Value] | [Value] | [Δ] |
| Net debt/equity | [X.XXx] | [X.XXx] | [↑/↓] |
| Gearing ratio | [%] | [%] | [↑/↓] |
| Debt/asset ratio | [%] | [%] | [↑/↓] |
| Bank borrowings | [Value] | [Value] | [%] |
| Retained earnings | [Value] | [Value] | [%] |

**Table 4: Working Capital Efficiency**
| Indicator | FY2024 | FY2023 | Interpretation |
|-----------|--------|--------|----------------|
| Receivables days | [Days] | [Days] | [Trend] |
| Payables days | [Days] | [Days] | [Trend] |
| Inventory days | [Days] | [Days] | [Trend] |
| Cash conversion cycle | [Days] | [Days] | [Trend] |
| Receivables change (CF) | [Value] | [Value] | [Collection signal] |
| Inventories change (CF) | [Value] | [Value] | [Inventory signal] |
```

**Analysis** (3 paragraphs):

1. **Liquidity assessment**: Can they meet short-term obligations? Is the current/quick ratio healthy? Cash runway? Concentration of current assets — too much in receivables or inventory?

2. **Leverage trajectory**: Is debt sustainable? How fast is D/E changing? Interest coverage ratio (if data available). Refinancing risk — maturity profile? Is leverage funding growth or covering losses?

3. **Working capital dynamics**: DSO/DIO/DPO trends — is the company collecting faster, paying slower, or managing inventory better? How does working capital affect cash flow (connect to Section VIII)? Is working capital efficiency improving or deteriorating?

**What NOT to include**:
- OCF or FCF (owned by Section VIII)
- Revenue or profit figures (Section III)
- Full balance sheet re-presentation (data is in the bundle, just show the key ratios)

---

## Output Format

Write ONLY markdown for Sections V and VII:

```markdown
# Ⅴ. Profitability & Growth - [Descriptive Title]

**Table 1: Profitability Indicators**
[Data]

**Table 2: Growth Quality**
[Data]

[3 paragraphs analysis]

---

# Ⅶ. Financial Health - [Descriptive Title]

**Table 3: Solvency Metrics**
[Data]

**Table 4: Working Capital Efficiency**
[Data]

[3 paragraphs analysis]
```

## Task

Write Sections V and VII using the data bundle.

**Output files**:
- Section V → `workspace/worker_4_sections_v.md`
- Section VII → `workspace/worker_4_sections_vii.md`

Write each section to its own file. Output ONLY markdown.
