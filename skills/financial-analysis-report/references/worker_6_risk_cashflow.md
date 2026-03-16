# Worker 6: Risk Analysis (Sections IX-XI)

## Data Access

Your data is **PRE-LOADED** in your prompt. All risk metrics and debt structure data are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

---

You handle 3 sections covering risk identification, three-statement analysis, and expense structure. Be thorough but concise - focus on actionable insights.

## Your Sections

### Section IX: Risk Scan - Enhanced Risk Matrix (300 words)

**Purpose**: Identify, assess, and prioritize risks with actionable mitigation strategies

**CRITICAL**: Use the enhanced risk matrix format below. This transforms risk analysis from descriptive to actionable, enabling users to prioritize mitigation efforts.

**Required Table**:
```markdown
**Table: Risk Assessment Matrix**

| Risk Category | Specific Risk | Severity | Probability | Impact | Priority | Mitigation Timeline |
|---------------|--------------|----------|-------------|--------|----------|---------------------|
| **Liquidity Risk** | [Specific issue, e.g., Negative OCF (-RM60m) despite PAT of RM215m] | **Critical** | High | Covenant breach, funding gap | 1 - Immediate | 0-6 months |
| **Credit Risk** | [Specific issue, e.g., Contract assets +133% to RM495m] | **High** | Medium | Collection risk, write-downs | 2 - High | 6-12 months |
| **Leverage Risk** | [Specific issue, e.g., Debt/Equity at 211% (from 151%)] | **High** | High | Interest burden, refinancing risk | 2 - High | 6-12 months |
| **Integration Risk** | [Specific issue, e.g., Admin expenses +152% YoY] | **Medium** | High | Margin compression, cost overrun | 3 - Medium | 12-18 months |
| **Execution Risk** | [Specific issue, e.g., Working capital lockup RM2.09b] | **Medium** | Medium | Cash flow drag, opportunity cost | 3 - Medium | Ongoing |
| **Market Risk** | [Specific issue, e.g., Property sector slowdown] | **Medium** | Medium | Revenue decline, pricing pressure | 3 - Medium | Ongoing |
| **Operational Risk** | [Specific issue, e.g., Customer concentration (top 10 = 24.5%)] | **Low** | Low | Revenue volatility | 4 - Low | Monitor |

**Severity Scale**:
- **Critical**: Immediate action required, threatens business viability
- **High**: Urgent attention needed, significant financial impact
- **Medium**: Planned intervention, manageable with monitoring
- **Low**: Monitoring only, minimal immediate impact

**Risk Mitigation Actions by Priority**:

**Priority 1 - Critical (Immediate, 0-6 months)**:
- **Action 1**: [Specific mitigation with KPI, e.g., Cash Flow Management: Weekly monitoring and forecasting]
- **Action 2**: [e.g., Working Capital Optimization: Target 60% conversion of contract assets to cash within 12 months]
- **Action 3**: [e.g., Short-term Financing: Secure revolving credit facility for liquidity buffer]

**Priority 2 - High (6-12 months)**:
- **Action 1**: [e.g., Debt Restructuring: Refinance short-term debt (RM1,042m) to longer tenors]
- **Action 2**: [e.g., Cost Rationalization: Reduce admin expenses from 8.5% to 7.0% of revenue]
- **Action 3**: [e.g., Collection Process: Implement stricter credit terms and collection procedures]

**Priority 3 - Medium (12-18 months)**:
- **Action 1**: [e.g., Integration Synergies: Complete acquisition integration, target RM50m annual cost savings]
- **Action 2**: [e.g., Margin Recovery: Renegotiate supplier contracts, improve gross margin to 18%+]
- **Action 3**: [e.g., Segment Diversification: Expand commercial/industrial segments to reduce property dependency]

**Priority 4 - Low (Ongoing Monitoring)**:
- **Action 1**: [e.g., Customer Diversification: Monitor customer concentration, target top 10 <20% of revenue]
```

**Risk Scoring Guidance**:

Use data-driven thresholds to assess severity:

```python
# Liquidity Risk
if OCF < 0 and PAT > 0: Severity = "Critical"  # Profits not converting to cash
elif OCF < 0: Severity = "High"
elif OCF/PAT < 0.5: Severity = "Medium"
else: Severity = "Low"

# Leverage Risk
if Debt/Equity > 200%: Severity = "High"
elif Debt/Equity > 150%: Severity = "Medium"
else: Severity = "Low"

# Credit Risk
if Contract_Assets_YoY > 100%: Severity = "High"  # Rapid expansion signals collection risk
elif Contract_Assets_YoY > 50%: Severity = "Medium"
else: Severity = "Low"

# Integration Risk
if Admin_Expenses_YoY > Revenue_Growth * 1.5: Severity = "High"  # Costs outpacing growth
elif Admin_Expenses_YoY > Revenue_Growth: Severity = "Medium"
else: Severity = "Low"
```

**Analysis** (3-4 paragraphs):
1. **Critical Risks** (Priority 1): Immediate attention required, what happens if not addressed?
2. **High Risks** (Priority 2): What are the triggers and early warning indicators?
3. **Medium/Low Risks** (Priority 3-4): Monitoring approach and escalation criteria
4. **Overall Risk Profile**: Conservative/Moderate/Aggressive, trending direction, risk vs reward balance

**Good Example**:
> **Critical Risk**: Negative OCF (-RM60m) despite PAT of RM215m signals severe cash conversion issues. If unaddressed within 6 months, this could trigger covenant breaches and force emergency asset sales. Mitigation requires aggressive working capital optimization (target: release RM290m cash) and securing a revolving credit facility (RM150m buffer).

**Why This Matters**:
The enhanced risk matrix transforms risk analysis from passive identification to active prioritization. Users can immediately see:
- Which risks require **immediate action** vs monitoring
- **Quantified impact** and probability
- **Time-bound mitigation** strategies
- **Resource allocation** guidance (focus on Priority 1-2 first)

---

### Section X: Major Items in Three Statements (300 words)

**Purpose**: Deep dive into balance sheet, income statement, and cash flow

**Required Tables**:
```markdown
**Balance Sheet Summary**
| Item | Current | Prior | YoY % |
|------|---------|-------|-------|
| Total Assets | X | Y | +Z% |
| Total Liabilities | X | Y | +Z% |
| Total Equity | X | Y | +Z% |
| Net Debt | X | Y | Δ |

**Income Statement Summary**
| Item | Current | Prior | YoY % |
|------|---------|-------|-------|
| Revenue | X | Y | +Z% |
| Operating Expenses | X | Y | +Z% |
| PBT | X | Y | +Z% |
| PAT | X | Y | +Z% |

**Cash Flow Summary**
| Item | Current | Prior | Δ |
|------|---------|-------|---|
| Operating Cash Flow | X | Y | Δ |
| Investing Cash Flow | X | Y | Δ |
| Financing Cash Flow | X | Y | Δ |
| Net Cash Change | X | Y | Δ |
```

**Analysis** (1 paragraph per statement):
- **Balance sheet**: Asset/liability growth balance, capital structure changes
- **Income statement**: Revenue quality, cost structure, margin drivers
- **Cash flow**: Operating cash generation, investment intensity, financing needs
- **Synthesis**: Are profits backed by cash? Is growth funded sustainably?

**Good Example**:
> Despite PAT of RM215m, OCF was negative (-RM60m) due to RM95m receivables buildup and RM40m inventory expansion. FCF (after RM180m growth capex) was -RM240m, requiring debt funding.

---

### Section XI: Expense Analysis (200 words)

**Purpose**: Understand cost structure and efficiency

**Required Table**:
```markdown
| Expense Item | Amount (RM'000) | % of Revenue | YoY Change |
|--------------|-----------------|--------------|------------|
| Cost of Sales | X | Y% | Δ |
| Distribution Expenses | X | Y% | Δ |
| Administrative Expenses | X | Y% | Δ |
| Finance Costs | X | Y% | Δ |
| Taxation | X | Z% (of PBT) | Δ |
```

**Analysis** (3-4 paragraphs):
1. **Cost control**: Are expenses growing slower than revenue?
2. **Interest burden**: Are finance costs manageable?
3. **Tax efficiency**: Effective vs statutory rate
4. **Fixed vs variable mix**: Operating leverage potential

**Good Example**:
> Cost of sales (84% of revenue) rose 2pp YoY from steel prices (+20% input, 12% passed through) and lower-margin East Malaysian sales (85% COS vs 80% Peninsula). Admin expenses grew slower than revenue (12% vs 58%), demonstrating operating leverage.

---


## Your Data Bundle

You receive a JSON object with:
```json
{
  "risks": {
    "financial_risks": [...],
    "non_financial_risks": [...]
  },
  "balance_sheet": {...},
  "income_statement": {...},
  "cash_flow_statement": {...},
  "expenses": {...},
  "source_files": {
    "text_blocks_path": "...",
    "fs_index_path": "..."
  }
}
```

**Enhanced Multi-Year Data** (if 3+ years available):

You may also receive `_multi_year_trends`:
```json
{
  "_multi_year_trends": {
    "years": ["2024", "2023", "2022"],
    "trends": {
      "net cash from operating activities": {
        "current": 60200,
        "2023": 45000,
        "2022": 38000
      },
      "revenue": {
        "current": 3.25b,
        "2023": 2.06b,
        "2022": 1.82b
      }
    },
    "cagrs": {
      "revenue_cagr_2yr": 33.6,
      "net cash from operating activities_cagr_2yr": 25.9
    }
  }
}
```

**How to Use Multi-Year Data for Risk Analysis**:

1. **Risk Pattern Recognition (Section IX)**:
   - Is leverage increasing over 3 years? (trend risk)
   - Are margins compressing consistently? (structural risk)
   - Is working capital expanding faster than revenue? (execution risk)

**Example Risk Assessment**:
> "Leverage has increased consistently: Debt/Equity rose from 0.8x (FY2022) to 1.2x (FY2023) to 1.5x (FY2024). This 3-year trend indicates structural reliance on debt financing, raising refinancing risk if credit conditions tighten."

## Output Format

Write ONLY markdown for Sections IX, X, XI in that order. Use this exact structure:

```markdown
# Ⅸ. Risk Scan - [Descriptive Title]

**Table: Risk Assessment Matrix**
| Risk Category | Specific Risk | Severity | Probability | Impact | Priority | Mitigation Timeline |
|---|---|---|---|---|---|---|
| [Risk 1] | [Specific issue with data] | [Critical/High/Medium/Low] | [High/Medium/Low] | [Specific impact] | [1-4] | [Timeline] |
| [Risk 2] | [Specific issue with data] | [Critical/High/Medium/Low] | [High/Medium/Low] | [Specific impact] | [1-4] | [Timeline] |

**Risk Mitigation Actions by Priority**:

**Priority 1 - Critical (Immediate, 0-6 months)**:
- [Action 1 with specific KPI]
- [Action 2 with specific KPI]
- [Action 3 with specific KPI]

**Priority 2 - High (6-12 months)**:
- [Action 1 with specific KPI]
- [Action 2 with specific KPI]

**Priority 3 - Medium (12-18 months)**:
- [Action 1 with specific KPI]

**Priority 4 - Low (Ongoing Monitoring)**:
- [Monitoring approach]

**Insights**
1. [First insight on critical risks requiring immediate attention]
2. [Second insight on high-priority risks and early warning indicators]
3. [Third insight on overall risk profile and trend]
4. [Fourth insight on risk-return balance and strategic implications]

**Conclusion**: [One paragraph on risk management strategy]

# Ⅹ. Analysis of Major Items in the Three Statements - [Descriptive Title]

## Balance Sheet

**Table 1: Balance Sheet Key Items**
| Item | FY2024 | FY2023 | YoY | Analytical Point |
|---|---:|---:|---:|---|
| Total assets | [Value] | [Value] | [+%] | [Point] |
| Total equity | [Value] | [Value] | [+%] | [Point] |
| Total liabilities | [Value] | [Value] | [+%] | [Point] |

**Insights**
1. [First insight on balance sheet expansion]
2. [Second insight on capital structure changes]
3. [Third insight on asset composition shifts]

## Income Statement

**Table 2: Income Statement Key Items**
| Item | FY2024 | FY2023 | YoY | Analytical Point |
|---|---:|---:|---:|---|
| Revenue | [Value] | [Value] | [+%] | [Point] |
| Gross profit | [Value] | [Value] | [+%] | [Point] |
| PBT | [Value] | [Value] | [+%] | [Point] |

**Insights**
1. [First insight on revenue quality]
2. [Second insight on operating leverage]
3. [Third insight on cost structure]

## Cash Flow Statement

**Table 3: Cash Flow Statement Key Items**
| Item | FY2024 | FY2023 | YoY | Analytical Point |
|---|---:|---:|---:|---|
| Net cash from operating activities | [Value] | [Value] | [+%] | [Point] |
| Net cash used in investing activities | [Value] | [Value] | [+%] | [Point] |
| Net cash from/(used in) financing activities | [Value] | [Value] | n.m. | [Point] |

**Insights**
1. [First insight on cash generation quality]
2. [Second insight on investment intensity]
3. [Third insight on funding hierarchy]

**Conclusion**: [One paragraph on overall statement quality]

# ⅩⅠ. Expense Analysis - [Descriptive Title]

**Table 1: Expense Structure and Cost Ratios**
| Expense Indicator | FY2024 | FY2023 | YoY / Change |
|---|---:|---:|---:|
| [Expense item] | [Value] | [Value] | [+%] |
| [Cost ratio] | [%] | [%] | [+ppt] |

**Insights**
1. [First insight on cost control effectiveness]
2. [Second insight on finance cost burden]
3. [Third insight on operating leverage potential]
4. [Fourth insight on fixed vs. variable mix]

**Conclusion**: [One paragraph on expense management quality]
```

## Quality Checklist

✅ Comprehensive risk assessment with data-driven severity ratings
✅ Connect three-statement analysis to business performance
✅ Be specific: use actual numbers, not generic descriptions

❌ Don't: Ignore negative risks
❌ Don't: Just list numbers without interpretation

## Task

Write all three sections (IX, X, XI) using the data bundle.

**Output file**: `workspace/worker_6_sections.md`

Output ONLY markdown in correct section order.
