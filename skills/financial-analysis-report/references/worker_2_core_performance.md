# Worker 2: Core Performance Analysis (Sections IV-V)

You write the most critical sections: executive summary and core financial performance. Keep it concise, analytical, and actionable.

## Your Task: Write Sections IV-V

### Section IV: Core Conclusions (150 words, 3-5 bullets)

**Purpose**: Key takeaways upfront - what should investors know immediately?

**Structure**:
```markdown
## Ⅳ. Core Conclusions

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
> - **Scale expansion is clear**: Revenue grew 58% YoY to RM3.25b, driven by construction recovery and East Malaysia expansion. However, margin dilution in new markets (8-10% vs 15-18% in Peninsula) raises quality concerns.
> - **Operating efficiency improved**: Operating margin expanded 7pp to 16% through vertical integration, but attributable margin compressed (7.1% → 3.5%) due to rising minority interests from JVs.
> - **Cash conversion weakened**: Despite accounting profits, operating cash flow remains negative (-RM60m FCF) due to receivables expansion in new markets, signaling execution risk.

**Bad Example**:
> - Performance improved significantly
> - Revenue grew substantially
> - The company did well

---

### Section V: Core Financial Performance (200 words)

**Purpose**: Present fundamental performance metrics with analysis

**Required Table**:
```markdown
**Table 1: Key Performance Metrics**

| Metric | Current | Prior | Change | YoY % |
|--------|---------|--------|--------|-------|
| Revenue | [X] | [Y] | [Δ] | [+Z%] |
| Operating Profit | [X] | [Y] | [Δ] | [+Z%] |
| PBT | [X] | [Y] | [Δ] | [+Z%] |
| PAT | [X] | [Y] | [Δ] | [+Z%] |
| Attributable Profit | [X] | [Y] | [Δ] | [+Z%] |
| Basic EPS (sen) | [X] | [Y] | [Δ] | [+Z%] |

**Performance Analysis**

[Explain the "why" behind the numbers - 3-4 paragraphs]

**Key Findings**:
- [Insight 1: Connect top-line to bottom-line growth]
- [Insight 2: Explain margin trajectory]
- [Insight 3: Assess attribution dilution (if any)]
```

**What to analyze**:
1. **Top-line vs bottom-line gap**: Why did revenue grow faster/slower than profits?
2. **Margin trajectory**: Are margins expanding or compressing? Why?
3. **Attribution dilution**: Is attributable profit growing slower than PAT?
4. **EPS trajectory**: Is per-share value keeping pace?

**Good Analysis**:
> Revenue growth (+58% YoY) significantly outpaced PBT growth (+46% YoY), indicating margin dilution from:
> - **Mix shift**: East Malaysian markets carry lower margins (8-10%) vs. Peninsula (15-18%)
> - **Input cost lag**: Steel prices rose 20% in H2, only 12% passed through
> - **Startup costs**: New Sabah plant incurred RM15m pre-operating expenses
>
> Attributable margin compression (7.1% → 3.5%) reflects rising minority interests from JVs (40-49% ownership), raising questions about growth quality.

**Bad Analysis**:
> Revenue increased from RM2.06b to RM3.25b. Operating profit went up. PBT also increased. The table shows the numbers changed.

---

## Your Data Bundle

You receive a JSON object with metrics and margins:

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

## Output Format

Write ONLY markdown for Sections IV-V:

```markdown
## Ⅳ. Core Conclusions

- **[Insight]**: [Analysis] (1-2 sentences)
... (3-5 bullets total)

## Ⅴ. Core Financial Performance

**Table 1: Key Performance Metrics**

| Metric | Current | Prior | Change | YoY % |
|--------|---------|--------|--------|-------|
[Filled from data bundle]

### Performance Analysis

[Your analysis - explain WHY, not just WHAT]

**Key Findings**:
- [Insight 1]
- [Insight 2]
- [Insight 3]
```

## Quality Checklist

✅ Use actual numbers from data bundle
✅ Explain drivers behind the numbers
✅ Connect revenue growth to profit conversion
✅ Assess quality of earnings

❌ Don't: Just describe what happened
❌ Don't: Use vague language
❌ Don't: Ignore negative trends
❌ Don't: Make unsupported claims

## Task

Write Sections IV-V using the data bundle. Output ONLY markdown for these two sections.
