# Agent Instructions for finanalysis CLI

This file provides instructions for AI agents on how to install and use the finanalysis CLI.

## Installation

Install the CLI before using any finanalysis commands:

```bash
# Recommended: Install from GitHub
pip install git+https://github.com/GuoxinShan/finanalysis.git

# Alternative: Install from PyPI (if published)
pip install finanalysis
```

Verify installation:
```bash
finanalysis --version
finanalysis --help
```

## Available Skills

### financial-analysis-report

**Location**: `skills/financial-analysis-report/`

**Purpose**: Generate professional 18-section financial analysis reports from parsed annual reports.

**When to use**:
- User asks to analyze company performance
- User wants to create financial reports
- User provides financial data and requests analysis
- User asks to "analyze this company", "create financial report", "generate analysis report"

**Prerequisites**:
1. Install finanalysis CLI (see above)
2. Parse annual report PDF:
   ```bash
   finanalysis parse report.pdf --company "Company Name" -o output/COMPANY/2024
   ```
3. Ensure `fs_index.json` exists in output directory

**How to invoke**:
Use the Skill tool with the skill name:
```python
Skill(skill="financial-analysis-report")
```

## Common Workflows

### 1. Parse a Financial Report

```bash
# Parse PDF and extract structured data
finanalysis parse annual_report_2024.pdf --company "Chin Hin" -o output/CHINHIN/2024

# This creates:
# - output/CHINHIN/2024/fs_index.json (236+ extracted line items)
# - output/CHINHIN/2024/metrics.json (25+ calculated ratios)
```

### 2. Query Metrics

```bash
# Single metric lookup
finanalysis query revenue -c CHINHIN -y 2024 -d output/CHINHIN/2024

# Time series query
finanalysis query-series revenue -c CHINHIN -d output/CHINHIN/2023 -d output/CHINHIN/2024

# Compare across years
finanalysis compare output/CHINHIN/2023 output/CHINHIN/2024
```

### 3. Calculate Derived Metrics

```bash
# Calculate financial ratios (requires current and prior year)
finanalysis calculate output/CHINHIN/2024/fs_index.json \
    --prior output/CHINHIN/2023/fs_index.json \
    --output output/CHINHIN/2024/metrics.json
```

### 4. Generate Analysis Report

After parsing and calculating metrics, invoke the skill:
```python
Skill(skill="financial-analysis-report")
```

The skill will:
1. Read `fs_index.json` and `metrics.json`
2. Launch 6 parallel worker agents
3. Generate an 18-section professional financial analysis report

## Output Files

All outputs stored in the specified output directory:

| File | Description |
|------|-------------|
| `fs_index.json` | **Structured financial data** - 236+ line items from balance sheet, income statement, cash flow |
| `metrics.json` | **Calculated ratios** - 25+ derived metrics (ROE, margins, liquidity ratios, etc.) |
| `text_blocks.jsonl` | Raw text extraction from PDF |
| `table_rows.jsonl` | Raw table extraction from PDF |
| `summary.json` | Processing statistics and metadata |

## Key Features

- **Zero LLM cost**: Deterministic pattern matching, no API calls needed
- **High accuracy**: 94.8% on benchmark tests (55/58 questions)
- **Fast**: ~38 seconds for 330-page PDF
- **Multi-currency support**: MYR, USD, SGD, HKD, EUR, GBP, CNY, IDR, THB, INR, AUD, JPY
- **Multi-year analysis**: Register and query across multiple years

## Troubleshooting

### Command not found
```bash
# Ensure CLI is installed
pip install git+https://github.com/GuoxinShan/finanalysis.git

# Verify installation
which finanalysis
finanalysis --version
```

### Missing dependencies
```bash
# Install system dependencies for PDF processing
# macOS:
brew install tesseract ghostscript

# Ubuntu/Debian:
sudo apt-get install tesseract-ocr ghostscript
```

### PDF parsing errors
```bash
# Force reprocess (ignore cache)
finanalysis parse report.pdf --company "Name" -o output --force

# Run specific stage
finanalysis parse report.pdf --stage 3
```

## Project Structure

```
finanalysis/
├── src/finanalysis/          # Main package
│   ├── cli.py                # Click CLI commands
│   ├── pipeline.py           # PDF processing pipeline
│   ├── fs_index.py           # Structured extraction (Stage 4)
│   ├── report_index.py       # Multi-company/year registry
│   └── calculators/          # Financial metrics calculation
├── skills/
│   └── financial-analysis-report/  # Agent skill for report generation
└── README.md                 # Full documentation
```

## Support

- **Documentation**: https://github.com/GuoxinShan/finanalysis#readme
- **Issues**: https://github.com/GuoxinShan/finanalysis/issues
- **Repository**: https://github.com/GuoxinShan/finanalysis
