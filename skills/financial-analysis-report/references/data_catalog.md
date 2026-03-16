# Data Catalog

Available financial data from `fs_index.json` (parsed by finanalysis CLI) and calculable ratios from `financial_calculator.py`.

---

## 1. Structured Data (fs_index.json)

### Metadata

| Field | Example | Description |
|---|---|---|
| `currency` | `"MYR"` | Reporting currency (auto-detected) |
| `fiscal_year_end` | `"2024-12-31"` | Fiscal year end date (ISO format) |
| `company_name` | `"CHINHIN"` | Company name (provided at parse time) |

### Line Items

Each line item has fields: `label`, `statement`, `section`, `page`, `group_current`, `group_prior`, `company_current`, `company_prior`.

**Entity dimensions:**
- `group_current` / `group_prior` — Consolidated group
- `company_current` / `company_prior` — Parent company only

**Values are in RM'000** (divide by 1000 for RM millions).

#### Income Statement (27 items)

| Label | fs_index key |
|---|---|
| Revenue | `revenue` |
| Cost of Sales | `cost of sales` |
| Gross Profit | `gross profit` |
| Distribution Expenses | `distribution expenses` |
| Administrative Expenses | `administrative expenses` |
| Other Expenses | `other expenses` |
| Other Income | `other income` |
| Finance Income | `finance income` |
| Finance Costs | `finance costs` |
| Fair Value Gain/(Loss) on Other Investments | `fair value gain/(loss) on other investments` |
| Gain/(Loss) on Disposal of Other Investments | `gain/(loss) on disposal of other investments` |
| Share of Results of Associates | `share of results of associates` |
| Share of Results of Joint Ventures | `share of results of joint ventures` |
| Profit Before Tax | `profit before tax` |
| Taxation | `taxation` |
| Profit for the Financial Year | `profit for the financial year` |
| Profit Attributable to Owners of the Parent | `profit for the financial year attributable to: owners of the parent` |
| Profit Attributable to Non-controlling Interests | `profit for the financial year attributable to: non-controlling interests` |
| Basic and Diluted EPS (sen) | `basic and diluted earnings per share (sen)` |
| Total Comprehensive Income | `total comprehensive income for the financial year` |

#### Balance Sheet (43 items)

| Label | fs_index key |
|---|---|
| Non-Current Assets | `non-current assets (non-current assets)` |
| Property, Plant and Equipment | `property, plant and equipment (non-current assets)` |
| Intangible Assets | `intangible assets (non-current assets)` |
| Investment Properties | `investment properties (non-current assets)` |
| Right-of-use Assets | `right-of-use assets (non-current assets)` |
| Investment in Associates | `investment in associates (non-current assets)` |
| Investment in Joint Ventures | `investment in joint ventures (non-current assets)` |
| Other Financial Assets | `other financial assets (non-current assets)` |
| Other Investments | `other investments (non-current assets)` |
| Deferred Tax Assets | `deferred tax assets (non-current assets)` |
| Current Assets | `current assets (current assets)` |
| Inventories | `inventories (current assets)` |
| Trade Receivables | `trade receivables (non-current assets)` |
| Other Receivables | `other receivables (current assets)` |
| Cash and Bank Balances | `cash and bank balances (current assets)` |
| Fixed Deposits with Licensed Banks | `fixed deposits with licensed banks (current assets)` |
| Assets Held for Sale | `assets held for sale (current assets)` |
| Contract Assets | `contract assets (current assets)` |
| Contract Costs | `contract costs (current assets)` |
| Tax Recoverable | `tax recoverable (current assets)` |
| Total Assets | `total assets (current assets)` |
| Equity Attributable to Owners | `equity attributable to owners of the parent (equity)` |
| Non-controlling Interests | `non-controlling interests (equity)` |
| Total Equity | `total equity (equity)` |
| Reserves | `reserves (equity)` |
| Share Capital | `share capital (equity)` |
| Treasury Shares | `treasury shares (equity)` |
| Non-Current Liabilities | `non-current liabilities (non-current liabilities)` |
| Bank Borrowings (non-current) | `bank borrowings (non-current liabilities)` |
| Lease Liabilities | `lease liabilities (non-current liabilities)` |
| Deferred Tax Liabilities | `deferred tax liabilities (non-current liabilities)` |
| Current Liabilities | `current liabilities (current liabilities)` |
| Trade Payables | `trade payables (non-current liabilities)` |
| Other Payables | `other payables (current liabilities)` |
| Contract Liabilities | `contract liabilities (current liabilities)` |
| Tax Payable | `tax payable (current liabilities)` |
| Total Liabilities | `total liabilities (current liabilities)` |

#### Cash Flow (64 items)

Key items (many adjustments exist — use `--search` to find specific items):

| Label | fs_index key |
|---|---|
| Operating Profit/(Loss) Before Working Capital Changes | `operating profit/(loss) before working capital changes (operating activities)` |
| Net Cash from Operating Activities | `net cash from operating activities (operating activities)` |
| Net Cash from Investing Activities | `net cash from investing activities (investing activities)` |
| Net Cash from Financing Activities | `net cash from financing activities (financing activities)` |
| Cash at Beginning of Year | `cash and cash equivalents at the beginning of the financial year` |
| Cash at End of Year | `cash and cash equivalents at the end of the financial year` |
| Tax Paid | `tax paid (operating activities)` |
| Interest Paid | `interest paid (operating activities)` |
| Interest Received | `interest received (operating activities)` |
| Dividend Received | `dividend received (investing activities)` |

---

## 2. Calculable Ratios (financial_calculator.py)

### Profitability

| Ratio | Formula | Unit |
|---|---|---|
| `operating_margin` | gross_profit / revenue × 100 | % |
| `pbt_margin` | profit_before_tax / revenue × 100 | % |
| `pat_margin` | profit_for_year / revenue × 100 | % |
| `attributable_margin` | attributable_profit / revenue × 100 | % |
| `roe` | attributable_profit / equity × 100 | % |
| `roa` | attributable_profit / total_assets × 100 | % |

### Liquidity

| Ratio | Formula | Unit |
|---|---|---|
| `current_ratio` | current_assets / current_liabilities | x |
| `quick_ratio` | (current_assets - inventories) / current_liabilities | x |
| `working_capital` | current_assets - current_liabilities | RM'000 |
| `cash_to_current_assets` | cash / current_assets × 100 | % |

### Solvency

| Ratio | Formula | Unit |
|---|---|---|
| `liabilities_to_assets` | total_liabilities / total_assets × 100 | % |
| `borrowings_to_assets` | bank_borrowings / total_assets × 100 | % |
| `net_debt_to_equity` | (bank_borrowings - cash) / equity | x |
| `equity_to_assets` | equity / total_assets × 100 | % |

### Efficiency

| Ratio | Formula | Unit |
|---|---|---|
| `receivables_days` | trade_receivables × 365 / revenue | days |
| `payables_days` | trade_payables × 365 / operating_expenses | days |
| `asset_turnover` | revenue / total_assets | x |

### Cash Flow

| Ratio | Formula | Unit |
|---|---|---|
| `ocf_to_revenue` | operating_cash_flow / revenue × 100 | % |
| `free_cash_flow` | OCF + investing_cash_flow (if negative) | RM'000 |
| `ocf_interest_coverage` | operating_cash_flow / finance_costs | x |
| `ocf_to_debt` | operating_cash_flow / bank_borrowings × 100 | % |

### With --prior (YoY Growth)

| Metric | Unit |
|---|---|
| revenue_growth | % |
| gross_profit_growth | % |
| pbt_growth | % |
| pat_growth | % |
| attributable_profit_growth | % |
| eps_growth | % |
| total_assets_growth | % |
| equity_growth | % |

### With --trend (3+ years)

| Metric | Description |
|---|---|
| CAGR | Compound annual growth rate (%) |
| volatility | Std dev of YoY growth (%) |
| direction | Strong Growth / Moderate Growth / Stable / Moderate Decline / Sharp Decline |
| consistency | Consistent / Volatile / Insufficient Data |

---

## 3. Unit System

| Type | Raw Value | Display | Example |
|---|---|---|---|
| Amounts | RM'000 | RM xxx million | 3,252,347 → RM 3,252.3 million |
| EPS | sen (cents) | RM x.xx | 28.0 sen → RM 0.28 |
| Percentages | % | 1 decimal place | 16.2% |
| Percentage change | pp (percentage points) | 1 decimal place | +2.3pp |
| Small changes | bps (basis points) | 0 decimal place | 180 bps |
| Ratios | x (times) | 2 decimal places | 1.67x |
| Days | days | 0 decimal place | 92 days |
| Negative cash flow | parentheses | (RM 45.2m) | Operating cash outflow |
