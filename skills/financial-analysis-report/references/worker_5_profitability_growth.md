# Worker 5: Profitability & Growth Analysis (Sections XII-XIII)

## Data Access

Your data is **PRE-LOADED** in your prompt. All profitability ratios and growth metrics are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

## Canonical Data Ownership

**You own**: ROE, ROA, NCI % of PAT, attributable margin trajectory, growth breadth analysis.
**Do NOT restate**: Revenue totals or growth % (Section V), gross margin (Section V), segment details (Section VI), leverage ratios (Section XIV), OCF (Section XVI).

See `references/canonical_data_registry.md` for the full ownership table.

---

You are responsible for margin trends, ROE drivers, and growth sustainability. Be concise — each section gets 1-2 tables + 1-2 paragraphs.

## Your Sections

### Section XII: Profitability Analysis (~120 words)

**Purpose**: Deep dive into margin trends and ROE — but NOT gross margin (that's Section V).

**Tables**:
```markdown
**Table 1: Profitability Indicators**
| Indicator | FY2024 | FY2023 | Change |
|-----------|--------|--------|--------|
| PBT margin | [%] | [%] | [ppt] |
| PAT margin | [%] | [%] | [ppt] |
| PATMI margin | [%] | [%] | [ppt] |
| Basic EPS (sen) | [Value] | [Value] | [%] |

**Table 2: Return Metrics**
| Indicator | FY2024 | FY2023 | Interpretation |
|-----------|--------|--------|----------------|
| Approx. ROE | [%] | [%] | [Interpretation] |
| Approx. ROA | [%] | [%] | [Interpretation] |
```

**Analysis** (2 paragraphs, ~80 words):
1. Margin trajectory: PBT/PAT/PATMI trends — is profitability improving at the shareholder level?
2. ROE drivers: Profit margin vs. asset turnover vs. leverage (DuPont decomposition). NCI dilution impact.

**What NOT to include**:
- Gross margin (owned by Section V — reference it, don't restate)
- Revenue growth (owned by Section V)
- Operating margin (covered in Section V already)

---

### Section XIII: Growth Capability Analysis (~120 words)

**Purpose**: Assess growth trajectory and sustainability.

**Tables**:
```markdown
**Table 1: Growth Indicators**
| Indicator | FY2024 | FY2023 | Observation |
|-----------|--------|--------|-------------|
| Gross profit growth | [%] | [%] | [Context] |
| PAT growth | [%] | [%] | [Context] |
| PATMI growth | [%] | [%] | [Context] |
| Total assets growth | [%] | [%] | [Context] |
| Equity growth | [%] | [%] | [Context] |

**Table 2: Growth Support**
| Indicator | FY2024 | FY2023 | Interpretation |
|-----------|--------|--------|----------------|
| Group capex | [Value] | [Value] | [Reinvestment intensity] |
| Operating cash flow | [Value] | [Value] | [Internal funding] |
```

**Analysis** (2 paragraphs, ~80 words):
1. Growth breadth: Is revenue → profit → EPS growth consistent? (earnings quality)
2. Sustainability: Can growth be funded internally? Balance sheet capacity for future growth?

**What NOT to include**:
- Revenue growth (owned by Section V — this section focuses on profit/assets/equity growth)
- FCF (owned by Section XVI)

---

## Output Format

Write ONLY markdown for Sections XII-XIII:

```markdown
# ⅩⅡ. Profitability Analysis - [Descriptive Title]

**Table 1: Profitability Indicators**
[Data]

**Table 2: Return Metrics**
[Data]

[2 paragraphs analysis]

---

# ⅩⅢ. Growth Capability Analysis - [Descriptive Title]

**Table 1: Growth Indicators**
[Data]

**Table 2: Growth Support**
[Data]

[2 paragraphs analysis]
```

## Task

Write Sections XII-XIII using the data bundle.

**Output file**: `workspace/worker_5_sections.md`

Output ONLY markdown for these two sections.
