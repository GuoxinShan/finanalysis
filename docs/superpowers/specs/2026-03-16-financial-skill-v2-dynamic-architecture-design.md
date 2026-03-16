# Financial Analysis Report Skill v2 — Dynamic Architecture

**Date**: 2026-03-16
**Status**: Approved

## Problem

The current `financial-analysis-report` skill uses a fixed architecture: 6+1 specialized worker agents, a rigid 9-section report structure, a canonical data ownership table, and a fixed assembly pipeline. This works but is inflexible — every company gets the same report template regardless of its data characteristics.

## Design Decision

Replace the fixed workflow with a fully dynamic approach. The skill provides **tools** (data extraction, ratio calculation, validation) and **light guidance** (writing style, precision, units). The model decides everything else: report structure, analysis depth, agent workflow, section organization.

## Architecture

```
financial-analysis-report/
├── SKILL.md                          # ~70 lines: tools + workflow + pointers
├── scripts/
│   ├── data_extractor.py             # Extract metrics + search text from fs_index
│   ├── financial_calculator.py       # Calculate derived financial ratios
│   └── validate_report.py            # Post-generation data verification
└── references/
    ├── data_catalog.md               # Available line items, calculable ratios, unit system
    └── writing_guidelines.md         # Merged tone + precision + units (light)
```

### Deleted Files

All worker instruction files (worker_1–worker_7), canonical_data_registry.md, output_format_specification.md, assemble_report.py, extract_worker_bundle.py, generate_report.py, prepare_workspace.py, manual_workflow.md, troubleshooting.md, quick_start_examples.md, data_format.md, example_worker_extraction.py.

## Tool Design

### data_extractor.py

CLI tool for querying both structured metrics and unstructured text from parsed financial data.

```bash
# Structured data (fs_index.json)
python scripts/data_extractor.py <fs_index.json> --metric revenue
python scripts/data_extractor.py <fs_index.json> --category income_statement
python scripts/data_extractor.py <fs_index.json> --search "borrowing"
python scripts/data_extractor.py <fs_index.json> --list

# Text data (text_blocks.jsonl, co-located with fs_index.json)
python scripts/data_extractor.py <fs_index.json> --text-search "management discussion"
python scripts/data_extractor.py <fs_index.json> --text-search "risk factor" --top 10
python scripts/data_extractor.py <fs_index.json> --text-page 45-60
```

**Output format** — every response includes source traceability:
```json
{"label": "revenue", "group_current": 3252347, "group_prior": 2057210, "unit": "RM'000", "source": "fs_index.json line_items['revenue']"}
```

Not-found returns explicit null:
```json
{"label": "customer_concentration", "value": null, "message": "not found in fs_index. try --text-search for qualitative data."}
```

### financial_calculator.py

CLI tool for computing derived financial ratios from fs_index.json.

```bash
python scripts/financial_calculator.py <fs_index.json>               # All ratios
python scripts/financial_calculator.py <fs_index.json> --category profitability
python scripts/financial_calculator.py <fs_index.json> --prior <prior.json>   # YoY growth
python scripts/financial_calculator.py <fs_index.json> --trend 2022:<f1> 2023:<f2>  # Multi-year
```

All calculations use raw RM'000 values. Output includes unit annotations.

### validate_report.py

Post-generation audit script. Extracts all numbers from the final report and cross-references against fs_index.json.

```bash
python scripts/validate_report.py report.md --data fs_index.json [--prior fs_index_2023.json]
```

Three issue categories:
- **MISMATCH** — reported value differs from source (>0.1% tolerance)
- **UNVERIFIABLE** — number cannot be traced to any known data source (possible fabrication)
- **ROUNDED_DERIVATION** — value appears derived from rounded intermediate (e.g., NCI% = 97.1/215.5 instead of 97078/215492)

## Anti-Fabrication Rules

SKILL.md enforces a hard rule: every number in the report must originate from a tool call. If a metric was not queried, it cannot appear in the report. Missing data is marked "not disclosed" — never guessed.

Tools reinforce this by:
1. Always returning source traceability metadata
2. Explicitly returning `null` with guidance for unfound metrics
3. validate_report.py performing a post-generation audit

## References

### data_catalog.md

Three sections:
1. **Structured data** — all fs_index line items grouped by statement (income statement, balance sheet, cash flow), with entity×period availability
2. **Calculable ratios** — all ratios from financial_calculator grouped by category (profitability, liquidity, solvency, efficiency, cashflow, growth, trend)
3. **Unit system** — RM'000 for amounts, sen for EPS, %/pp/bps for ratios, days for efficiency, parentheses for negative cash flows

Loaded on demand via Read tool, not embedded in SKILL.md.

### writing_guidelines.md

Merged from existing tone_guidelines.md + writing_standards.md + precision_quick_reference.md, trimmed to ~150 lines. Covers:
- Precision: calculate from raw values, round only for display
- Tone: professional, objective, specific — explain WHY not just WHAT
- Units: standard display conventions
- Anti-patterns: over-hedging, emotional language, generic statements

Section-specific tone guidance removed (no fixed sections to reference).

## SKILL.md Structure (~70 lines)

```
Frontmatter: name + description (trigger description)

# Financial Analysis Report
One paragraph: generate reports from parsed data, you decide structure/depth/agents.

## Tools
### 1. Data Extraction (all flags)
### 2. Ratio Calculation (all flags)
### 3. Report Validation

## Anti-Fabrication Rule
Hard rule: every number must come from a tool call.

## Workflow
1. Parse PDF with finanalysis CLI
2. Explore data with tools
3. Decide report structure based on data characteristics
4. Write (optionally with parallel agents)
5. Validate with validate_report.py

## References
- data_catalog.md
- writing_guidelines.md
```

## What Changes vs. Current

| Dimension       | Current                    | New                        |
|-----------------|----------------------------|----------------------------|
| SKILL.md        | 370 lines                  | ~70 lines                  |
| Scripts         | 6 (generate, extract, assemble, prepare, validate, calculator) | 3 (extractor, calculator, validator) |
| Reference files | 14                         | 2                          |
| Worker defs     | 7                          | 0                          |
| Report structure | Fixed 9 sections           | Model decides              |
| Agent workflow  | Fixed 6+1 parallel         | Model decides              |
| Data ownership  | Canonical registry         | Not needed (single source) |
