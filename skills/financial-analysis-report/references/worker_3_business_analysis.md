# Worker 3: Business & Strategy (Section IV)

## Data Access

Your financial metrics are **PRE-LOADED** in your prompt (text excerpts, page hints).

For detailed business context (segments, strategy, MD&A, industry), read `text_blocks.jsonl` from the path in your bundle:

```python
import json
text_blocks = []
with open(text_blocks_path, 'r') as f:
    for line in f:
        text_blocks.append(json.loads(line))
```

**Do NOT** read `fs_index.json`, `data_bundles.json`, or any other `.json` files — your metrics are already provided.

---

You are responsible for segment performance, industry impact, and strategic execution. Go deeper than surface-level observations — assess whether strategy is translating to financial outcomes.

## Canonical Data Ownership

**You own**: Segment revenue/PBT, order book, geographic mix, industry impact assessment, strategic scorecard.
**Do NOT restate**: Revenue totals, gross margin, profit figures — those belong to Section III. Reference Section III if needed.

---

## Your Section

### Section IV: Business & Strategy

**Purpose**: Comprehensive business analysis covering segments, industry context, and strategic execution. This section answers "what does this company actually do, and how well are they doing it?"

**Required Tables** (3 tables):

```markdown
**Table 1: Segment Revenue (RM million)**
| Segment | FY2024 | FY2023 | YoY % | Share |
|---------|--------|--------|-------|-------|
| [Segment] | [Value] | [Value] | [+%] | [%] |
| **Total** | **[Value]** | **[Value]** | **[+%]** | **100%** |

**Table 2: Segment Profitability (RM million)**
| Segment | FY2024 | FY2023 | YoY % | Margin |
|---------|--------|--------|-------|--------|
| [Segment] | [Value] | [Value] | [+%] | [%] |
| **Total** | **[Value]** | **[Value]** | **[+%]** | **[%]** |

**Table 3: Strategic Scorecard**
| Initiative | Evidence | Assessment |
|------------|----------|------------|
| [M&A / Capex / Expansion] | [Specific action + financial impact] | [Effective/Mixed/Concerning] |
```

**Analysis** (3 paragraphs):

1. **Segment dynamics**: Which segments drove growth? Are margins improving or deteriorating at segment level? Is the mix shifting toward higher-value businesses? Use text_blocks.jsonl for management commentary on segment performance.

2. **Industry impact**: How did external factors (demand, regulation, input costs) directly affect this company's results? Be specific — connect industry signals to company-specific financial outcomes. No generic macro commentary (GDP, OPR).

3. **Strategic execution**: Are strategic moves translating to financial outcomes? Is M&A paying off? Is capex generating returns? Is the company disciplined about capital allocation? Be critical — this is not a press release.

**What NOT to include**:
- Plant locations, product descriptions, or operational details
- Lists of individual projects (keep order book aggregate only)
- Digital transformation bullet lists (BIM, RPA, AI) without quantified financial impact
- Sustainability / ESG initiatives without financial materiality
- Macroeconomic background (GDP growth rates, OPR decisions)
- Sub-sections per subsidiary

---

## Output Format

Write **ONLY** markdown for Section IV:

```markdown
# Ⅳ. Business & Strategy - [Descriptive Title]

**Table 1: Segment Revenue (RM million)**
| Segment | FY2024 | FY2023 | YoY | Share |
|---|---:|---:|---:|---:|
| [Data] | [Data] | [Data] | [%] | [%] |

**Table 2: Segment Profitability (RM million)**
| Segment | FY2024 | FY2023 | YoY | Margin |
|---|---:|---:|---:|---:|
| [Data] | [Data] | [Data] | [%] | [%] |

**Table 3: Strategic Scorecard**
| Initiative | Evidence | Assessment |
|---|---|---|
| [Initiative] | [Evidence] | [Assessment] |

**Analysis**
1. [Segment dynamics paragraph]
2. [Industry impact paragraph]
3. [Strategic execution paragraph]
```

## Quality Standards

- Use actual segment data if available
- Connect industry trends to company-specific performance
- Assess strategic execution critically — not a press release

**Do NOT**:
- Invent segment data if not provided
- Write generic macro commentary
- Include operational filler (plant lists, product catalogs)

## Task

Write Section IV using the data bundle.

**Output file**: `workspace/worker_3_sections.md`

Output ONLY markdown for this section.
