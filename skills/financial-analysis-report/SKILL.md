---
name: financial-analysis-report
description: >
  Generate financial analysis reports from parsed annual report data. You decide the report structure,
  analysis depth, agent workflow, and section organization — this skill provides tools and guidance only.

  ALWAYS use this skill when the user wants to: create financial analysis reports, analyze company performance,
  generate investment research, compare financials across years, assess risk profile, write research reports,
  analyze financial statements, or produce professional financial analysis documents. Triggers on:
  "analyze this company", "create financial report", "generate analysis report", "analyze financial performance",
  "write research report", "assess financial health", "compare financial statements", or when user provides
  financial data (PDFs, fs_index.json files) and asks for analysis.
---

# Financial Analysis Report

Generate financial analysis reports from parsed annual report data. You decide the report structure, what to analyze, and how to organize it. This skill provides the tools.

## Tools

### 1. Data Extraction

```bash
python scripts/data_extractor.py <fs_index.json> [options]
```

| Flag | What it does |
|---|---|
| `--metric <name>` | Extract one or more specific line items (exact then substring match) |
| `--category <name>` | Extract all items from a statement: `income_statement`, `balance_sheet`, `cash_flow` |
| `--search <keyword>` | Fuzzy search line items by key or label |
| `--list` | List all available fields grouped by statement (deduplicated) |
| `--text-search <query>` | Search annual report text for a keyword (reads `text_blocks.jsonl` from same directory) |
| `--text-page <range>` | Extract text from a page range, e.g. `45-60` |

Every output includes a `source` field for traceability. Not-found metrics return explicit `null` with guidance.

### 2. Ratio Calculation

```bash
python scripts/financial_calculator.py <fs_index.json> [options]
```

| Flag | What it does |
|---|---|
| (none) | Calculate all ratios: profitability, liquidity, solvency, efficiency, cashflow |
| `--category <name>` | Calculate one category: `profitability`, `liquidity`, `solvency`, `efficiency`, `cashflow` |
| `--prior <file>` | Add YoY growth rates and ratio changes (needs prior year fs_index.json) |
| `--trend <year:file>` | Add multi-year trend analysis (CAGR, volatility, direction) for 3+ years |

All calculations use raw RM'000 values. Output is always JSON.

### 3. Report Validation

```bash
python scripts/validate_report.py <report.md> --data <fs_index.json> [--prior <prior.json>]
```

Post-generation audit. Checks every number in the report against source data:
- **MISMATCH** — reported value differs from fs_index (>0.1% tolerance)
- **UNVERIFIABLE** — number can't be traced to any known data source (possible fabrication)
- **ROUNDED_DERIVATION** — value may have been computed from rounded intermediates

## Anti-Fabrication Rule

Every number in the report must come from a tool call. If you did not query a metric, do not use its value. Missing data is "not disclosed" — never guess.

## Workflow

1. **Parse PDF** with `finanalysis parse <pdf> --company <NAME> -o output/<NAME>/<YEAR>`
2. **Explore data** — use tools to understand what's available and what stands out
3. **Decide structure** — based on data characteristics, choose what to cover and how deep
4. **Write** — optionally use parallel agents for different sections
5. **Validate** — run `validate_report.py` to audit all numbers before delivering

## Prerequisites

```bash
pip install git+https://github.com/GuoxinShan/finanalysis.git
```

Verify: `finanalysis --version`

## References

- [data_catalog.md](references/data_catalog.md) — All available line items, calculable ratios, and unit conventions. Read this to understand what data you can query.
- [writing_guidelines.md](references/writing_guidelines.md) — Precision rules, tone guidance, and unit formatting standards.
