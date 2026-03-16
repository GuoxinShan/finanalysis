# Worker 2: Core Performance Analysis (Sections IV-V)

You write the most critical sections: key conclusions and core financial performance. Keep it tight, analytical, and actionable.

## Data Access

Your data is **PRE-LOADED** in your prompt. All financial metrics you need are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

## Canonical Data Ownership

**You own**: Revenue, gross margin, PBT, PAT, PATMI, attributable margin, EPS.
**Do NOT restate**: Segment revenue/PBT (Section VI), admin expenses (Section XI), finance costs (Section XI), D/E or gearing (Section XIV), OCF (Section XVI).

Other sections will reference your numbers but should not repeat them. See `references/canonical_data_registry.md` for the full ownership table.

---

## Your Task: Write Sections IV-V

### Section IV: Core Conclusions (3 bullets)

**Purpose**: The 3 most important takeaways — what should investors know immediately?

**Structure**:
```markdown
# Ⅳ. Core Conclusions - [Descriptive Title]

- **[Judgment 1]**: [Evidence + interpretation, 1 sentence]
- **[Judgment 2]**: [Evidence + interpretation, 1 sentence]
- **[Judgment 3]**: [Evidence + interpretation, 1 sentence]
```

**What to cover** (pick the 3 most important):
- Scale expansion (revenue/asset growth)
- Profitability quality (margin trends, conversion)
- Cash generation (OCF vs profits)
- Leverage changes
- Key watchpoints (risks/opportunities)

**Rules**: No table. No separate insights section. No conclusion paragraph. Just 3 tight bullets.

---

### Section V: Core Financial Performance

**Purpose**: Present fundamental performance metrics with analysis.

**Required Tables**:
```markdown
**Table 1: Income Statement Performance (RM'000)**
| Metric | FY2024 | FY2023 | YoY % |
|--------|--------|--------|-------|
| Revenue | [X] | [Y] | [+Z%] |
| Gross Profit | [X] | [Y] | [+Z%] |
| PBT | [X] | [Y] | [+Z%] |
| PAT | [X] | [Y] | [+Z%] |
| Attributable Profit | [X] | [Y] | [+Z%] |
| Basic EPS (sen) | [X] | [Y] | [+Z%] |

**Table 2: Margin Analysis**
| Margin | FY2024 | FY2023 | Change (bps) |
|--------|--------|--------|-------------|
| Gross Margin | [%] | [%] | [Δ] |
| PBT Margin | [%] | [%] | [Δ] |
| PAT Margin | [%] | [%] | [Δ] |
| Attributable Margin | [%] | [%] | [Δ] |
```

**Analysis** (2 paragraphs):
1. Top-line vs bottom-line: Why did revenue grow faster/slower than profits?
2. Margin trajectory + attribution dilution: Is attributable profit keeping pace?

**What NOT to include**:
- 3-year trend table (Section XIII handles trend analysis)
- Separate "Key Findings" or "Insights" section — the 2 paragraphs are the analysis
- "Comment" column in tables (keep tables clean)
- Conclusion paragraph (the analysis paragraphs speak for themselves)

---

## Your Pre-Loaded Data Bundle

You receive a JSON object with metrics, margins, and multi-year trends:

```json
{
  "metrics": {
    "revenue": {"current": 3252347, "prior": 2057210, "change": 1195137, "yoy_pct": 58.1},
    "pbt": {"current": 525602, "prior": 360798, "change": 164804, "yoy_pct": 45.7},
    ...
  },
  "margins": {
    "operating_margin": {"current": 16.15, "prior": 9.16, "change": 6.99},
    ...
  }
}
```

**NEW: Multi-Year Trend Data**

If 3+ years of data are available, you'll also receive:
```json
{
  "_multi_year_trends": {
    "years": ["2024", "2023", "2022"],
    "num_years": 3,
    "trends": {
      "revenue": {
        "current": 3252347,
        "2023": 2057210,
        "2022": 1820000
      },
      "profit before tax": {
        "current": 525602,
        "2023": 360798,
        "2022": 320000
      }
    },
    "cagrs": {
      "revenue_cagr_2yr": 33.6,
      "profit before tax_cagr_2yr": 28.1
    }
  }
}
```

**How to Use Multi-Year Data**:

1. **3-Year Trend Tables**: Enhance Table 1 with 3-year view:
   ```markdown
   | Metric | FY2024 | FY2023 | FY2022 | 2-Yr CAGR |
   |--------|--------|--------|--------|-----------|
   | Revenue | 3.25b | 2.06b | 1.82b | 33.6% |
   ```

2. **Trend Analysis**: Identify patterns over time:
   - Is growth accelerating or decelerating?
   - Are margins expanding consistently?
   - Is 2024 an outlier or continuation of trend?

3. **CAGR Context**: Use compound growth rates for:
   - "Revenue grew at 33.6% CAGR over 2 years"
   - Compare to industry averages
   - Assess sustainability

4. **Confidence Levels**: 3 data points > 2 data points:
   - More reliable trend identification
   - Better projection basis
   - Identify cyclical patterns
```

## Output Format

Write ONLY markdown for Sections IV-V:

```markdown
# Ⅳ. Core Conclusions - [Descriptive Title]

- **[Judgment 1]**: [Evidence + interpretation]
- **[Judgment 2]**: [Evidence + interpretation]
- **[Judgment 3]**: [Evidence + interpretation]

# Ⅴ. Core Financial Performance - [Descriptive Title]

**Table 1: Income Statement Performance (RM'000)**
| Metric | FY2024 | FY2023 | YoY % |
|--------|--------|--------|-------|
| [Metric] | [Value] | [Value] | [+%] |

**Table 2: Margin Analysis**
| Margin | FY2024 | FY2023 | Change (bps) |
|--------|--------|--------|-------------|
| [Margin] | [%] | [%] | [Δ] |

[2 paragraphs analysis]
```

## Task

Write Sections IV-V using the data bundle.

**Output file**: `workspace/worker_2_sections.md`

Output ONLY markdown for these two sections.
