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

## Output Convention

Reports must be saved to `reports/<COMPANY>/<YEAR>/analysis_report.md`.

Use the same `<COMPANY>` and `<YEAR>` as the fs_index.json source. If no year is specified, use the `fiscal_year_end` from the data.

## Anti-Fabrication Rule

Every number in the report must come from a tool call. If you did not query a metric, do not use its value. Missing data is "not disclosed" — never guess.

## Workflow

1. **Parse PDF** with `finanalysis parse <pdf> --company <NAME> -o output/<NAME>/<YEAR>`
2. **Explore data** — `--list` to see all fields, `--category` to pull a statement, `--text-search` for narrative context. Decide what's noteworthy.
3. **Plan sections** — split the report into 3-5 independent sections based on what you found. Each section should have a clear analytical angle, not just a data category.
4. **Write with parallel agents** — dispatch one Agent per section (see below). Each agent independently queries data and writes its section.
5. **Assemble** — stitch sections together into a coherent report. Add cross-references between sections where metrics relate.
6. **Validate** — run `validate_report.py` to audit every number before delivering.

## Parallel Agent Strategy

Use the Agent tool to dispatch one subagent per report section. This produces deeper, more focused analysis because each agent dedicates its full context to one topic.

**How to split sections (examples):**
- Revenue & profitability | Balance sheet strength | Cash flow quality | Risk factors & outlook
- Segment performance | Capital structure | Working capital efficiency | Growth trajectory

**Each subagent brief must include:**
1. The fs_index path(s) and available tool commands (copy from Tools section above)
2. The specific section topic and what to analyze
3. Instruction to `--text-search` for management commentary on the topic
4. Reference to [writing_guidelines.md](references/writing_guidelines.md) for tone and units

**Each subagent should:**
- Query all relevant metrics for its topic (use `--metric`, `--category`, `--search`)
- Search annual report text for management's explanation (`--text-search`)
- Calculate relevant ratios (`financial_calculator.py`)
- Write 2-4 paragraphs of **analytical narrative** — not a data dump
- Surface risks, trade-offs, and what the numbers imply (not just what they are)

**Example subagent prompt:**
```
Write the "Revenue & Profitability" section of a financial analysis report.

Data: /path/to/fs_index.json (current year), /path/to/prior.json (prior year)

Available tools:
- python scripts/data_extractor.py <fs_index.json> --metric <names>
- python scripts/data_extractor.py <fs_index.json> --text-search <query>
- python scripts/financial_calculator.py <fs_index.json> --prior <prior.json>

Instructions:
1. Query revenue, gross profit, PBT, PAT, EPS and all profitability ratios
2. Search annual report text for management commentary on revenue drivers ("revenue", "segment", "growth")
3. Analyze: what drove revenue change, margin trends, profitability quality
4. Read references/writing_guidelines.md for tone and formatting
5. Output 2-4 paragraphs of analytical prose. No raw tables — weave numbers into narrative.
```

## Analysis Depth

Go beyond reporting numbers. For every metric you mention, answer: **so what?**

| Shallow (avoid) | Deep (target) |
|---|---|
| "Revenue grew 58% to RM 3.25 billion." | "Revenue grew 58% to RM 3.25 billion, driven by a 72% surge in the construction segment as the Group secured RM 2.1 billion in new contracts during the year. The growth was partially offset by a 12% decline in the trading division, suggesting the Group's strategic pivot toward project-based work is accelerating." |
| "Gross margin was 15.4%." | "Gross margin compressed 310bps to 15.4%, reflecting cost pressures from rising steel prices and labor shortages in East Malaysia. This is the third consecutive year of margin erosion — the Group will need to either renegotiate contracts or improve procurement efficiency to stabilize profitability." |
| "Current ratio was 1.67x." | "The current ratio of 1.67x provides adequate short-term liquidity, though this represents a decline from 1.88x in the prior year as trade payables grew 34% faster than current assets — a potential signal of stretched supplier payment terms." |

**Techniques for depth:**
- **Root cause**: Use `--text-search` to find management's explanation for changes
- **Trend context**: Use `--prior` to show multi-year trajectory, not just current snapshot
- **Cross-metric linkage**: Connect balance sheet changes to income statement performance (e.g., receivables growth vs revenue growth = collection risk)
- **Implication**: What does this mean for future performance, risk, or valuation?
- **Benchmark**: Is the metric strong or weak relative to its own history?

## Prerequisites

```bash
pip install git+https://github.com/GuoxinShan/finanalysis.git
```

Verify: `finanalysis --version`

## References

- [data_catalog.md](references/data_catalog.md) — All available line items, calculable ratios, and unit conventions. Read this to understand what data you can query.
- [writing_guidelines.md](references/writing_guidelines.md) — Precision rules, tone guidance, and unit formatting standards.
