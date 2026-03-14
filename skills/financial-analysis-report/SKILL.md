---
name: financial-analysis-report
description: >
  Create professional 18-section financial analysis reports and executive summaries using parallel agents for context efficiency.
  Spawns 7 specialized workers: Context Setup, Core Performance, Business Analysis, Operational Health,
  Profitability & Growth, Risk & Cash Flow analysis, and Executive Summary generation. Each worker handles 2-3 sections with focused context.

  ALWAYS use this skill when the user wants to: create financial analysis reports, analyze company performance,
  generate investment research, compare financials across years, assess risk profile, write research reports,
  analyze financial statements, or produce professional financial analysis documents. Triggers on:
  "analyze this company", "create financial report", "generate analysis report", "analyze financial performance",
  "write research report", "assess financial health", "compare financial statements", or when user provides
  financial data and asks for analysis.
---

# Financial Analysis Report - Parallel Agent Architecture

This skill generates professional 18-section financial analysis reports using a **coordinator + parallel workers** pattern to avoid context limits and enable scalable report generation.

## Architecture Overview

```
Coordinator Agent (you)
    ↓
    1. Parse fs_index.json and extract metrics
    2. Prepare focused data bundles for each worker
    3. Launch 6 parallel worker agents for report sections
    4. Collect and assemble worker outputs into full report
    5. Launch worker 7 for executive summary generation
    6. Generate final report files
    ↓
7 Parallel Workers (spawned via Agent tool)
    - Worker 1: Context Setup (Sections I-III)
    - Worker 2: Core Performance (Sections IV-V)
    - Worker 3: Business Analysis (Sections VI-VIII)
    - Worker 4: Operational Health (Sections XIV-XV)
    - Worker 5: Profitability & Growth (Sections XII-XIII)
    - Worker 6: Risk & Cash Flow (Sections IX-XI, XVI-XVIII)
    - Worker 7: Executive Summary (4-section summary from full report)
```

## Quick Start

The fastest way to generate a complete report:

**Phase 1: Preparation** (automated by script):
```bash
python scripts/generate_report.py \
  --pdf-2024 testdata/CHINHIN_Annual_Report_2024.pdf \
  --pdf-2023 testdata/CHINHIN_Annual_Report_2023.pdf \
  --company CHINHIN \
  --output-dir output/CHINHIN \
  --workspace workspace
```

This single command:
1. Parses PDFs with finanalysis CLI (auto-detects installation)
2. Calculates derived metrics
3. Generates data bundles for workers
4. Prepares workspace for parallel workers

**Phase 2: Worker Execution** (spawn workers):
After preparation completes, spawn 6 parallel workers to generate report sections.

**Phase 3: Assembly**:
```bash
python scripts/assemble_report.py \
  --workspace workspace \
  --output CHINHIN-2024-revised.md \
  --company CHINHIN \
  --period FY2024
```

**Phase 4: Summary Generation** (LLM-based):
Spawn worker 7 to generate executive summary from the full report.

This produces two files:
- **Full report**: `CHINHIN-2024-revised.md` (all 18 sections, ~8-12 pages)
- **Summary report**: `CHINHIN-summary.md` (4 sections, ~2-3 pages, LLM-generated)

## Output Format

### Full Report Structure (18 Sections)

The full report uses Roman numerals (Ⅰ-ⅩⅧ) and follows this pattern:

```
# [Company] [Period] Financial Analysis Report

Ⅰ. Company Profile
Ⅱ. Analysis Purpose
Ⅲ. Data Description
Ⅳ. Core Conclusions - [Descriptive Title]
Ⅴ. Core Financial Performance - [Descriptive Title]
Ⅵ. Analysis of Changes in Core Business - [Descriptive Title]
Ⅶ. Industry Change Analysis - [Descriptive Title]
Ⅷ. Strategic Initiatives Analysis - [Descriptive Title]
Ⅸ. Risk Scan - [Descriptive Title]
Ⅹ. Analysis of Major Items in the Three Statements - [Descriptive Title]
Ⅺ. Expense Analysis - [Descriptive Title]
Ⅻ. Profitability Analysis - [Descriptive Title]
ⅩⅢ. Growth Capability Analysis - [Descriptive Title]
ⅩⅣ. Solvency Analysis - [Descriptive Title]
ⅩⅤ. Operating Capability Analysis - [Descriptive Title]
ⅩⅥ. Cash Flow Analysis - [Descriptive Title]
ⅩⅦ. Asset Quality Analysis - [Descriptive Title]
ⅩⅧ. Future Forecast - [Descriptive Title]
```

**Section format** (sample pattern):
```markdown
# [Roman Numeral]. [Section Title] - [Descriptive Subtitle]

**Table N: [Table Title]**
| Column | FY2024 | FY2023 | YoY | Comment |
|---|---:|---:|---:|---|
| [Item] | [Value] | [Value] | [+%] | [Note] |

**Insights**
1. [First key insight with evidence]
2. [Second insight connecting data points]
3. [Third insight on implications]

**Conclusion**: [Summary paragraph]
```

### Summary Report Structure (4 Sections)

The executive summary extracts key highlights:

```
# [Company] [Period] Financial Analysis Summary

1. Key Conclusions
   - Extracted from Section Ⅳ (Core Conclusions table)

2. Data Parsing
   - Core metrics from Section Ⅴ
   - Profitability from Section Ⅻ
   - Solvency from Section ⅩⅣ

3. Trend Analysis
   - Synthesized from Sections Ⅴ, Ⅻ, ⅩⅣ
   - Revenue, margin, and solvency trajectories

4. Risk Warning
   - Extracted from Section Ⅸ (Risk Scan)
   - Top risks and mitigants
```

## Summary Report Generation

The summary report is **generated by Worker 7 (LLM-based)** from the full report with 4 key sections:

1. **Key Conclusions** - Extracted from Section Ⅳ (Core Conclusions)
2. **Data Parsing** - Extracted from Section Ⅲ (Data Description) + Section Ⅴ (Core Performance table)
3. **Trend Analysis** - Synthesized from Sections Ⅴ, Ⅻ, ⅩⅣ
4. **Risk Warning** - Extracted from Section Ⅸ (Risk Scan)

**Generation process**:
After assembling the full report, spawn Worker 7 with:
- Full report path
- Company name
- Period
- Worker 7 instructions (from `references/worker_7_summary.md`)

Worker 7 reads the full report and synthesizes the executive summary following the 4-section format specified in the sample report (`sample-report/4677-summary.md`).

**Why LLM-based?** The summary requires interpretation and synthesis across multiple sections, not just extraction. An LLM can identify the most important insights and maintain narrative coherence better than a script.

The summary provides a 2-3 page executive overview suitable for quick stakeholder updates.

## Prerequisites

### 1. Install the finanalysis CLI

**Option A: Install from GitHub (Recommended)**
```bash
pip install git+https://github.com/GuoxinShan/finanalysis.git
```

**Option B: Install from PyPI (if published)**
```bash
pip install finanalysis
```

**Option C: Install from source (for development)**
```bash
git clone https://github.com/GuoxinShan/finanalysis.git
cd finanalysis
pip install -e .
```

Verify installation:
```bash
finanalysis --version
finanalysis --help
```

**Note**: The `generate_report.py` script will auto-detect the CLI installation location, including virtual environments.

### 2. Prepare Financial Data

- **fs_index.json** from finanalysis CLI (parsed annual/quarterly report)
- **Prior year fs_index.json** for YoY comparison (optional but recommended)
- Understanding of the company's business model

If fs_index.json doesn't exist, use `generate_report.py` to parse PDFs automatically.

## Coordinator Workflow

### Method 1: End-to-End Automation (Recommended)

Use `scripts/generate_report.py` to automate the entire pipeline:

```bash
python scripts/generate_report.py \
  --pdf-2024 <path/to/2024.pdf> \
  --pdf-2023 <path/to/2023.pdf> \
  --company <NAME> \
  --output-dir output/<NAME> \
  --workspace workspace
```

**What it does**:
1. **PDF Parsing**: Auto-detects and runs finanalysis CLI to parse PDFs
2. **Metrics Calculation**: Runs `finanalysis calculate` to derive financial ratios
3. **Data Bundle Generation**: Creates worker-specific data bundles
4. **Worker Preparation**: Sets up workspace with instructions

**After running workers** (see Step 2 below), assemble the final report:

```bash
python scripts/assemble_report.py \
  --workspace workspace \
  --output <TICKER>-<PERIOD>-revised.md \
  --company <NAME> \
  --period <PERIOD>
```

This assembles worker outputs in correct section order.

---

### Method 2: Manual Step-by-Step (For Control)

#### Step 1: Extract and Prepare Data Bundles

If you already have fs_index.json files:

```bash
python scripts/data_extractor.py output/2024/fs_index.json \
  --company CHINHIN \
  --prior output/2023/fs_index.json \
  --output workspace/data_bundles.json
```

**Robust CLI Detection**: The script automatically finds finanalysis CLI in:
- System PATH
- Common virtual environment locations (`../finanalysis/.venv`, `./venv`, etc.)
- Python module imports

**Real Data Extraction**: Extracts actual values from fs_index.json line_items - no placeholders:
- Revenue, gross profit, PBT, PAT, attributable profit
- Operating margins, PBT margins, PAT margins
- Balance sheet items: assets, liabilities, equity
- Current ratio, quick ratio, working capital

#### Step 2: Launch Parallel Workers (Workers 1-6)

Spawn 6 worker agents in parallel using the Agent tool. Each worker receives:
- **Focused context**: Only the sections they need to write (~100-300 lines)
- **Data bundle**: Pre-calculated metrics, ratios, and trends
- **Worker instructions**: Clear guidance from `references/worker_N_*.md`

**Example for Worker 2 (Core Performance)**:
```python
# Read worker instructions
worker_2_instructions = Read("references/worker_2_core_performance.md")

# Read data bundle
data_bundles = Read("workspace/data_bundles.json")

# Spawn worker
worker_2 = Agent(
    subagent_type="general-purpose",
    description="Core performance analysis",
    prompt=f"""
{worker_2_instructions}

**Your Data Bundle**:
{data_bundles['worker_2']}

**Task**: Write Sections IV and V following the instructions above.
Output ONLY the markdown content for these two sections.
    """,
    model="sonnet"  # Use sonnet for quality
)
```

**Launch all 6 workers in a single turn**:
```python
workers = [
    Agent(subagent_type="general-purpose", description="Context setup", prompt=worker_1_prompt),
    Agent(subagent_type="general-purpose", description="Core performance", prompt=worker_2_prompt),
    Agent(subagent_type="general-purpose", description="Business analysis", prompt=worker_3_prompt),
    Agent(subagent_type="general-purpose", description="Operational health", prompt=worker_4_prompt),
    Agent(subagent_type="general-purpose", description="Profitability & growth", prompt=worker_5_prompt),
    Agent(subagent_type="general-purpose", description="Risk & cash flow", prompt=worker_6_prompt),
]
```

#### Step 3: Collect Worker Outputs

Each worker returns markdown content for their assigned sections. Collect all outputs:

```python
# Wait for all workers to complete
outputs = [wait_for_agent(w) for w in workers]

# Organize by section
sections = {
    "I-III": outputs[0],
    "IV-V": outputs[1],
    "VI-VIII": outputs[2],
    "XIV-XV": outputs[3],
    "XII-XIII": outputs[4],
    "IX-XI-XVI-XVIII": outputs[5],
}
```

#### Step 4: Assemble Full Report

Combine worker outputs in correct order:

```markdown
# Financial Analysis Report: [Company Name] - [Period]

[Worker 1: Sections I-III]

[Worker 2: Sections IV-V]

[Worker 3: Sections VI-VIII]

[Worker 6: Sections IX, X, XI]

[Worker 5: Sections XII-XIII]

[Worker 4: Sections XIV-XV]

[Worker 6: Sections XVI-XVIII]
```

Write to: `<TICKER>-<PERIOD>-revised.md` (full 18-section report)

#### Step 5: Generate Executive Summary (Worker 7)

Spawn Worker 7 to generate the executive summary from the full report:

```python
# Read worker 7 instructions
worker_7_instructions = Read("references/worker_7_summary.md")

# Spawn worker 7
worker_7 = Agent(
    subagent_type="general-purpose",
    description="Executive summary generation",
    prompt=f"""
{worker_7_instructions}

**Full Report Path**: CHINHIN-2024-revised.md
**Company**: CHINHIN
**Period**: FY2024

**Task**: Read the full report and generate a 4-section executive summary following the instructions.
Write the summary to: CHINHIN-summary.md
    """,
    model="sonnet"  # Use sonnet for quality
)
```

Worker 7 produces: `<TICKER>-<PERIOD>-summary.md` (4-section executive summary)

#### Step 6: Quality Check

Before delivering, verify:
- [ ] All 18 sections present and in correct order
- [ ] Tables formatted correctly
- [ ] No duplicate or missing content
- [ ] Consistent terminology across sections
- [ ] All metrics referenced in data bundles appear in report

## Worker Instruction Files

Each worker has dedicated instructions in `references/`:

- `worker_1_context_setup.md` - Sections I-III (Company Profile, Purpose, Data Description)
- `worker_2_core_performance.md` - Sections IV-V (Core Conclusions, Core Financial Performance)
- `worker_3_business_analysis.md` - Sections VI-VIII (Segment Analysis, Industry, Strategy)
- `worker_4_operational_health.md` - Sections XIV-XV (Solvency, Operational Capability)
- `worker_5_profitability_growth.md` - Sections XII-XIII (Profitability, Growth Capability)
- `worker_6_risk_cashflow.md` - Sections IX-XI, XVI-XVIII (Risk, Expenses, Major Items, Cash Flow, Asset Quality, Forecast)
- `worker_7_summary.md` - Executive Summary (4-section summary from full report)

**Important**: Workers only see their assigned instruction file, keeping context focused.

## Data Bundle Structure

Each worker receives a JSON data bundle with:

```json
{
  "worker_N": {
    "metadata": {
      "company_name": "...",
      "period": "...",
      "currency": "...",
      "fiscal_year_end": "..."
    },
    "metrics": {
      "revenue": 3252347,
      "pbt": 525602,
      ...
    },
    "ratios": {
      "operating_margin": 16.15,
      "current_ratio": 1.32,
      ...
    },
    "yoy_changes": {
      "revenue_growth": 58.1,
      "margin_change": 6.99,
      ...
    },
    "benchmarks": {
      "operating_margin_benchmark": 15.0,
      ...
    }
  }
}
```

The `data_extractor.py` script calculates all metrics, ratios, and comparisons upfront so workers can focus on interpretation.

## Quality Standards

Each worker must follow these principles:

1. **Explain WHY, not just WHAT** - Numbers tell a story; interpret it
2. **Be specific, not generic** - Use actual data from the bundle
3. **Connect the dots** - Link insights within your sections
4. **Be forward-looking** - Assess implications and risks
5. **Write for the user** - Professional but accessible

See `references/writing_standards.md` for detailed guidance.

## Tools and Scripts

### `scripts/generate_report.py` ⭐ **NEW**
End-to-end automation script that orchestrates the entire workflow:
- Auto-detects and runs finanalysis CLI for PDF parsing
- Calculates derived metrics using `finanalysis calculate`
- Generates data bundles for workers
- Prepares workspace with instructions
- **Usage**: `python scripts/generate_report.py --pdf-2024 <path> --company <NAME> ...`

**Key Features**:
- **Robust CLI Finding**: Searches PATH, common venv locations, and Python modules
- **Skip Flags**: `--skip-pdf-parsing`, `--skip-metrics`, `--skip-bundles` for incremental runs
- **Error Handling**: Clear error messages with actionable steps

### `scripts/assemble_report.py` ⭐ **NEW**
Assembles worker outputs into final report in correct section order:
- Reads worker output files from workspace
- Combines in proper section order (I-III, IV-V, VI-VIII, IX-XI, XII-XIII, XIV-XV, XVI-XVIII)
- Adds report header with company name and period
- **Usage**: `python scripts/assemble_report.py --workspace <dir> --output <file> --company <NAME> --period <PERIOD>`

### `scripts/data_extractor.py`
Extracts metrics and prepares data bundles for workers:
- Parses fs_index.json line_items to extract real values
- Calculates all ratios and metrics (no placeholders)
- Computes YoY changes and trends
- Compares against benchmarks
- Outputs structured JSON for workers
- **Enhanced**: Now extracts real data with verification metadata

### `scripts/financial_calculator.py`
Standalone ratio calculator (can be used independently):
```bash
python scripts/financial_calculator.py output/2024/fs_index.json \
  --prior output/2023/fs_index.json \
  --benchmark \
  --format markdown
```

## Example Usage

**User says**: "Analyze Chin Hin Group's 2024 financial performance"

**Your process (Automated)**:
1. Run `python scripts/generate_report.py --pdf-2024 CHINHIN_2024.pdf --pdf-2023 CHINHIN_2023.pdf --company CHINHIN --output-dir output/CHINHIN`
2. Script parses PDFs, calculates metrics, prepares data bundles
3. Spawn 6 parallel workers with focused instructions (see Step 2 above)
4. Collect worker outputs as they complete
5. Run `python scripts/assemble_report.py --workspace workspace --output CHINHIN-2024-revised.md --company CHINHIN --period FY2024`
6. Spawn worker 7 to generate executive summary from the full report
7. Deliver `<TICKER>-<PERIOD>-revised.md` and `-summary.md` to user

**Your process (Manual - if fs_index.json already exists)**:
1. Check for fs_index.json at `output/CHINHIN/2024/fs_index.json`
2. Extract data bundles: `python scripts/data_extractor.py ...`
3. Spawn 6 parallel workers with focused instructions
4. Collect worker outputs as they complete
5. Assemble full report using `assemble_report.py`
6. Spawn worker 7 to generate executive summary
7. Deliver to user

## Benefits of Parallel Architecture

✅ **Context Efficiency**: Each worker sees ~100-300 lines, not the full skill
✅ **Scalability**: Can add more sections without hitting context limits
✅ **Parallel Execution**: 7 workers run efficiently (6 for sections + 1 for summary)
✅ **Focused Expertise**: Each worker specializes in specific sections
✅ **Consistent Data**: All workers use same pre-calculated metrics
✅ **LLM-Based Summary**: Worker 7 provides intelligent synthesis, not just extraction

## Troubleshooting

**Problem**: `generate_report.py` cannot find finanalysis CLI
**Solution**: The script searches multiple locations automatically. If still not found:
- **Option 1**: Install it: `pip install git+https://github.com/GuoxinShan/finanalysis.git`
- **Option 2**: Activate venv: `source ../finanalysis/.venv/bin/activate`
- **Option 3**: Use `--skip-pdf-parsing` if fs_index.json already exists

**Problem**: Worker output missing required sections
**Solution**:
- Verify worker instructions explicitly list section headers
- Check that data bundle contains all required metrics
- Ensure worker prompt includes output format template

**Problem**: Inconsistent metrics across sections
**Solution**:
- Ensure all workers use the same data_bundles.json (no recalculation)
- Verify data_extractor.py extracted real values (check `_verification` metadata)
- Run `finanalysis calculate` once and reuse the metrics.json

**Problem**: Duplicate content between workers
**Solution**:
- Review worker assignments for overlapping responsibilities
- Each worker should only see their assigned instruction file
- Workers should output ONLY their assigned sections

**Problem**: Context still too large for worker
**Solution**:
- Worker instructions have been streamlined for efficiency
- Each worker sees ~100-300 lines of instructions
- If still too large, further simplify data bundle format

**Problem**: Worker completion times vary widely
**Solution**:
- Worker 2 (Core Performance) has most complex analysis - expected to take longer
- Simplified instructions now reduce variance
- Use `sonnet` model for quality (not `haiku`)

**Problem**: Data bundles contain zeros or placeholders
**Solution**:
- Verify fs_index.json has actual data (not empty line_items)
- Check data_extractor.py output for `_verification.data_quality: "REAL_DATA_EXTRACTED"`
- Ensure finanalysis CLI successfully parsed the PDF

**Problem**: Manual assembly required - no automation
**Solution**:
- Use `scripts/assemble_report.py` to automate combining worker outputs
- Run after all workers complete: `python scripts/assemble_report.py --workspace workspace --output report.md --company NAME --period FY2024`

## Summary

This skill uses parallel agents to generate comprehensive financial analysis reports without context overflow. As the coordinator, you:

1. Extract data once using `data_extractor.py`
2. Launch 6 specialized workers in parallel (for report sections)
3. Collect and assemble their outputs
4. Launch worker 7 to generate executive summary
5. Deliver a professional 18-section report + executive summary

The parallel architecture ensures each worker has focused context, enabling deep analysis without hitting token limits.

Now go create insightful financial reports! 🎯
