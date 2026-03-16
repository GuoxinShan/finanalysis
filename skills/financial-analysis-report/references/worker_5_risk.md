# Worker 5: Risk Assessment (Section VI)

## Data Access

Your data is **PRE-LOADED** in your prompt. All risk metrics are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

---

You handle the standalone risk assessment. Be specific — every risk must be backed by data from the bundle.

## Canonical Data Ownership

**You own**: Risk matrix, risk analysis.
**Do NOT restate**: Revenue/profit totals (Section III), leverage ratios like D/E and gearing (Section VII), OCF (Section VIII), bank borrowings (Section VII). Reference these sections when discussing risks.

---

## Your Section

### Section VI: Risk Assessment

**Purpose**: Identify and prioritize material risks with actionable mitigation. This is the "what could go wrong" section — be honest and specific.

**Required Table**:
```markdown
**Table: Risk Assessment Matrix**
| Risk | Specific Issue | Severity | Priority | Mitigation |
|------|---------------|----------|----------|------------|
| [Risk 1] | [Issue with data] | [Critical/High/Medium/Low] | [1-5] | [Specific action] |
| [Risk 2] | [Issue with data] | [Critical/High/Medium/Low] | [1-5] | [Specific action] |
| [Risk 3] | [Issue with data] | [Critical/High/Medium/Low] | [1-5] | [Specific action] |
| [Risk 4] | [Issue with data] | [Critical/High/Medium/Low] | [1-5] | [Specific action] |
| [Risk 5] | [Issue with data] | [Critical/High/Medium/Low] | [1-5] | [Specific action] |
```

**Analysis** (2 paragraphs):

1. **Critical and high-priority risks**: What happens if not addressed? Quantify potential impact where possible (e.g., "If receivables days extend by 30 days, ~RM X of additional working capital would be required"). Cross-reference relevant sections (Section III for margin risk, Section VII for leverage risk, Section VIII for cash flow risk).

2. **Overall risk profile**: Is the company conservative, moderate, or aggressive? Is risk trending up or down? What's the single biggest risk investors should monitor?

**Risk categories to consider** (pick the 5 most material):
- Working capital / cash conversion risk
- Margin dilution (new markets, competitive pressure)
- Leverage / refinancing risk
- Concentration risk (customer, supplier, geographic)
- NCI / JV governance risk
- Interest rate risk
- Currency risk (if multi-currency operations)
- Regulatory risk
- Asset quality risk (receivables, inventory obsolescence)

**What NOT to include**:
- Climate risk / TCFD assessments — not material at this level
- Risk scoring code or methodology — include the assessment, not the process
- Sub-sections for each risk category — one matrix covers everything
- Risks without data backing — every risk must cite specific numbers

---

## Output Format

Write ONLY markdown for Section VI:

```markdown
# Ⅵ. Risk Assessment - [Descriptive Title]

**Table: Risk Assessment Matrix**
| Risk | Specific Issue | Severity | Priority | Mitigation |
|---|---|---|---|---|
| [Risk] | [Data] | [Level] | [#] | [Action] |

[2 paragraphs analysis]
```

## Quality Standards

- Risk severity must be data-driven, not generic
- Each risk must cite specific financial data
- Mitigation must be actionable, not vague

**Do NOT**:
- Ignore negative risks or soft-pedal concerns
- Just list numbers without interpretation
- Create sub-sections beyond the matrix + analysis format

## Task

Write Section VI using the data bundle.

**Output file**: `workspace/worker_5_sections.md`

Output ONLY markdown for this section.
