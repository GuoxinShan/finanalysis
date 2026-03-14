---
name: financial-analysis-report
description: >
  Create professional 18-section financial analysis reports using parallel agents for context efficiency.
  Spawns 6 specialized workers: Context Setup, Core Performance, Business Analysis, Operational Health,
  Profitability & Growth, and Risk & Cash Flow analysis. Each worker handles 2-3 sections with focused context.

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
    3. Launch 6 parallel worker agents
    4. Collect and assemble worker outputs
    5. Generate final report files
    ↓
6 Parallel Workers (spawned via Agent tool)
    - Worker 1: Context Setup (Sections I-III)
    - Worker 2: Core Performance (Sections IV-V)
    - Worker 3: Business Analysis (Sections VI-VIII)
    - Worker 4: Operational Health (Sections XIV-XV)
    - Worker 5: Profitability & Growth (Sections XII-XIII)
    - Worker 6: Risk & Cash Flow (Sections IX-XI, XVI-XVIII)
```

## Prerequisites

Before starting, ensure you have:

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

### 2. Prepare Financial Data

- **fs_index.json** from finanalysis CLI (parsed annual/quarterly report)
- **Prior year fs_index.json** for YoY comparison (optional but recommended)
- Understanding of the company's business model

If fs_index.json doesn't exist, parse the PDF first:
```bash
finanalysis parse <report.pdf> --company <NAME> -o output/<NAME>/<YEAR>
```

## Coordinator Workflow

### Step 1: Extract and Prepare Data Bundles

Read `scripts/data_extractor.py` to prepare focused data bundles for each worker:

```bash
# Generate all data bundles
python scripts/data_extractor.py output/2024/fs_index.json \
  --prior output/2023/fs_index.json \
  --output workspace/data_bundles.json
```

This creates a JSON file with 6 pre-processed data bundles, one per worker.

### Step 2: Launch Parallel Workers

Spawn 6 worker agents in parallel using the Agent tool. Each worker receives:
- **Focused context**: Only the sections they need to write (~100-300 lines)
- **Data bundle**: Pre-calculated metrics, ratios, and trends
- **Worker instructions**: Clear guidance from `references/worker_N_instructions.md`

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

### Step 3: Collect Worker Outputs

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

### Step 4: Assemble Final Report

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

Write to two files:
- `<TICKER>-<PERIOD>-revised.md` (full 18-section report)
- `<TICKER>-<PERIOD>-summary.md` (executive summary from Section IV)

### Step 5: Quality Check

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

### `scripts/data_extractor.py`
Extracts metrics and prepares data bundles for workers:
- Parses fs_index.json
- Calculates all ratios and metrics
- Computes YoY changes and trends
- Compares against benchmarks
- Outputs structured JSON for workers

### `scripts/financial_calculator.py`
Standalone ratio calculator (can be used independently):
```bash
python scripts/financial_calculator.py output/2024/fs_index.json \
  --prior output/2023/fs_index.json \
  --benchmark \
  --format markdown
```

### `scripts/assemble_report.py`
Assembles worker outputs into final report:
```bash
python scripts/assemble_report.py \
  --worker-1 workspace/worker_1_output.md \
  --worker-2 workspace/worker_2_output.md \
  ... \
  --output report.md
```

## Example Usage

**User says**: "Analyze Chin Hin Group's 2024 financial performance"

**Your process**:
1. Check for fs_index.json at `output/CHINHIN/2024/fs_index.json`
2. Extract data bundles: `python scripts/data_extractor.py ...`
3. Spawn 6 parallel workers with focused instructions
4. Collect worker outputs as they complete
5. Assemble final report in correct section order
6. Write `<TICKER>-<PERIOD>-revised.md` and `-summary.md`
7. Deliver to user

## Benefits of Parallel Architecture

✅ **Context Efficiency**: Each worker sees ~100-300 lines, not the full 670-line skill
✅ **Scalability**: Can add more sections without hitting context limits
✅ **Parallel Execution**: 6 workers run simultaneously
✅ **Focused Expertise**: Each worker specializes in 2-3 related sections
✅ **Consistent Data**: All workers use same pre-calculated metrics

## Troubleshooting

**Problem**: Worker output missing required sections
**Solution**: Verify worker instructions explicitly list section headers

**Problem**: Inconsistent metrics across sections
**Solution**: Ensure all workers use the same data_bundles.json (no recalculation)

**Problem**: Duplicate content between workers
**Solution**: Review worker assignments for overlapping responsibilities

**Problem**: Context still too large for worker
**Solution**: Further split worker instructions or simplify data bundle format

## Summary

This skill uses parallel agents to generate comprehensive financial analysis reports without context overflow. As the coordinator, you:

1. Extract data once using `data_extractor.py`
2. Launch 6 specialized workers in parallel
3. Collect and assemble their outputs
4. Deliver a professional 18-section report

The parallel architecture ensures each worker has focused context, enabling deep analysis without hitting token limits.

Now go create insightful financial reports! 🎯
