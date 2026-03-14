# Worker 5: Profitability & Growth Analysis (Sections XII-XIII)

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

## Output Format

Write **ONLY** the markdown content for Sections XII-XIII. Use this exact structure:

```markdown
## Ⅻ. Profitability Analysis

| Ratio | Current | Prior | 3-Year Avg | Industry |
|-------|---------|--------|------------|----------|
[Fill in from data bundle]

### Profitability Assessment

[Your insights here]

## ⅩⅢ. Growth Capability Analysis

| Metric | YoY Growth | 3-Year CAGR | Trend |
|--------|------------|-------------|-------|
[Fill in from data bundle]

### Growth Sustainability

[Your insights here]
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

Using the data bundle provided, write Sections XII-XIII following the guidelines above. Output ONLY the markdown for these two sections.
