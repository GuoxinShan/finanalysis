# Worker 5: Profitability & Growth Analysis (Sections XII-XIII)

**🚫 CRITICAL FILE ACCESS RESTRICTIONS 🚫**

Your data is **PRE-LOADED** in your prompt below. **ABSOLUTELY DO NOT**:
- ❌ Read `fs_index.json`
- ❌ Read `data_bundles.json`
- ❌ Read any `.json` files
- ❌ Use the Read tool for any data access
- ❌ Attempt to access the filesystem for metrics

**Why?** Your coordinator has already extracted and pre-loaded your specific data bundle. Reading files wastes time, duplicates work, and can cause errors.

**What to do instead**: Use the JSON data provided directly below in your prompt.

---

### 📂 **Optional: Deep-Dive Access** (10% of cases)

If you need additional context beyond the pre-loaded data, file paths are provided in your bundle under `source_files`.

**When to use**:
- ✅ Need complete profitability history (not just 3 years)
- ✅ Need detailed ROE component breakdown
- ✅ Need all margin calculations

**How to access** (ONLY if needed):
```python
# Read complete metrics.json for full breakdown
with open(metrics_path, 'r') as f:
    metrics = json.load(f)
    complete_profitability = metrics['profitability']
```

**Note**: 90% of the time, the pre-loaded data is sufficient. Only access files when absolutely necessary.

---

You are responsible for analyzing margin trends, ROE drivers, and growth sustainability.

## Your Sections

### Section Ⅻ: Profitability Analysis (~200 words)

**Purpose**: Deep dive into margin trends and ROE

**Table**:
```markdown
| Ratio | Current | Prior* | 3-Year Avg | Industry |
|-------|---------|--------|------------|----------|
| Operating Margin | X% | Y% | Z% | A% |
| PBT Margin | X% | Y% | Z% | A% |
| PAT Margin | X% | Y% | Z% | A% |
| Attributable Margin | X% | Y% | Z% | A% |
| ROE | X% | Y% | Z% | A% |
```

**Insights to develop**:
1. **Margin trajectory**: 3-year trend - improving, stable, or deteriorating?
2. **ROE drivers**: Profit margin vs. asset turnover vs. leverage (DuPont analysis)
3. **Margin compression/expansion**: What's driving the change?
4. **Industry comparison**: Above or below peers? Why?

**Conclusion**: Assess profitability quality vs. scale - is growth coming at the expense of margins?

---

### Section ⅩⅢ: Growth Capability Analysis (~200 words)

**Purpose**: Assess growth trajectory and sustainability

**Table**:
```markdown
| Metric | YoY Growth | 3-Year CAGR | Trend |
|--------|------------|-------------|-------|
| Revenue | +X% | Y% | ▲/▼/— |
| Operating Profit | +X% | Y% | ▲/▼/— |
| PBT | +X% | Y% | ▲/▼/— |
| PAT | +X% | Y% | ▲/▼/— |
| EPS | +X% | Y% | ▲/▼/— |
| Total Assets | +X% | Y% | ▲/▼/— |
```

**Insights to develop**:
1. **Growth breadth**: Is revenue → profit → EPS growth consistent? (earnings quality)
2. **Sustainable growth rate**: Can growth be funded internally or needs external capital?
3. **Balance sheet capacity**: Debt headroom for future growth?
4. **Growth vs. profitability trade-off**: Are margins sacrificed for growth?

**Conclusion**: Assess growth engine strength - sustainable or fueled by debt/low-quality revenue?

---

## Your Data Bundle

You will receive a JSON object with:

```json
{
  "profitability_ratios": {
    "operating_margin": {"current": 16.15, "prior": 9.16, "three_year_avg": 12.5, "industry": 15.0},
    "pbt_margin": {"current": 16.15, "prior": 17.53, "three_year_avg": 16.0, "industry": 18.0},
    "pat_margin": {"current": 6.61, "prior": 13.27, "three_year_avg": 10.0, "industry": 12.0},
    "attributable_margin": {"current": 3.53, "prior": 7.08, "three_year_avg": 5.5, "industry": 8.0},
    "roe": {"current": 14.18, "prior": 19.11, "three_year_avg": 17.0, "industry": 15.0}
  },
  "growth_metrics": {
    "revenue": {"yoy": 58.1, "cagr": 45.0, "trend": "▲"},
    "operating_profit": {"yoy": 178.7, "cagr": 120.0, "trend": "▲"},
    "pbt": {"yoy": 45.7, "cagr": 40.0, "trend": "▲"},
    "pat": {"yoy": -21.2, "cagr": 15.0, "trend": "▼"},
    "eps": {"yoy": -21.2, "cagr": 12.0, "trend": "▼"},
    "total_assets": {"yoy": 38.5, "cagr": 35.0, "trend": "▲"}
  }
}
```

**Enhanced Multi-Year Data** (if 3+ years available):

You may also receive `_multi_year_trends` with actual year-by-year values:
```json
{
  "_multi_year_trends": {
    "years": ["2024", "2023", "2022"],
    "trends": {
      "revenue": {"current": 3.25b, "2023": 2.06b, "2022": 1.82b},
      "profit before tax": {"current": 525k, "2023": 360k, "2022": 320k}
    },
    "cagrs": {
      "revenue_cagr_2yr": 33.6,
      "profit before tax_cagr_2yr": 28.1
    }
  }
}
```

**How to Use**:
- **Trend Analysis**: Show FY2022 → FY2023 → FY2024 progression in your tables
- **CAGR Accuracy**: Use actual CAGRs from multi-year data (more accurate than estimates)
- **Pattern Recognition**: Identify if growth is accelerating (2022→23 < 2023→24) or decelerating
- **Outlier Detection**: Is FY2024 performance normal or exceptional relative to 2-year history?

## Output Format

Write **ONLY** the markdown content for Sections XII-XIII. Use this exact structure:

```markdown
# ⅩⅡ. Profitability Analysis - [Descriptive Title]

**Table 1: Profitability Indicators**
| Indicator | FY2024 | FY2023 | Change |
|---|---:|---:|---:|
| Gross margin | [%] | [%] | [+/-ppt] |
| PBT margin | [%] | [%] | [+/-ppt] |
| Net margin (PAT) | [%] | [%] | [+/-ppt] |
| PATMI margin | [%] | [%] | [+/-ppt] |
| Basic EPS (sen) | [Value] | [Value] | [+%] |

**Insights**
1. [First insight on margin trajectory]
2. [Second insight on profitability quality]
3. [Third insight on per-share value creation]
4. [Fourth insight on industry comparison]

**Table 2: Return Metrics**
| Indicator | FY2024 | FY2023 | Interpretation |
|---|---:|---:|---|
| Approx. ROE | [%] | [%] | [Interpretation] |
| Approx. ROA | [%] | [%] | [Interpretation] |

**Insights**
1. [First insight on return improvement]
2. [Second insight on capital productivity]
3. [Third insight on leverage vs. operational drivers]

**Conclusion**: [One paragraph on profitability trajectory]

# ⅩⅢ. Growth Capability Analysis - [Descriptive Title]

**Table 1: Growth Indicators**
| Indicator | FY2024 | FY2023 | Observation |
|---|---:|---:|---|
| Revenue growth | [+%] | [+%] | [Context] |
| Gross profit growth | [+%] | [+%] | [Context] |
| PAT growth | [+%] | [+%] | [Context] |
| PATMI growth | [+%] | [+%] | [Context] |
| Total assets growth | [+%] | [+%] | [Context] |
| Equity growth | [+%] | [+%] | [Context] |

**Insights**
1. [First insight on growth breadth]
2. [Second insight on quality vs. scale]
3. [Third insight on balance sheet expansion]
4. [Fourth insight on sustainable growth capacity]

**Table 2: Growth Support Indicators**
| Support Indicator | FY2024 | FY2023 | Interpretation |
|---|---:|---:|---|
| Group capex | [Value] | [Value] | [Interpretation] |
| Operating cash flow | [Value] | [Value] | [Interpretation] |

**Insights**
1. [First insight on reinvestment intensity]
2. [Second insight on internal funding capacity]
3. [Third insight on capex productivity]

**Conclusion**: [One paragraph on growth sustainability]
```

## Quality Standards

- ✅ Analyze margin trends critically
- ✅ Connect ROE to DuPont components
- ✅ Assess growth quality vs. quantity
- ✅ Compare to industry benchmarks

**Do NOT**:
- ❌ Just list the numbers
- ❌ Ignore negative trends
- ❌ Make unsupported claims

## Task

Using the data bundle provided, write Sections XII-XIII following the guidelines above.

**Output file**: `workspace/worker_5_sections.md`

Output ONLY the markdown for these two sections.
