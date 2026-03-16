# Worker 3: Business Analysis (Sections VI-VIII)

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

You are responsible for segment performance, industry impact, and strategic execution.

## Canonical Data Ownership

**You own**: Segment revenue/PBT, order book, geographic mix.
**Do NOT restate**: Revenue totals, gross margin, profit figures — those belong to Section V. Reference Section V if needed.

See `references/canonical_data_registry.md` for the full ownership table.

---

## Your Sections

### Section VI: Analysis of Changes in Core Business

**Purpose**: Segment-level performance and business model evolution.

**Tables** (if segment data available):
```markdown
**Table 1: Segment Revenue (RM million)**
| Segment | FY2024 | FY2023 | YoY % | Share |
|---------|--------|--------|-------|-------|
| [Segment] | [Value] | [Value] | [+%] | [%] |
| **Total** | **[Value]** | **[Value]** | **[+%]** | **100%** |

**Table 2: Segment PBT (RM million)**
| Segment | FY2024 | FY2023 | YoY % | Margin |
|---------|--------|--------|-------|--------|
| [Segment] | [Value] | [Value] | [+%] | [%] |
| **Total** | **[Value]** | **[Value]** | **[+%]** | **[%]** |
```

**Analysis** (1 paragraph): Which segments drove growth? Are margins improving or deteriorating at segment level? Is the mix shifting toward higher-value businesses?

**What NOT to include**:
- Plant locations, product descriptions, or operational details
- Lists of individual projects (keep order book aggregate only)
- Sub-sub-sections per subsidiary (VI.3.1, VI.3.2, etc.)
- Sub-segment detail beyond what the tables show (2-3 sentences max per segment in the analysis paragraph)

---

### Section VII: Industry Change Analysis

**Purpose**: External factors that materially impacted this company — only what's specific and actionable.

**Table**:
```markdown
**Table: Industry Impact Assessment**
| Factor | Signal | Impact on Company |
|--------|--------|-------------------|
| [Demand/cost/regulatory factor] | [Specific market signal] | [Specific impact on performance] |
```

**Analysis** (2-3 sentences): How did external factors directly affect this company's results?

**What NOT to include**:
- Macroeconomic background (GDP growth rates, OPR decisions, broad industry statistics) — these are annual report filler, not analysis
- Generic industry commentary that doesn't connect to company-specific performance
- Climate risk / TCFD assessments (not financial analysis at this level)
- Multiple sub-sections (VII.1, VII.2, etc.) — one table + 2-3 sentences is enough

---

### Section VIII: Strategic Initiatives

**Purpose**: Assess management's strategic execution and its financial impact.

**Table**:
```markdown
**Table: Strategic Initiatives Scorecard**
| Initiative | Evidence | Assessment |
|------------|----------|------------|
| [M&A / Capex / Expansion] | [Specific action + financial impact] | [Effective/Mixed/Concerning] |
```

**Analysis** (1 paragraph): Are strategic moves translating to financial outcomes? Is the acquisition pipeline paying off? Is execution disciplined?

**What NOT to include**:
- Digital transformation bullet lists (BIM, RPA, AI, IoT) without quantified financial impact
- Sustainability / ESG initiatives without financial materiality
- Detailed acquisition histories for minor deals (keep only major M&A)
- Plant-by-plant capacity tables (operational detail, not financial analysis)
- Sub-sections for each initiative category (VIII.1, VIII.2, etc.) — one table suffices

---

## Output Format

Write **ONLY** markdown for Sections VI-VIII:

```markdown
# Ⅵ. Analysis of Changes in Core Business - [Descriptive Title]

**Table 1: Segment Revenue (RM million)**
| Segment | FY2024 | FY2023 | YoY | Share |
|---|---:|---:|---:|---:|
| [Data] | [Data] | [Data] | [%] | [%] |

**Table 2: Segment PBT (RM million)**
| Segment | FY2024 | FY2023 | YoY | Margin |
|---|---:|---:|---:|---:|
| [Data] | [Data] | [Data] | [%] | [%] |

[1 paragraph analysis]

---

# Ⅶ. Industry Change Analysis - [Descriptive Title]

**Table: Industry Impact Assessment**
| Factor | Signal | Impact on Company |
|---|---|---|
| [Factor] | [Signal] | [Impact] |

[2-3 sentences]

---

# Ⅷ. Strategic Initiatives - [Descriptive Title]

**Table: Strategic Scorecard**
| Initiative | Evidence | Assessment |
|---|---|---|
| [Initiative] | [Evidence] | [Assessment] |

[1 paragraph analysis]
```

## Quality Standards

- Use actual segment data if available
- Connect industry trends to company-specific performance
- Assess strategic execution critically — not a press release

**Do NOT**:
- Invent segment data if not provided
- Write generic macro commentary
- Include operational filler (plant lists, product catalogs, project lists)

## Task

Write Sections VI-VIII using the data bundle.

**Output file**: `workspace/worker_3_sections.md`

Output ONLY markdown for these three sections.
