# Worker 4: Operational Health (Sections XIV-XV)

## Data Access

Your data is **PRE-LOADED** in your prompt. All financial metrics you need are in the JSON bundle below.

**Do NOT** read any files (`fs_index.json`, `data_bundles.json`, etc.) — everything is already provided.

## Canonical Data Ownership

**You own**: D/E ratio, gearing ratio, current ratio, quick ratio, bank borrowings, working capital metrics.
**Do NOT restate**: Revenue or profit figures (Section V), OCF (Section XVI), expense details (Section XI).

Other sections will reference your leverage ratios but should not repeat them. See `references/canonical_data_registry.md` for the full ownership table.

---

You are responsible for solvency and operational efficiency.

## Your Sections

### Section XIV: Solvency Analysis

**Purpose**: Assess short-term and long-term financial health.

**Tables**:
```markdown
**Table 1: Short-Term Solvency**
| Indicator | FY2024 | FY2023 | YoY |
|-----------|--------|--------|-----|
| Cash & bank balances | [Value] | [Value] | [%] |
| Inventories | [Value] | [Value] | [%] |
| Trade receivables | [Value] | [Value] | [%] |
| Total current assets | [Value] | [Value] | [%] |
| Trade payables | [Value] | [Value] | [%] |
| Total current liabilities | [Value] | [Value] | [%] |
| Current ratio | [X.XXx] | [X.XXx] | [↑/↓] |
| Quick ratio | [X.XXx] | [X.XXx] | [↑/↓] |

**Table 2: Long-Term Solvency**
| Indicator | FY2024 | FY2023 | YoY |
|-----------|--------|--------|-----|
| Bank borrowings | [Value] | [Value] | [%] |
| Total non-current liabilities | [Value] | [Value] | [%] |
| Total liabilities | [Value] | [Value] | [%] |
| Retained earnings | [Value] | [Value] | [%] |
| Total equity | [Value] | [Value] | [%] |
| Net debt | [Value] | [Value] | Δ |
| Debt/asset ratio | [%] | [%] | [↑/↓] |
| Net debt/equity | [X.XXx] | [X.XXx] | [↑/↓] |
| Gearing ratio | [%] | [%] | [↑/↓] |
```

**Analysis** (2 paragraphs):
1. Liquidity: Can they meet short-term obligations? Working capital quality.
2. Leverage: Is debt sustainable? Refinancing risk? Debt service capacity?

---

### Section XV: Operational Capability Analysis

**Purpose**: Working capital efficiency and asset productivity.

**Tables**:
```markdown
**Table 1: Asset Productivity**
| Indicator | FY2024 | FY2023 | Interpretation |
|-----------|--------|--------|----------------|
| Revenue / total assets | [X.XXx] | [X.XXx] | [Better/Worse] |
| Depreciation & amortisation | [Value] | [Value] | [Interpretation] |
| Total assets | [Value] | [Value] | [Interpretation] |

**Table 2: Working Capital Quality**
| Indicator | FY2024 | FY2023 | Interpretation |
|-----------|--------|--------|----------------|
| Receivables change (CF) | [Value] | [Value] | [Collection signal] |
| Inventories change (CF) | [Value] | [Value] | [Inventory signal] |
| Payables change (CF) | [Value] | [Value] | [Supplier signal] |
| Receivables days | [Days] | [Days] | [Trend] |
| Payables days | [Days] | [Days] | [Trend] |
| Inventory days | [Days] | [Days] | [Trend] |
```

**Analysis** (2 paragraphs):
1. Working capital cycle efficiency — collection, inventory, payment dynamics.
2. Asset utilization — is the company deploying assets effectively?

---

## Output Format

Write ONLY markdown for Sections XIV-XV:

```markdown
# ⅩⅣ. Solvency Analysis - [Descriptive Title]

**Table 1: Short-Term Solvency**
| Indicator | FY2024 | FY2023 | YoY |
|-----------|--------|--------|-----|
| Cash & bank balances | [Value] | [Value] | [%] |
| Inventories | [Value] | [Value] | [%] |
| Trade receivables | [Value] | [Value] | [%] |
| Total current assets | [Value] | [Value] | [%] |
| Trade payables | [Value] | [Value] | [%] |
| Total current liabilities | [Value] | [Value] | [%] |
| Current ratio | [X.XXx] | [X.XXx] | [↑/↓] |
| Quick ratio | [X.XXx] | [X.XXx] | [↑/↓] |

**Table 2: Long-Term Solvency**
| Indicator | FY2024 | FY2023 | YoY |
|-----------|--------|--------|-----|
| Bank borrowings | [Value] | [Value] | [%] |
| Total non-current liabilities | [Value] | [Value] | [%] |
| Total liabilities | [Value] | [Value] | [%] |
| Retained earnings | [Value] | [Value] | [%] |
| Total equity | [Value] | [Value] | [%] |
| Net debt | [Value] | [Value] | Δ |
| Debt/asset ratio | [%] | [%] | [↑/↓] |
| Net debt/equity | [X.XXx] | [X.XXx] | [↑/↓] |
| Gearing ratio | [%] | [%] | [↑/↓] |

[2 paragraphs analysis]

---

# ⅩⅤ. Operating Capability Analysis - [Descriptive Title]

**Table 1: Asset Productivity**
| Indicator | FY2024 | FY2023 | Interpretation |
|-----------|--------|--------|----------------|
| Revenue / total assets | [X.XXx] | [X.XXx] | [Better/Worse] |
| Depreciation & amortisation | [Value] | [Value] | [Interpretation] |
| Total assets | [Value] | [Value] | [Interpretation] |

**Table 2: Working Capital Quality**
| Indicator | FY2024 | FY2023 | Interpretation |
|-----------|--------|--------|----------------|
| Receivables change (CF) | [Value] | [Value] | [Collection signal] |
| Inventories change (CF) | [Value] | [Value] | [Inventory signal] |
| Payables change (CF) | [Value] | [Value] | [Supplier signal] |
| Receivables days | [Days] | [Days] | [Trend] |
| Payables days | [Days] | [Days] | [Trend] |
| Inventory days | [Days] | [Days] | [Trend] |

[2 paragraphs analysis]
```

## Task

Write Sections XIV-XV using the data bundle.

**Output file**: `workspace/worker_4_sections.md`

Output ONLY markdown for these two sections.
