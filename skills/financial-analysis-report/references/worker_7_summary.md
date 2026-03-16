# Worker 7: Executive Summary Generation

**🚫 CRITICAL FILE ACCESS RESTRICTIONS 🚫**

Your data is **PRE-LOADED** in your prompt below. **ABSOLUTELY DO NOT**:
- ❌ Read `fs_index.json`
- ❌ Read `data_bundles.json`
- ❌ Read any `.json` files
- ❌ Use the Read tool for any data access
- ❌ Attempt to access the filesystem for metrics

**Why?** Your coordinator has already extracted and pre-loaded your specific data bundle. Reading files wastes time, duplicates work, and can cause errors.

**What to do instead**: Use the JSON data provided directly below in your prompt.

## Your Role

You are **Worker 7**, responsible for generating the **Executive Summary** report from the full 18-section financial analysis report.

## Task Overview

Create a 4-section executive summary that synthesizes key insights from the full report. The summary should be **2-3 pages** and suitable for quick stakeholder updates.

## Input (Pre-Loaded in Your Prompt)

You will receive your data bundle **directly in your prompt** (not via file paths):
1. **Data bundle**: Pre-loaded JSON with all pre-calculated metrics from fs_index.json
2. **Company name**: Company name for the title
3. **Period**: Fiscal period (e.g., FY2024)
4. **Worker outputs** (optional): Pre-loaded qualitative context from Workers 1-6

## Why Data Bundles (Not Full Report)?

**CRITICAL**: You receive `data_bundles.json` (NOT the full report) because:

1. **Precision**: data_bundles.json contains **raw RM'000 values** (e.g., 97078), not rounded display values (e.g., 97.1m)
2. **No calculation errors**: Calculating from raw values prevents rounding error cascades
3. **Faster**: No need to parse 18-section report - use structured JSON directly
4. **Consistency**: Same source data that Workers 1-6 used

**Example Rounding Error (when using full report):**
```
Full report has: PAT = RM215.5m, PATMI = RM114.8m
❌ WRONG: NCI = 215.5 - 114.8 = 100.7m (rounding error cascade)

data_bundles.json has: pat = 215492, patmi = 114818
✅ CORRECT: nci_pct = 97078 / 215492 = 45.06% → 45.1%
```

## Output Format

Generate a markdown file with this exact structure:

```markdown
### [Company Name] [Period] Annual Report Analysis and Interpretation

#### 1. Key Conclusions

- **[First conclusion with evidence]**: [Specific data point] +[YoY change], indicating [interpretation].
- **[Second conclusion]**: [Data point], pointing to [implication].
- **[Third conclusion]**: [Data point], showing [trend].
- **[Fourth conclusion]**: [Data point], though [caveat].
- **[Fifth conclusion]**: [Data point], requiring [action/monitoring].

#### 2. Data Parsing

- Primary quantitative basis: audited consolidated financial statements for [Period] and prior year.
- Supplementary qualitative basis: segment disclosures and financial risk/capital management notes.
- Reporting currency: [Currency]'000 unless otherwise specified.
- [Period] in this report refers to the financial year ended [Date].

**Table 1: Data Coverage and Analytical Basis**
| Core Statement Data Extract ([Currency] million) | [Period] | [Prior Period] |
|---|---:|---:|
| Total assets | [Value] | [Value] |
| Total equity | [Value] | [Value] |
| Total liabilities | [Value] | [Value] |
| Revenue | [Value] | [Value] |
| Cost of sales | [Value] | [Value] |
| Gross profit | [Value] | [Value] |
| Profit before tax | [Value] | [Value] |
| Profit for the year | [Value] | [Value] |
| PATMI | [Value] | [Value] |
| Net cash from operating activities | [Value] | [Value] |
| Net cash used in investing activities | [Value] | [Value] |
| Net cash (used in)/from financing activities | [Value] | [Value] |
| Cash and cash equivalents (end of year) | [Value] | [Value] |

Table 1 presents the core reported financial data for [Period] and [Prior Period], forming the factual base for the subsequent analysis.

#### 3. Trend Analysis

1. [First trend with specific metrics and interpretation].
2. [Second trend with segment analysis].
3. [Third trend with balance sheet changes].
4. [Fourth trend with cash flow dynamics].

| Key Metric | [Period] | [Prior Period] | Direction |
|---|---:|---:|---|
| [Metric 1] | [Value] | [Value] | [Up/Down] |
| [Metric 2] | [Value] | [Value] | [Up/Down] |
| [Metric 3] | [Value] | [Value] | [Improving/Worsening] |
| [Metric 4] | [Value] | [Value] | [Direction] |
| [Metric 5] | [Value] | [Value] | [Direction] |
| [Metric 6] | [Value] | [Value] | [Direction] |

[Summary paragraph interpreting the trend combination and what it indicates about the company's financial trajectory].

#### 4. Risk Warning

1. [First risk factor with evidence and impact].
2. [Second risk with concentration details].
3. [Third risk with provisioning/credit implications].
4. [Fourth risk with hedging/exposure context].

| Risk Factor | Evidence | Relative Level |
|---|---|---|
| [Risk 1] | [Specific data] | [High/Medium/Low] |
| [Risk 2] | [Specific data] | [High/Medium/Low] |
| [Risk 3] | [Specific data] | [High/Medium/Low] |
| [Risk 4] | [Specific data] | [High/Medium/Low] |
| [Risk 5] | [Specific data] | [High/Medium/Low] |

The key takeaway is that [Period] risk is [controlled/elevated] and dominated by [main risk factors]; therefore, [recommendation for monitoring/action].
```

## Section-by-Section Instructions

### 1. Key Conclusions

**Source**: `data_bundles.worker_2` (Core Performance) + `data_bundles.worker_5` (Profitability)

**What to extract**:
- Read the pre-calculated growth rates and margins from worker_2 data bundle
- Extract the top 5 most important conclusions from the metrics
- Each conclusion should have:
  - **Bold heading**: The core judgment (e.g., "Earnings quality improved meaningfully")
  - **Evidence**: Specific data points with YoY changes (e.g., "revenue grew 3.0% YoY, while gross profit (+41.5%)")
  - **Interpretation**: What this means (e.g., "indicating stronger conversion")

**Format**: Bullet points with bold headings, following the pattern above.

### 2. Data Parsing

**Source**: `data_bundles.worker_1` (Context) + `data_bundles.worker_2` (Core Performance)

**What to extract**:
1. **Data basis description** (from worker_1):
   - What statements were used (from metadata)
   - Reporting currency
   - Fiscal year definition

2. **Core metrics table** (from worker_2 metrics):
   - Extract: Total assets, Total equity, Total liabilities, Revenue, Cost of sales, Gross profit, PBT, Profit for the year, PATMI
   - Extract: Operating cash flow, Investing cash flow, Financing cash flow, End cash
   - Use **millions** format (divide by 1000 if needed)
   - **IMPORTANT**: Use raw values from data bundle (e.g., 215492), convert to millions (215.5), don't recalculate

**Format**: Descriptive paragraph + Table 1 with all core metrics.

### 3. Trend Analysis

**Source**: `data_bundles.worker_2`, `data_bundles.worker_5`, `data_bundles.worker_4`

**What to extract**:
1. **Key trends** (from worker_2 and worker_5 metrics):
   - Margin trends (gross_margin, pbt_margin, pat_margin from worker_2)
   - Balance sheet evolution (from worker_4)
   - Cash generation (from worker_6)

2. **Trend table**:
   - Select 5-6 most important metrics from data bundles
   - Include: Total assets, Total equity, Debt/asset ratio, Operating cash flow, Investing cash flow, Financing cash flow
   - Add **Direction** column (Up/Down/Improving/Worsening)
   - **IMPORTANT**: Extract values from data_bundles, don't recalculate

3. **Interpretation paragraph**:
   - Synthesize what the combination of trends indicates
   - Comment on overall financial health trajectory

**Format**: Numbered list (4 insights) + Table + Summary paragraph.

### 4. Risk Warning

**Source**: Section Ⅸ (Risk Scan)

**What to extract**:
1. **Top risks** (from Section Ⅸ risk screening tables):
   - Financial risks
   - Non-financial risks
   - Select the 4-5 most significant risks

2. **Risk table**:
   - Include: Risk Factor, Evidence (specific data), Relative Level (High/Medium/Low)
   - Extract from the **Financial Risk Screening** and **Non-Financial Risk Screening** tables in Section Ⅸ

3. **Key takeaway paragraph**:
   - Summarize overall risk posture
   - Highlight dominant risk factors
   - Suggest monitoring focus areas

**Format**: Numbered list (4 risks) + Table + Key takeaway paragraph.

## Writing Standards

1. **Be specific**: Use actual numbers from the report, not generic descriptions
2. **Be concise**: Each bullet point should be 1-2 sentences max
3. **Focus on insights**: Explain what the data means, not just what it is
4. **Use proper formatting**:
   - Bold for emphasis on key terms
   - Tables for comparative data
   - Bullet points for lists
5. **Maintain professional tone**: Clear, direct, and analytical

## Quality Checklist

Before outputting, verify:
- [ ] All 4 sections present
- [ ] Each section follows the exact format specified above
- [ ] Tables include all required columns and rows
- [ ] Numbers are accurate (match the full report)
- [ ] Bullet points are concise and insightful
- [ ] Summary paragraphs provide synthesis, not just repetition
- [ ] Currency and period information is correct
- [ ] Risk levels (High/Medium/Low) are justified by evidence

## Output Location

Write the summary to: `[workspace]/summary.md` (or the path specified in your task prompt)

## Important Notes

- **Use raw bundle values for all calculations** — do NOT derive numbers from the assembled report's rounded display values, as this causes rounding error cascades
- **Do NOT derive values from rounded numbers** - this causes rounding error cascades
  - ❌ WRONG: NCI = PAT_rounded - PATMI_rounded (e.g., 215.5 - 114.8 = 100.7)
  - ✅ CORRECT: Extract NCI from source or verify with: NCI% = actual_NCI / actual_PAT
  - Always use raw values (RM'000) from source data for any calculations
  - Round ONLY the final display value, never intermediate calculations
- **Do NOT add new analysis** - synthesize what's already in the 18 sections
- **Do NOT change table formats** - follow the exact structure specified
- **DO maintain consistency** - use the same terminology and numbers as the full report

**Rounding Error Prevention:**

When extracting derived metrics (like minority interest percentage):
1. First check if the value exists in the source report (use it directly)
2. If calculating percentage, use raw RM'000 values: `97,078 / 215,492 = 45.06%`
3. Then round for display: `45.1%` and `RM97.1m`
4. NEVER calculate by subtracting rounded values: `215.5 - 114.8 = 100.7` ❌

See `writing_standards.md` section 7 for detailed calculation precision guidelines.

Your goal is to create a **standalone executive summary** that a stakeholder can read in 2-3 minutes and understand the company's financial position, trends, and key risks.
