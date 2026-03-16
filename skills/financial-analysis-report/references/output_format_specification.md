# Output Format Specification

Complete specification for the financial analysis report output format.

---

## Full Report Structure (9 Sections)

The full report uses Roman numerals (Ⅰ-Ⅸ) and follows this pattern:

```markdown
# [Company] [Period] Financial Analysis Report

Ⅰ. Company Overview
Ⅱ. Core Conclusions - [Descriptive Title]
Ⅲ. Financial Performance - [Descriptive Title]
Ⅳ. Business & Strategy - [Descriptive Title]
Ⅴ. Profitability & Growth - [Descriptive Title]
Ⅵ. Risk Assessment - [Descriptive Title]
Ⅶ. Financial Health - [Descriptive Title]
Ⅷ. Cash Flow & Capital Allocation - [Descriptive Title]
Ⅸ. Outlook - [Descriptive Title]
```

**Total length**: 6-10 pages (depending on complexity)

---

## Section Format Template

Each section follows this pattern:

```markdown
# [Roman Numeral]. [Section Title] - [Descriptive Subtitle]

**Table N: [Table Title]**
| Column | FY2024 | FY2023 | YoY | Comment |
|---|---:|---:|---:|---|
| [Item] | [Value] | [Value] | [+%] | [Note] |

**Analysis**
1. [First key insight with evidence]
2. [Second insight connecting data points]
3. [Third insight on implications]

**Conclusion**: [Summary paragraph]
```

### Section Format Rules

1. **Roman numerals**: Use Unicode Roman numerals (Ⅰ-Ⅸ)
2. **Descriptive subtitles**: Each section gets a unique subtitle reflecting key findings
   - Good: "Financial Performance - Revenue Surge with Margin Compression"
   - Bad: "Financial Performance - Analysis"
3. **Tables**: Numbered sequentially within each section (Table 1, Table 2, etc.)
4. **Number alignment**: Right-align numbers in table columns
5. **Currency formatting**: Use consistent currency notation (e.g., RM'000, RM million)
6. **Percentage precision**: One decimal place for percentages (e.g., 58.1%)
7. **YoY changes**: Include +/- sign and percentage
8. **Analysis label**: Use "**Analysis**" header (not "Insights") followed by numbered paragraphs

---

## Section-by-Section Specifications

### Section I: Company Overview (~30 lines)

**Structure**: Three sub-sections separated by `---`

1. **Company Profile** (100-150 words): Business description, segments, geography, market position
2. **Analysis Purpose** (50-100 words): Why, what questions, stakeholder perspective
3. **Data Description** (100-150 words): Sources, metrics, currency, quality notes

---

### Section II: Core Conclusions (~15 lines)

**Structure**: 3-5 bullet points

```markdown
# Ⅱ. Core Conclusions - [Descriptive Title]

- **[Judgment 1]**: [Evidence + interpretation, 1-2 sentences]
- **[Judgment 2]**: [Evidence + interpretation, 1-2 sentences]
- **[Judgment 3]**: [Evidence + interpretation, 1-2 sentences]
```

No table. No separate insights section. No conclusion paragraph.

---

### Section III: Financial Performance (~80 lines)

**Purpose**: Comprehensive P&L analysis with expense structure.

**Required**: 3 tables + 3-4 paragraphs of analysis

- **Table 1**: Income Statement Performance (Revenue → PATMI, EPS)
- **Table 2**: Margin Analysis (Gross → Attributable margins)
- **Table 3**: Expense Structure (Cost of sales, admin, finance, tax)

**Analysis**:
1. Revenue drivers and gross margin
2. Margin waterfall (gross → attributable, where value leaks)
3. Expense structure and operating leverage
4. Earnings quality (one-time items, NCI dilution)

---

### Section IV: Business & Strategy (~80 lines)

**Purpose**: Segment performance, industry context, strategic execution.

**Required**: 3 tables + 3 paragraphs of analysis

- **Table 1**: Segment Revenue (with share)
- **Table 2**: Segment Profitability (with margin)
- **Table 3**: Strategic Scorecard

**Analysis**:
1. Segment dynamics and mix shift
2. Industry impact on company results
3. Strategic execution assessment

---

### Section V: Profitability & Growth (~60 lines)

**Purpose**: ROE decomposition, growth quality, sustainability.

**Required**: 2 tables + 3 paragraphs of analysis

- **Table 1**: Profitability Indicators (margins, EPS, ROE, ROA)
- **Table 2**: Growth Quality (revenue → EPS growth consistency)

**Analysis**:
1. DuPont decomposition (margin × turnover × leverage)
2. NCI dilution impact
3. Growth quality assessment

---

### Section VI: Risk Assessment (~50 lines)

**Purpose**: Material risks with data-backed severity ratings.

**Required**: 1 risk matrix + 2 paragraphs

- **Risk Matrix**: Risk, Specific Issue, Severity, Priority, Mitigation (5 risks)

**Analysis**:
1. Critical/high-priority risks with quantified impact
2. Overall risk profile assessment

---

### Section VII: Financial Health (~70 lines)

**Purpose**: Balance sheet resilience and working capital efficiency.

**Required**: 2 tables + 3 paragraphs of analysis

- **Table 1**: Solvency Metrics (current/quick ratio, D/E, gearing, net debt)
- **Table 2**: Working Capital Efficiency (DSO, DIO, DPO, CCC)

**Analysis**:
1. Liquidity assessment
2. Leverage trajectory and sustainability
3. Working capital dynamics

---

### Section VIII: Cash Flow & Capital Allocation (~60 lines)

**Purpose**: Cash generation quality, capital allocation effectiveness.

**Required**: 2 tables + 3 paragraphs of analysis

- **Table 1**: Cash Flow Summary (OCF, investing, FCF, financing, dividends)
- **Table 2**: Cash Flow Quality & Capital Allocation (OCF/Revenue, Capex/Revenue, dividend coverage)

**Analysis**:
1. Cash conversion quality
2. Capital allocation effectiveness
3. Asset quality signals

---

### Section IX: Outlook (~45 lines)

**Purpose**: Scenario analysis and investment thesis.

**Required**: 1 scenario table + 2 paragraphs + final view

- **Scenario Forecast**: Optimistic/Base/Conservative (revenue, PATMI, probability)

**Analysis**:
1. Key drivers and base case plausibility
2. Upside/downside triggers

**Final View**: 2-3 sentence investment thesis

---

## Executive Summary Report Structure (4 Sections)

Generated by Worker 7 from the full report:

```markdown
# [Company] [Period] Financial Analysis Summary

1. Key Conclusions
   - Extracted from Section Ⅱ (Core Conclusions)

2. Data Parsing
   - Core metrics from Section Ⅲ
   - Profitability from Section Ⅴ
   - Financial health from Section Ⅶ

3. Trend Analysis
   - Synthesized from Sections Ⅲ, Ⅴ, Ⅶ
   - Revenue, margin, and solvency trajectories

4. Risk Warning
   - Extracted from Section Ⅵ (Risk Assessment)
   - Top risks and mitigants
```

**Total length**: 2-3 pages

---

## Quality Standards

### Precision Standards

**CRITICAL**: Calculate from source data BEFORE rounding. Never use rounded values as calculation inputs.

```
❌ WRONG: Round → Calculate
   PAT: 215.5m, PATMI: 114.8m
   NCI = 215.5 - 114.8 = 100.7m  ← ERROR (actual: 97.1m)

✅ CORRECT: Calculate → Round
   NCI = 215,492 - 114,818 = 97,078
   Display: 97.1m (97,078 / 1000)
```

See `writing_standards.md` section 7 for detailed examples.

---

## File Naming Conventions

**Full report**: `<TICKER>-<PERIOD>-revised.md`
**Executive summary**: `<TICKER>-<PERIOD>-summary.md`
**Worker outputs**: `worker_N_sections.md`
