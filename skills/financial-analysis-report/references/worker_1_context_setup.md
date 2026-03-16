# Worker 1: Context Setup

## Data Access

Your data is **PRE-LOADED** in your prompt. All financial metrics you need are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

---

## Canonical Data Ownership

**You own**: Company profile, data description, analysis scope.
**Do NOT restate**: Any financial metrics — those belong to Sections V, XI, XIV, XVI.

---

## Your Task

Write your sections using the data bundle.

**Output file**: `workspace/worker_1_sections.md`

Output ONLY markdown for your assigned sections.

---

### Section I: Company Profile

**Purpose**: Establish context for the analysis.

**Format**: Use an HTML info card for key facts, followed by 1-2 sentences of business description.

```html
<table style="width:100%; border-collapse:collapse; font-size:14px;">
  <tr style="background:#f8fafc;">
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600; width:30%;">Company</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">[Company Name]</td>
  </tr>
  <tr>
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600;">Core Business</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">[What they do — be specific]</td>
  </tr>
  <tr style="background:#f8fafc;">
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600;">Segments</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">[Segment 1] · [Segment 2] · [Segment 3]</td>
  </tr>
  <tr>
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600;">Geography</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">[Countries/regions]</td>
  </tr>
  <tr style="background:#f8fafc;">
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600;">Market Position</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">[Leader/Challenger/Niche in X]</td>
  </tr>
</table>
```

[1-2 sentence description of what drives their economics and competitive position.]

**Rules**: Fill every cell. Be specific (not "A public listed company in Malaysia"). Use data from your bundle.

---

### Section II: Analysis Purpose

**Purpose**: State what the report covers and why.

**Format**: Numbered list of objectives (3-4 items).

```
# II. Analysis Purpose

This report presents a data-verified FY2024 analysis using disclosed audited figures and note-level information, with the following objectives:

1. Reconcile performance changes between FY2024 and FY2023.
2. Assess margin, cash flow, leverage, and solvency quality.
3. Identify structural drivers at segment and geographic levels.
4. Translate disclosed financial risk notes into an actionable risk scan.
```

**Rules**: Adapt objectives to the specific company. Don't copy generic wording — tailor to what the data actually allows.

---

### Section III: Data Description

**Purpose**: State data source and coverage.

**Format**: 1-2 sentences.

```
# III. Data Description

All financial data in this report is represented in RM, unless specifically noted.
```

**Rules**: State the reporting currency (from `fs_index.currency`). Note the fiscal year end (from `fs_index.fiscal_year_end`). Keep it brief.

---

## Your Data Bundle

You receive a JSON object with these fields:

```json
{
  "company_name": "Company",
  "period": "FY2024",
  "currency": "MYR",
  "fiscal_year_end": "2024-12-31",
  "data_source": "Audited Annual Report",
  "text_search": {
    "text_blocks_path": "/path/to/text_blocks.jsonl",
    "page_hints": {
      "business_overview": [],
      "industry_overview": [],
      "segment_reporting": [],
      "mda_section": [],
      "strategy_outlook": [],
      "risk_factors": []
    }
  }
}
```

**How to use it:**

- `company_name`, `period`, `currency`, `fiscal_year_end` -- use directly in your output
- `text_search.page_hints` -- tells you which pages have business context (already extracted for you)

---

## Output Format

```markdown
# I. Company Profile

```html
<table style="width:100%; border-collapse:collapse; font-size:14px;">
  <tr style="background:#f8fafc;">
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600; width:30%;">Company</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">YTL Corporation Berhad</td>
  </tr>
  <tr>
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600;">Core Business</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">Diversified infrastructure and utilities conglomerate with operations in power generation, water treatment, cement, construction, property, and hospitality</td>
  </tr>
  <tr style="background:#f8fafc;">
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600;">Segments</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">Utilities · Cement & Building Materials · Construction · Property · Hotels · Management Services</td>
  </tr>
  <tr>
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600;">Geography</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">Malaysia, Singapore, United Kingdom, other markets</td>
  </tr>
  <tr style="background:#f8fafc;">
    <td style="padding:8px 12px; border:1px solid #e2e8f0; font-weight:600;">Market Position</td>
    <td style="padding:8px 12px; border:1px solid #e2e8f0;">Major independent power and water producer in Malaysia; established cement and construction player in ASEAN</td>
  </tr>
</table>
```

YTL's economics are driven by long-duration concession contracts in utilities and infrastructure, which provide recurring cash flows but require sustained capital investment and debt financing.

# II. Analysis Purpose

This report presents a data-verified FY2024 analysis using disclosed audited figures and note-level information, with the following objectives:

1. Reconcile performance changes between FY2024 and FY2023.
2. Assess margin, cash flow, leverage, and solvency quality.
3. Identify structural drivers at segment and geographic levels.
4. Translate disclosed financial risk notes into an actionable risk scan.

# III. Data Description

All financial data in this report is represented in RM, unless specifically noted. FY2024 refers to the financial year ended 30 June 2024.
```

---

## What to Avoid

- **Vague descriptions**: "A public listed company in Malaysia" — say what they actually do
- **Hype language**: "industry leader", "dominant player", "world-class" — use factual descriptions
- **Missing cells**: Every cell in the HTML table must be filled
- **Unverified claims**: Don't state market position without text-search evidence

## Quality Checklist

- [ ] Every cell in the HTML info card is filled with specific data
- [ ] Company description is factual, not promotional
- [ ] Analysis objectives are tailored to the company
- [ ] Reporting currency and fiscal year end are correctly stated
- [ ] Text-search was used to verify business description claims
