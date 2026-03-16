# Writing Guidelines

## Precision

**Calculate from raw values. Round only for display. Never derive metrics from rounded table values.**

```
CORRECT:  NCI = 215,492 - 114,818 = 97,078 → display as 97.1m
WRONG:    NCI = 215.5 - 114.8 = 100.7m  (error: 3.6m)
```

This matters most for:
- Subtraction (errors compound)
- Percentage calculations
- Derived ratios

## Units

| Type | Convention | Example |
|---|---|---|
| Amounts | RM xxx million (from RM'000 ÷ 1000) | RM 3,252.3 million |
| EPS | RM x.xx (from sen ÷ 100) | RM 0.28 |
| Percentage change | +X.Xpp or X.X percentage points | +2.3pp |
| Small margin change | X bps (basis points) | 180 bps |
| Ratios | X.XXx (times) | 1.67x |
| Days | X days | 92 days |
| Negative values | Parentheses | (RM 45.2m) |
| Currency symbol | RM (not MYR, not RM') | RM 3.25 billion |

## Tone

Professional, objective, specific. Explain WHY not just WHAT.

**Do:**
- "Revenue grew 58% YoY to RM 3.25 billion, driven by East Malaysia expansion"
- "Margin compression reflects competitive pressures in new markets"
- "Negative operating cash flow requires attention"

**Don't:**
- "Revenue increased significantly" (vague)
- "The company performed well" (meaningless)
- "Explosive growth" / "Crisis" / "Burning cash" (emotional)
- "It could perhaps maybe suggest" (over-hedging)

### Word Replacements

| Avoid | Use Instead |
|---|---|
| Explosive growth | Strong growth of X% |
| Crisis | Challenge |
| Dramatic collapse | Sharp decline of X% |
| Burning cash | Negative operating cash flow of RM X million |
| Good financial position | Net cash of RM X million, debt-to-equity of Y% |
| MYR 3.25b | RM 3.25 billion |
| Margin increased 2% | Margin improved 2pp |
| -RM 45m (in tables) | (RM 45m) |

## Anti-Patterns

1. **Over-hedging** — One "may/might/could" per paragraph max. Make clear judgments.
2. **Generic statements** — "The company faces various risks" means nothing. Be specific: "Customer concentration risk: top 3 = 60% of revenue".
3. **Describing without analyzing** — Don't list numbers. Interpret them. Every number should answer "so what?".
4. **Ignoring negatives** — Balance strengths with concerns for credibility.
5. **Over-templating** — Customize insights to the specific company, not generic fill.
6. **Data dumps** — Raw tables without narrative add no value. Weave numbers into analytical prose. If a metric is worth including, it's worth explaining why it matters.
7. **Missing context** — A single-year snapshot is rarely useful. Always provide YoY comparison, trend direction, or peer context.

## Depth Checklist

Before finalizing any section, verify:
- [ ] Does it explain **why** the numbers changed, not just **what** changed?
- [ ] Does it connect related metrics (e.g., revenue growth vs receivables growth)?
- [ ] Does it identify risks or concerns, not just positives?
- [ ] Does it use management commentary (`--text-search`) to support analysis?
- [ ] Would a professional analyst find this section informative, or just a restatement of the financial statements?
