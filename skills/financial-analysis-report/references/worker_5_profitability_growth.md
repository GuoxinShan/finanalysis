# Worker 5: Profitability & Growth Analysis

## Data Access

Your data is **PRE-LOADED** in your prompt. All financial metrics you need are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

---

## Canonical Data Ownership

**You own**: ROE, ROA, NCI % of PAT, attributable margin trajectory, DuPont decomposition, growth breadth analysis, growth quality assessment.
**Do NOT restate**: Revenue totals or growth % (Section V), gross margin (Section V), segment details (Section VI), leverage ratios (Section XIV), OCF (Section XVI).

---

## Your Task

Write your sections using the data bundle.

**Output file**: `workspace/worker_5_sections.md`

Output ONLY markdown for your assigned sections.

---

You analyze profitability trends, return metrics, DuPont decomposition, and growth trajectory. Your output is visual-first: charts, tables, then analytical prose. Every number should answer "so what?" — refer to [writing_guidelines.md](references/writing_guidelines.md) for tone, precision, and anti-patterns.

---

## Section XII: Return on Capital & Shareholder Returns

### XII.1 Profitability Overview

**Table: Return Metrics**

| Metric | FY2023 | FY2024 | Change | Signal |
|--------|--------|--------|--------|--------|
| ROE | [%] | [%] | [Δpp] | ✅/⚠️ |
| ROA | [%] | [%] | [Δpp] | ✅/⚠️ |
| PAT Margin | [%] | [%] | [Δpp] | ✅/⚠️ |
| PATMI Margin | [%] | [%] | [Δpp] | ✅/⚠️ |
| Gross Margin | [%] | [%] | [Δpp] | ✅/⚠️ |
| EPS (sen) | [X] | [Y] | [%] | ✅/⚠️ |
| NCI % of PAT | [%] | [%] | [Δpp] | ⚠️ if >10% |
| Asset Turnover | [X.XXx] | [Y.YYx] | [Δ] | ✅/⚠️ |

**Chart: Profitability Positioning**

```html
<table style="width:100%; text-align:center; border-collapse:collapse; font-size:13px;">
  <tr style="background:#f1f5f9;">
    <th style="padding:8px; border:1px solid #e2e8f0;"></th>
    <th style="padding:8px; border:1px solid #e2e8f0;">Low ROE (&lt;[threshold]%)</th>
    <th style="padding:8px; border:1px solid #e2e8f0;">High ROE (≥[threshold]%)</th>
  </tr>
  <tr>
    <td style="padding:8px; border:1px solid #e2e8f0; font-weight:600;">Low Growth</td>
    <td style="padding:8px; border:1px solid #e2e8f0;">⚠️/❌ Cash trap</td>
    <td style="padding:8px; border:1px solid #e2e8f0;">💰 Cash cow</td>
  </tr>
  <tr style="background:#f8fafc;">
    <td style="padding:8px; border:1px solid #e2e8f0; font-weight:600;">High Growth</td>
    <td style="padding:8px; border:1px solid #e2e8f0;">📈 Volume play</td>
    <td style="padding:8px; border:1px solid #e2e8f0;">⭐ Star</td>
  </tr>
</table>
```

Mark the company's actual position with **→ [Company]** in the appropriate cell.

**Insight**: [2-3 sentence DuPont decomposition analysis. Identify whether ROE change was driven by margin expansion, asset efficiency, or financial leverage. Connect to the positioning quadrant — is the company a Star, Cash cow, Volume play, or Cash trap, and why?]

### XII.2 DuPont Decomposition

**Table: DuPont Breakdown**

| Component | FY2024 | FY2023 | Change | Driver |
|-----------|--------|--------|--------|--------|
| Net profit margin | [%] | [%] | [Δpp] | ✅/⚠️ |
| Asset turnover | [X.XXx] | [Y.YYx] | [Δ] | ✅/⚠️ |
| Equity multiplier | [X.XXx] | [Y.YYx] | [Δ] | ✅/⚠️ |
| ROE (product) | [%] | [%] | [Δpp] | ✅/⚠️ |

> **Calculation**: ROE = Net profit margin × Asset turnover × Equity multiplier. Net profit margin = PATMI / Revenue. Asset turnover = Revenue / Total assets. Equity multiplier = Total assets / Total equity. Calculate from raw values; round only for display.

**Insight**: [2-3 sentence analysis on which DuPont component drove ROE change. Was it operational improvement (margin), capital efficiency (turnover), or financial engineering (leverage)? A healthy ROE increase driven by margin and turnover is more sustainable than leverage-driven gains. Flag if equity multiplier increase is the primary driver.]

### XII.3 Key Findings & Tracking

**Key Findings**

| Finding | Data | Interpretation |
|---------|------|----------------|
| [ROE trajectory] | [ROE: X% → Y%] | [Improving/declining — which DuPont component is responsible?] |
| [NCI dilution] | [NCI % of PAT] | [Material? Trend? Impact on minority vs parent returns?] |
| [Attributable quality] | [PATMI margin] | [Shareholder returns vs group profit — is NCI diluting parent returns?] |

[1 sentence DuPont summary — concise verdict on ROE quality and sustainability.]

**Tracking Recommendations**
- [Bullet 1: Track ROE composition — monitor whether margin gains are sustained or if leverage is increasing unsustainably]
- [Bullet 2: Watch NCI % of PAT — if trending up, minority shareholders are capturing growing share of group profits]
- [Bullet 3: Compare asset turnover trend — declining turnover with rising ROE may signal leverage dependency rather than operational improvement]

---

## Section XIII: Growth Trajectory

### XIII.1 Growth Rates

**Table: Growth Rates**

| Metric | FY2023 | FY2024 | Growth (%) |
|--------|--------|--------|------------|
| Revenue | [RM X million] | [RM Y million] | [%] |
| Gross Profit | [RM X million] | [RM Y million] | [%] |
| PAT | [RM X million] | [RM Y million] | [%] |
| PATMI | [RM X million] | [RM Y million] | [%] |
| Total Assets | [RM X million] | [RM Y million] | [%] |
| Total Equity | [RM X million] | [RM Y million] | [%] |
| EPS | [X sen] | [Y sen] | [%] |

**Chart: Growth Breadth**
```mermaid
xychart-beta
    title "Growth Rates (%)"
    x-axis [Gross Profit, PAT, PATMI, Total Assets, Equity]
    y-axis "%" [min] --> [max]
    bar [gp_growth, pat_growth, patmi_growth, ta_growth, eq_growth]
```

**Insight**: [2-3 sentence analysis on growth breadth and quality. Are growth rates broadly consistent across metrics (healthy breadth) or concentrated in top-line only (profit not keeping up)? Is asset growth outpacing revenue growth (potential over-investment)? Is EPS growth aligned with PAT growth (no dilution)?]

### XIII.2 Growth Quality

**Table: Growth Support**

| Item | FY2024 (RM'000) | Assessment |
|------|-----------------|------------|
| Operating Cash Flow | [value] | ✅/⚠️ |
| Capex / Investing Outflow | [value] | ✅/⚠️ |
| Free Cash Flow | [OCF + Investing] | ✅/⚠️ |
| OCF / Revenue | [%] | ✅/⚠️ |

**Table: Growth Quality Assessment**

| Dimension | Growth Rate | Quality Signal |
|-----------|-------------|----------------|
| Top-line → Bottom-line | [Revenue growth] → [PAT growth] | ✅ Converging / ⚠️ Diverging |
| Profit → EPS | [PAT growth] → [EPS growth] | ✅ Aligned / ⚠️ Diluted |
| Internal funding | [OCF] vs [Capex] | ✅ Self-funded / ⚠️ External dependent |
| Balance sheet capacity | [D/E trend] | ✅ Headroom / ⚠️ Stretched |

**Insight**: [2-3 sentence analysis on growth sustainability. Is growth being funded internally by operating cash flow or does it require external financing? If top-line growth is strong but PAT growth lags, what is compressing margins? Is the balance sheet absorbing growth or becoming stretched? Connect to DuPont findings from Section XII if relevant.]

### XIII.3 Key Findings & Tracking

**Tracking Recommendations**
- [Bullet 1: Monitor OCF / Revenue ratio — declining conversion may signal receivables/inventory buildup behind revenue growth]
- [Bullet 2: Track PAT-to-PATMI spread — widening gap means minority interests are absorbing more profit, reducing parent shareholder returns]
- [Bullet 3: Compare asset growth to revenue growth — if assets grow faster than revenue, asset turnover is declining (see DuPont XII.2) and returns may compress]

---

## Output Format

Your section output must follow this structure:

### Section XII: Return on Capital & Shareholder Returns
1. **XII.1 Profitability Overview** — Return Metrics table (8 rows), Profitability Positioning HTML quadrant chart, Insight paragraph
2. **XII.2 DuPont Decomposition** — DuPont Breakdown table (4 rows), Insight paragraph
3. **XII.3 Key Findings & Tracking** — Key Findings table (3 rows), 1-sentence DuPont summary, Tracking Recommendations (3 bullets)

### Section XIII: Growth Trajectory
4. **XIII.1 Growth Rates** — Growth Rates table (7 rows), Growth Breadth mermaid bar chart, Insight paragraph
5. **XIII.2 Growth Quality** — Growth Support table (4 rows), Growth Quality Assessment table (4 rows), Insight paragraph
6. **XIII.3 Key Findings & Tracking** — Tracking Recommendations (3 bullets)

**Formatting rules:**
- Tables use `✅` for healthy signals, `⚠️` for concerns, `❌` for critical issues
- All monetary values in RM'000 in tables; RM xxx million in prose (RM'000 / 1000)
- Percentages to 1 decimal place
- Use "pp" for changes >= 100bps, "bps" for changes < 100bps
- EPS in sen in tables; RM x.xx in prose (sen / 100)
- Mermaid charts use actual data values, not placeholders
- HTML quadrant chart threshold: use 10% for ROE unless industry context suggests otherwise
- Reference [writing_guidelines.md](references/writing_guidelines.md) for tone and precision rules
