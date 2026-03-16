# Output Format Specification

Complete specification for the financial analysis report output format.

---

## Full Report Structure (18 Sections)

The full report uses Roman numerals (Ⅰ-ⅩⅤⅢ) and follows this pattern:

```markdown
# [Company] [Period] Financial Analysis Report

Ⅰ. Company Profile
Ⅱ. Analysis Purpose
Ⅲ. Data Description
Ⅳ. Core Conclusions - [Descriptive Title]
Ⅴ. Core Financial Performance - [Descriptive Title]
Ⅵ. Analysis of Changes in Core Business - [Descriptive Title]
Ⅶ. Industry Change Analysis - [Descriptive Title]
Ⅷ. Strategic Initiatives Analysis - [Descriptive Title]
Ⅸ. Risk Scan - [Descriptive Title] (ENHANCED with Risk Matrix)
Ⅹ. Analysis of Major Items in the Three Statements - [Descriptive Title]
Ⅺ. Expense Analysis - [Descriptive Title]
Ⅻ. Profitability Analysis - [Descriptive Title]
ⅩⅢ. Growth Capability Analysis - [Descriptive Title]
ⅩⅣ. Solvency Analysis - [Descriptive Title]
ⅩⅤ. Operating Capability Analysis - [Descriptive Title]
ⅩⅥ. Cash Flow Analysis - [Descriptive Title]
ⅩⅦ. Asset Quality Analysis - [Descriptive Title]
ⅩⅧ. Future Forecast - [Descriptive Title]
```

**Total length**: 8-12 pages (depending on complexity)

---

## Section Format Template

Each section follows this pattern:

```markdown
# [Roman Numeral]. [Section Title] - [Descriptive Subtitle]

**Table N: [Table Title]**
| Column | FY2024 | FY2023 | YoY | Comment |
|---|---:|---:|---:|---|
| [Item] | [Value] | [Value] | [+%] | [Note] |

**Insights**
1. [First key insight with evidence]
2. [Second insight connecting data points]
3. [Third insight on implications]

**Conclusion**: [Summary paragraph]
```

### Section Format Rules

1. **Roman numerals**: Use Unicode Roman numerals (Ⅰ-ⅩⅤⅢ), not ASCII
2. **Descriptive subtitles**: Each section gets a unique subtitle reflecting key findings
   - Good: "Core Conclusions - Scale Expansion with Margin Pressure"
   - Bad: "Core Conclusions - Analysis"
3. **Tables**: Numbered sequentially (Table 1, Table 2, etc.)
4. **Number alignment**: Right-align numbers in table columns
5. **Currency formatting**: Use consistent currency notation (e.g., RM'000, RM million)
6. **Percentage precision**: One decimal place for percentages (e.g., 58.1%)
7. **YoY changes**: Include +/- sign and percentage
8. **Comments column**: Provide context for unusual items

---

## Table Formatting Standards

### Standard Metrics Table

```markdown
**Table 1: Core Financial Performance**
| Metric | FY2024 | FY2023 | YoY Change | Comment |
|---|---:|---:|---:|---|
| Revenue | 3,252,347 | 2,057,210 | +58.1% | Construction recovery + East Malaysia |
| Gross Profit | 525,602 | 188,626 | +178.5% | Vertical integration gains |
| PBT | 275,845 | 189,318 | +45.7% | Operating leverage |
| PAT | 215,492 | 162,702 | +32.4% | Lower effective tax rate |
| PATMI | 114,818 | 85,005 | +35.1% | NCI increased from JVs |
```

### Margin Analysis Table

```markdown
**Table 2: Margin Analysis**
| Margin | FY2024 | FY2023 | Change | Comment |
|---|---:|---:|---:|---|
| Gross Margin | 16.15% | 9.16% | +6.99pp | In-house production |
| Operating Margin | 8.48% | 9.19% | -0.71pp | New market dilution |
| PBT Margin | 8.48% | 9.20% | -0.72pp | Stable |
| PAT Margin | 6.63% | 7.91% | -1.28pp | Tax normalization |
| Attributable Margin | 3.53% | 4.13% | -0.60pp | Rising minority interests |
```

### Balance Sheet Table

```markdown
**Table 3: Balance Sheet Summary**
| Item | FY2024 | FY2023 | Change | Comment |
|---|---:|---:|---:|---|
| Total Assets | 2,156,489 | 1,634,271 | +32.0% | Expansion financing |
| Total Liabilities | 1,234,567 | 890,123 | +38.7% | Working capital needs |
| Total Equity | 921,922 | 744,148 | +23.9% | Retained earnings |
| Current Ratio | 1.32 | 1.45 | -0.13 | Still healthy |
| Debt-to-Equity | 0.34 | 0.20 | +0.14 | Leverage increased |
```

### Multi-Year Trend Table (3+ Years)

```markdown
**Table 4: Three-Year Revenue Trend**
| Year | Revenue (RM'000) | YoY Growth | CAGR (2yr) |
|---|---:|---:|---:|
| FY2022 | 1,820,000 | - | - |
| FY2023 | 2,057,210 | +13.0% | - |
| FY2024 | 3,252,347 | +58.1% | +33.6% |
```

---

## Section-by-Section Specifications

### Section I: Company Profile (100-150 words)

**Purpose**: Establish context for the analysis

**Required elements**:
- Company name and ticker
- Industry/sector
- Core business description
- Geographic footprint
- Market position

**Example**:
```markdown
# Ⅰ. Company Profile

Chin Hin Group Berhad (CHINHIN:MK) is a leading Malaysian building materials conglomerate with operations across Peninsula Malaysia and East Malaysia. The company operates through three core divisions: construction materials (60% of revenue), property development (25%), and trading (15%). Chin Hin holds market-leading positions in concrete and steel fabrication, with an integrated supply chain from raw material sourcing to end-product delivery. The group operates 12 manufacturing facilities nationwide and serves both public infrastructure projects and private residential developments.

**Key operations**: Manufacturing, construction, property development
**Geographic focus**: Malaysia (Peninsula 70%, East Malaysia 30%)
**Market position**: Top 3 in Malaysian building materials sector
```

---

### Section II: Analysis Purpose (50-100 words)

**Purpose**: Define the analytical framework and objectives

**Required elements**:
- Why this analysis is being conducted
- Key questions to answer
- Analytical focus areas
- Stakeholder perspective (investor, management, creditor)

**Example**:
```markdown
# Ⅱ. Analysis Purpose

This analysis evaluates Chin Hin's FY2024 financial performance to assess the company's growth trajectory, profitability sustainability, and financial health following its East Malaysia expansion. Key questions include: (1) Is revenue growth translating to profit quality? (2) Can operating cash flow support expansion? (3) Are leverage levels manageable? The analysis is conducted from an equity investor perspective, focusing on long-term value creation and risk-adjusted returns.
```

---

### Section III: Data Description (100-150 words)

**Purpose**: Transparency about data sources and limitations

**Required elements**:
- Data sources (annual reports, years covered)
- Metrics extracted
- Currency and units
- Data quality notes
- Comparison period

**Example**:
```markdown
# Ⅲ. Data Description

**Data sources**:
- Chin Hin Group Berhad Annual Report 2024 (FY2024: 12 months ended 31 December 2024)
- Chin Hin Group Berhad Annual Report 2023 (FY2023: 12 months ended 31 December 2023)

**Metrics extracted**: 236 line items from balance sheet, income statement, and cash flow statement, plus 25+ calculated financial ratios

**Currency**: Malaysian Ringgit (RM'000 unless otherwise stated)

**Data quality**: Financial statements audited by [Auditor Name], unqualified opinion. All metrics extracted via finanalysis CLI with 100% accuracy from structured FSIndex parsing.

**Comparative analysis**: YoY comparison (FY2024 vs FY2023), with industry benchmarks from Malaysian construction sector averages.
```

---

### Section IV: Core Conclusions (150-200 words, 3-5 bullets)

**Purpose**: Key takeaways upfront - what should investors know immediately?

**Structure**:
```markdown
# Ⅳ. Core Conclusions - [Descriptive Subtitle]

- **[Key insight]**: [What happened + why it matters] (1-2 sentences)
- **[Key insight]**: [What happened + why it matters] (1-2 sentences)
... (3-5 total bullets)
```

**What to include**:
- Scale expansion (revenue/asset growth)
- Profitability quality (margin trends, conversion efficiency)
- Cash generation (OCF vs. accounting profits)
- Leverage changes (debt levels)
- Key watchpoints (top risks/opportunities)

**Good Example**:
```markdown
# Ⅳ. Core Conclusions - Scale Expansion with Margin Dilution

- **Scale expansion is clear**: Revenue grew 58% YoY to RM3.25b, driven by construction recovery and East Malaysia expansion. However, margin dilution in new markets (8-10% vs 15-18% in Peninsula) raises quality concerns.
- **Operating efficiency improved**: Operating margin expanded 7pp to 16% through vertical integration, but attributable margin compressed (7.1% → 3.5%) due to rising minority interests from JVs.
- **Cash conversion weakened**: Despite accounting profits, operating cash flow remains negative (-RM60m FCF) due to receivables expansion in new markets, signaling execution risk.
- **Leverage increased but manageable**: Debt-to-equity rose from 0.20x to 0.34x to fund expansion, but interest coverage remains healthy at 8.2x.
- **Strategic inflection point**: FY2024 marks transition from Peninsula-centric to national player, with execution risk concentrated in working capital management and JV governance.
```

---

### Section V: Core Financial Performance (300-400 words)

**Purpose**: Detailed breakdown of revenue, profitability, and key drivers

**Required elements**:
- Revenue analysis with YoY breakdown
- Gross profit and margin analysis
- Operating profit and margin trends
- Net profit and margin trends
- Earnings quality assessment

**Format**: Tables + narrative insights + conclusion

**Example structure**:
```markdown
# Ⅴ. Core Financial Performance - Revenue Surge, Margin Mixed Signals

**Table 1: Core Financial Metrics**
[Standard metrics table]

**Insights**

1. **Revenue growth driven by volume, not price**: The 58% revenue surge reflects a 45% volume increase in concrete and steel, with only 13% from price adjustments. East Malaysia contributed RM975m (30% of total), validating the geographic expansion strategy.

2. **Gross margin expansion masks segment divergence**: While overall gross margin improved 7pp to 16.15%, Peninsula operations achieved 18% margins vs. 8-10% in East Malaysia due to lower pricing power and higher logistics costs in new markets.

3. **Operating leverage captured, but NCI dilution significant**: Operating margin improved 0.71pp to 8.48%, but attributable margin compressed 0.60pp to 3.53% as minority interests in JVs absorbed 47% of PAT growth. This structural shift requires investor attention.

**Conclusion**: FY2024 demonstrates successful scale expansion but reveals margin quality concerns in new markets and structural dilution from the JV-heavy expansion model. The 58% revenue growth is real, but the 3.53% attributable margin suggests the company trades profitability for scale—a strategy that requires monitoring in FY2025.
```

---

### Section IX: Risk Scan (ENHANCED with Risk Matrix)

**Purpose**: Comprehensive risk assessment with severity ratings and mitigation

**Required elements**:
- Risk matrix table with severity, probability, impact, priority
- Time-bound mitigation actions
- Residual risk assessment

**Risk Matrix Format**:
```markdown
# Ⅸ. Risk Scan - Execution and Concentration Risks Elevated

**Table 9: Risk Matrix**
| Risk | Severity | Probability | Impact | Priority | Mitigation | Timeline | Residual |
|---|---|---|---|---:|---|---|---|
| Working capital strain | High | High | Cash flow negative | 1 | Tighten collections, factoring | Q1-Q2 2025 | Medium |
| Margin dilution in EM | High | Medium | Profitability drag | 2 | Operational improvements | 12 months | Medium |
| JV governance | Medium | Medium | NCI dilution | 3 | Strengthen oversight | Ongoing | Low-Medium |
| Concentration risk | Medium | Low | Revenue volatility | 4 | Diversify customer base | 24 months | Low |
```

**Each risk should include**:
- Severity: Critical/High/Medium/Low
- Probability: High/Medium/Low
- Impact: Description of financial/operational impact
- Priority: 1-4 ranking (1 = highest)
- Mitigation: Specific, actionable steps
- Timeline: When mitigation will be implemented
- Residual: Expected risk level after mitigation

---

### Section XII: Profitability Analysis (250-350 words)

**Required elements**:
- ROE, ROA, ROIC analysis
- Margin decomposition (gross → operating → net)
- Profitability drivers
- Peer comparison (if available)

---

### Section XIV: Solvency Analysis (200-300 words)

**Required elements**:
- Debt-to-equity, debt-to-assets
- Interest coverage ratio
- Current ratio, quick ratio
- Working capital analysis
- Debt maturity profile

---

### Section XVI: Cash Flow Analysis (250-350 words)

**Required elements**:
- Operating cash flow vs. net income
- Free cash flow analysis
- Cash conversion quality
- Working capital impact
- Investing/financing activities summary

---

### Section XVIII: Future Forecast (200-300 words)

**Required elements**:
- 12-month outlook
- Key growth drivers
- Risk factors
- Management guidance (if available)
- Analyst consensus (if available)

**Format**:
```markdown
# ⅩⅧ. Future Forecast - Cautiously Optimistic on Execution

**12-Month Outlook**: Revenue projected to grow 15-20% to RM3.7-3.9b, with margin stabilization expected as East Malaysia operations mature. Management targets attributable margin recovery to 4.0-4.5% through operational improvements and tighter working capital management.

**Key growth drivers**:
1. Infrastrucure projects: RM1.2b order book from Pan Borneo Highway
2. Margin recovery: East Malaysia operations reaching scale efficiency
3. Working capital optimization: Factoring arrangements to improve cash conversion

**Risk factors**:
- Working capital execution: -RM60m FCF must reverse to sustain growth
- Margin pressure: Competitive intensity in East Malaysia remains high
- Interest rate risk: Rising rates could increase financing costs

**Management guidance**: Management targets 15-20% revenue growth and 4.0-4.5% attributable margin for FY2025.

**Analyst consensus**: [If available, include sell-side analyst projections]

**Conclusion**: FY2025 will test Chin Hin's ability to convert scale into sustainable profitability. The 58% revenue growth in FY2024 set the foundation; FY2025 must deliver margin recovery and cash generation to validate the expansion strategy.
```

---

## Executive Summary Report Structure (4 Sections)

The executive summary is **generated by Worker 7 (LLM-based)** from the full report with 4 key sections:

```markdown
# [Company] [Period] Financial Analysis Summary

1. Key Conclusions
   - Extracted from Section Ⅳ (Core Conclusions table)

2. Data Parsing
   - Core metrics from Section Ⅴ
   - Profitability from Section Ⅻ
   - Solvency from Section ⅩⅣ

3. Trend Analysis
   - Synthesized from Sections Ⅴ, Ⅻ, ⅩⅣ
   - Revenue, margin, and solvency trajectories

4. Risk Warning
   - Extracted from Section Ⅸ (Risk Scan)
   - Top risks and mitigants
```

**Total length**: 2-3 pages

**Generation process**: After assembling the full report, Worker 7 reads the full report and synthesizes the executive summary following the 4-section format.

**Why LLM-based?** The summary requires interpretation and synthesis across multiple sections, not just extraction. An LLM can identify the most important insights and maintain narrative coherence better than a script.

---

## Quality Standards

### Precision Standards

**CRITICAL**: Calculate from source data BEFORE rounding. Never use rounded values as calculation inputs.

**The Rounding Error Pattern**:
```
❌ WRONG: Round → Calculate
   PAT: 215.5m, PATMI: 114.8m
   NCI = 215.5 - 114.8 = 100.7m  ← ERROR (actual: 97.1m)

✅ CORRECT: Calculate → Round
   NCI = 215,492 - 114,818 = 97,078
   Display: 97.1m (97,078 / 1000)
```

See `references/writing_standards.md` section 7 for detailed examples.

---

## File Naming Conventions

**Full report**: `<TICKER>-<PERIOD>-revised.md`
- Example: `CHINHIN-FY2024-revised.md`

**Executive summary**: `<TICKER>-<PERIOD>-summary.md` or `<TICKER>-summary.md`
- Example: `CHINHIN-summary.md`

**Worker outputs**: `worker_N_output.md`
- Example: `worker_2_output.md`
