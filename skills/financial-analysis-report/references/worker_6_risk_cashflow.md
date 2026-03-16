# Worker 6: Risk Analysis (Sections IX-XI)

## Data Access

Your data is **PRE-LOADED** in your prompt. All risk metrics and expense data are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

---

You handle 3 sections: risk identification, three-statement summary, and expense structure. Be concise and actionable.

## Canonical Data Ownership

**You own**: Risk matrix, three-statement summary tables, admin expenses, finance costs.
**Do NOT restate**: Revenue/profit totals (Section V), leverage ratios like D/E and gearing (Section XIV), OCF (Section XVI), bank borrowings (Section XIV).

See `references/canonical_data_registry.md` for the full ownership table.

---

## Your Sections

### Section IX: Risk Scan (~180 words)

**Purpose**: Identify and prioritize material risks with actionable mitigation.

**Required Table**:
```markdown
**Table: Risk Assessment Matrix**
| Risk | Specific Issue | Severity | Priority | Mitigation |
|------|---------------|----------|----------|------------|
| [Risk 1] | [Issue with data] | [Critical/High/Medium/Low] | [1-4] | [Specific action] |
| [Risk 2] | [Issue with data] | [Critical/High/Medium/Low] | [1-4] | [Specific action] |
| [Risk 3] | [Issue with data] | [Critical/High/Medium/Low] | [1-4] | [Specific action] |
| [Risk 4] | [Issue with data] | [Critical/High/Medium/Low] | [1-4] | [Specific action] |
| [Risk 5] | [Issue with data] | [Critical/High/Medium/Low] | [1-4] | [Specific action] |
```

**Analysis** (2 paragraphs, ~120 words):
1. Critical and high-priority risks — what happens if not addressed?
2. Overall risk profile — conservative/moderate/aggressive, trending direction

**What NOT to include**:
- Detailed multi-level mitigation action lists (Priority 1-4 sections with timelines) — the table's Mitigation column is sufficient
- Climate risk / TCFD-aligned assessments — not material for financial analysis at this level
- Risk scoring code or threshold logic — include the assessment, not the methodology
- Sub-sections for each risk category (IX.1, IX.2, etc.) — one matrix table covers everything

---

### Section X: Major Items in Three Statements (~150 words)

**Purpose**: Summarize the three financial statements concisely.

**Required Tables** (one per statement, no sub-tables):
```markdown
**Table 1: Balance Sheet (RM'000)**
| Item | FY2024 | FY2023 | YoY |
|------|--------|--------|-----|
| Total assets | [Value] | [Value] | [%] |
| Total equity | [Value] | [Value] | [%] |
| Total liabilities | [Value] | [Value] | [%] |
| Net debt | [Value] | [Value] | Δ |

**Table 2: Income Statement (RM'000)**
| Item | FY2024 | FY2023 | YoY |
|------|--------|--------|-----|
| Revenue | [Value] | [Value] | [%] |
| Gross profit | [Value] | [Value] | [%] |
| PBT | [Value] | [Value] | [%] |
| PAT | [Value] | [Value] | [%] |

**Table 3: Cash Flow (RM'000)**
| Item | FY2024 | FY2023 |
|------|--------|--------|
| Operating cash flow | [Value] | [Value] |
| Investing cash flow | [Value] | [Value] |
| Financing cash flow | [Value] | [Value] |
```

**Analysis** (1 paragraph, ~60 words): Are profits backed by cash? Is growth funded sustainably? What's the funding hierarchy?

**What NOT to include**:
- Sub-tables for current asset movements (X.1.1) or liability movements (X.1.2) — the main tables already show this
- Detailed investing cash flow decomposition (X.3.2) — 1 sentence in the analysis paragraph is enough
- Balance sheet re-presentation with full composition — Section XVII handles asset quality
- "Analytical Point" or "Comment" columns — keep tables clean

---

### Section XI: Expense Analysis (~120 words)

**Purpose**: Cost structure and efficiency.

**Required Table**:
```markdown
**Table: Expense Structure (RM'000)**
| Expense Item | FY2024 | FY2023 | % of Revenue | YoY |
|-------------|--------|--------|-------------|-----|
| Cost of sales | [Value] | [Value] | [%] | [%] |
| Admin expenses | [Value] | [Value] | [%] | [%] |
| Finance costs | [Value] | [Value] | [%] | [%] |
| Taxation | [Value] | [Value] | [% of PBT] | [%] |
```

**Analysis** (2 paragraphs, ~80 words):
1. Cost control: Are expenses growing slower than revenue? Operating leverage?
2. Interest burden (this is your canonical section for finance costs) and tax efficiency

---

## Output Format

Write ONLY markdown for Sections IX, X, XI:

```markdown
# Ⅸ. Risk Scan - [Descriptive Title]

**Table: Risk Assessment Matrix**
| Risk | Specific Issue | Severity | Priority | Mitigation |
|---|---|---|---|---|
| [Risk] | [Data] | [Level] | [#] | [Action] |

[2 paragraphs analysis]

---

# Ⅹ. Major Items in Three Statements - [Descriptive Title]

**Table 1: Balance Sheet (RM'000)**
[Balance sheet data]

**Table 2: Income Statement (RM'000)**
[Income statement data]

**Table 3: Cash Flow (RM'000)**
[Cash flow data]

[1 paragraph synthesis]

---

# Ⅺ. Expense Analysis - [Descriptive Title]

**Table: Expense Structure (RM'000)**
[Expense data]

[2 paragraphs analysis]
```

## Quality Standards

- Risk severity must be data-driven, not generic
- Connect three-statement analysis to business performance
- Be specific with numbers, not descriptions

**Do NOT**:
- Ignore negative risks
- Just list numbers without interpretation
- Create sub-sections or sub-tables beyond what's specified above

## Task

Write Sections IX-XI using the data bundle.

**Output file**: `workspace/worker_6_sections.md`

Output ONLY markdown in correct section order.
