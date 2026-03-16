# Worker 3: Business Analysis

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

## Canonical Data Ownership

**You own**: Segment revenue/PBT, order book, geographic mix.
**Do NOT restate**: Revenue totals, gross margin, profit figures — those belong to Section V. Reference Section V if needed.

---

## Your Task

Write your sections using the data bundle.

**Output file**: `workspace/worker_3_sections.md`

Output ONLY markdown for your assigned sections.

---

**Role:** Analyze business segments, competitive dynamics, external factors, and management execution.

**Tone:** Professional, objective, specific. See [writing_guidelines.md](writing_guidelines.md).

---

## Section VI: Segment Performance

Break down the Group's revenue and profitability by business segment. Identify which segments are driving growth, which are dragging, and how the revenue mix is shifting. Search text_blocks for keywords: "segment", "division", "business segment" to find segment disclosure text.

### VI.1 Revenue by Segment

Revenue table with YoY comparison and share analysis:

| Segment | FY2024 Revenue | FY2023 Revenue | Growth | Share FY2024 | Share FY2023 |
|---------|---------------|---------------|--------|-------------|-------------|
| [Segment 1] | RM X million | RM Y million | +Z% | A% | B% |
| [Segment 2] | RM X million | RM Y million | +Z% | A% | B% |
| [Segment 3] | RM X million | RM Y million | +Z% | A% | B% |
| **Total** | **RM X million** | **RM Y million** | **+Z%** | **100%** | **100%** |

Pie chart for revenue composition:

```mermaid
pie title "Revenue by Segment (FY2024)"
    "[Segment 1]" : [value]
    "[Segment 2]" : [value]
    "[Segment 3]" : [value]
```

### VI.2 Segment Profitability

| Segment | FY2024 Margin | FY2023 Margin | Change | Contribution to Group PBT |
|---------|--------------|--------------|--------|--------------------------|
| [Segment 1] | X% | Y% | +Zpp | A% |
| [Segment 2] | X% | Y% | +Zpp | A% |
| [Segment 3] | X% | Y% | +Zpp | A% |

**Insight**: [2-3 sentence analysis paragraph interpreting the segment profitability dynamics — which segments are expanding or compressing margins, why, and what this signals about the group's earnings quality.]

### VI.3 Key Findings & Tracking

| Finding | Data | Interpretation |
|---------|------|----------------|
| [e.g., "Growth driver"] | [Segment + growth %] | [Why this segment grew] |
| [e.g., "Margin leader"] | [Segment + margin %] | [Profitability dynamics] |
| [e.g., "Mix shift"] | [Share change] | [Strategic direction] |

[1 sentence on overall segment strategy — how management is positioning the portfolio and what the mix shift indicates about future earnings composition.]

**Tracking Recommendations**:
- [Bullet 1: Key metric or disclosure to monitor for the highest-growth segment]
- [Bullet 2: Segment-level margin trend to watch and why it matters]
- [Bullet 3: Emerging segment or revenue mix shift that warrants attention in the next reporting period]

---

## Section VII: Industry & Competitive Landscape

Assess the company's competitive position, industry trends, and external factors affecting performance. Search text_blocks for keywords: "industry", "competition", "market", "regulation", "outlook", "strategy", "initiative".

### VII.1 Market Environment

| Trend | Impact | Evidence |
|-------|--------|----------|
| [Trend 1] | [Positive / Negative / Neutral] | [Data or management commentary] |
| [Trend 2] | [Positive / Negative / Neutral] | [Data or management commentary] |
| [Trend 3] | [Positive / Negative / Neutral] | [Data or management commentary] |

### VII.2 Competitive Position

| Dimension | Assessment | Evidence |
|-----------|-----------|----------|
| Market position | [Leader / Challenger / Niche] | [Share, ranking, or management claim] |
| Competitive advantage | [Cost / Scale / Brand / Technology / Regulatory] | [Supporting data or commentary] |
| Key vulnerability | [Specific threat] | [Evidence from financials or commentary] |

**Insight**: [2-3 sentence analysis paragraph synthesizing the competitive assessment — how sustainable is the current position, where are the defensibility gaps, and what differentiates this company from peers in the same market.]

### VII.3 Opportunities & Threats

| Factor | Signal | Impact | Materiality |
|--------|--------|--------|-------------|
| [Factor] | [Market signal] | [Company-specific impact] | High/Medium/Low |
| [Factor] | [Market signal] | [Company-specific impact] | High/Medium/Low |
| [Factor] | [Market signal] | [Company-specific impact] | High/Medium/Low |

[1 sentence on the dominant external factor — the single most consequential force shaping the company's outlook.]

**Tracking Recommendations**:
- [Bullet 1: Industry development or regulatory change to monitor]
- [Bullet 2: Competitive action or market share shift to watch]
- [Bullet 3: Macro or external factor with the highest potential impact on earnings]

---

## Section VIII: Management & Strategy

Evaluate management's strategic initiatives, capital allocation decisions, and execution track record. Search text_blocks for keywords: "strategy", "expansion", "acquisition", "dividend", "capital" for strategic initiatives and capital allocation data.

### VIII.1 Strategic Initiatives

| Initiative | Description | Year | Status |
|------------|-------------|------|--------|
| [Initiative 1] | [Brief description] | [FY] | Announced / In Progress / Completed |
| [Initiative 2] | [Brief description] | [FY] | Announced / In Progress / Completed |
| [Initiative 3] | [Brief description] | [FY] | Announced / In Progress / Completed |

### VIII.2 Capital Allocation

| Category | FY2024 | FY2023 | Trend |
|----------|--------|--------|-------|
| Capex | RM X million | RM Y million | [Up / Down / Stable] |
| Dividends | RM X million | RM Y million | [Up / Down / Stable] |
| Debt repayment | RM X million | RM Y million | [Up / Down / Stable] |
| Acquisitions | RM X million | RM Y million | [Up / Down / Stable] |

**Insight**: [2-3 sentence analysis paragraph interpreting the capital allocation priorities — where management is choosing to invest, what the spending pattern signals about growth phase, and whether the allocation is shareholder-friendly or growth-oriented.]

### VIII.3 Execution Assessment & Tracking

| Initiative | Financial Impact | Assessment |
|------------|-----------------|------------|
| [Initiative] | [Quantified impact] | Effective / Mixed / Concerning |
| [Initiative] | [Quantified impact] | Effective / Mixed / Concerning |
| [Initiative] | [Quantified impact] | Effective / Mixed / Concerning |

[1 sentence on management execution quality — overall track record of delivering on stated strategic goals.]

**Tracking Recommendations**:
- [Bullet 1: Key strategic milestone or deliverable to monitor in the next period]
- [Bullet 2: Capital allocation decision or spending trend to watch]
- [Bullet 3: Management guidance or target that can be tracked against actual outcomes]

---

## Output Format Summary

This worker produces visual-first analysis. Every section includes:

1. **Data tables** — structured financial data with YoY comparison
2. **Mermaid charts** — pie charts for mix/composition, bar charts for trends
3. **Finding tables** — concise rows with Finding / Data / Interpretation
4. **Insight paragraphs** — 2-3 sentence analytical synthesis after profitability, competitive, and capital allocation tables
5. **Tracking Recommendations** — 3 actionable bullets per section for ongoing monitoring
6. **One-sentence synthesis** — the key takeaway after each major sub-section

---

## Anti-Patterns

- No raw paragraphs of text. Use tables and charts instead.
- No vague adjectives. Every cell must contain specific data.
- No missing context. Always include YoY comparison or trend direction.
- No over-hedging. Make clear, evidence-backed judgments. One "may/might/could" per paragraph max.
- No generic statements. "The company faces various risks" means nothing. Be specific.
- No describing without analyzing. Every number should answer "so what?".
- No ignoring negatives. Balance strengths with concerns for credibility.
- No data dumps. Raw tables without narrative add no value. Weave numbers into analytical prose.
