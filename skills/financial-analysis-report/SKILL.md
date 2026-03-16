---
name: financial-analysis-report
description: >
  Create professional 18-section financial analysis reports and executive summaries using parallel agents for context efficiency.
  Spawns 8 specialized workers: Context Setup, Core Performance, Business Analysis, Operational Health,
  Profitability & Growth, Risk Analysis (IX-XI), Cash Flow & Forecast (XVI-XVIII), and Executive Summary. Each worker handles 2-3 sections with focused context.

  ALWAYS use this skill when the user wants to: create financial analysis reports, analyze company performance,
  generate investment research, compare financials across years, assess risk profile, write research reports,
  analyze financial statements, or produce professional financial analysis documents. Triggers on:
  "analyze this company", "create financial report", "generate analysis report", "analyze financial performance",
  "write research report", "assess financial health", "compare financial statements", or when user provides
  financial data (PDFs, fs_index.json files) and asks for analysis.
---

# Financial Analysis Report - Parallel Agent Architecture

Generate professional 18-section financial analysis reports using a **coordinator + parallel workers** pattern to avoid context limits.

## Architecture

```
Coordinator Agent (you)
    ↓
    1. Parse PDFs → Extract financial data (automated)
    2. Generate worker-specific data bundles
    3. Launch 8 parallel workers
    4. Assemble worker outputs into final report
    ↓
8 Parallel Workers
    ├─ Worker 1:  Context Setup (Sections I-III)
    ├─ Worker 2:  Core Performance (Sections IV-V)
    ├─ Worker 3:  Business Analysis (Sections VI-VIII)
    ├─ Worker 4:  Operational Health (Sections XIV-XV)
    ├─ Worker 5:  Profitability & Growth (Sections XII-XIII)
    ├─ Worker 6:  Risk Analysis (Sections IX-XI)
    ├─ Worker 6b: Cash Flow & Forecast (Sections XVI-XVIII)
    └─ Worker 7:  Executive Summary (4 sections)
```

---

## Quick Start

### End-to-End Automation (Recommended)

```bash
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:annual_2024.pdf 2023:annual_2023.pdf 2022:annual_2022.pdf \
  --output-dir output/CHINHIN \
  --workspace workspace
```

**This single command**:
1. Parses PDFs with finanalysis CLI (auto-detects installation)
2. Calculates derived metrics
3. Generates data bundles for workers
4. Prepares workspace

**After preparation**, spawn 7 workers (1-6 and 6b) in parallel, assemble report, then spawn Worker 7 for executive summary.

**For detailed examples** (2-year, single-year, manual workflow, skip flags), see [quick_start_examples.md](references/quick_start_examples.md)

---

## Prerequisites

### 1. Install finanalysis CLI

```bash
pip install git+https://github.com/GuoxinShan/finanalysis.git
```

Verify: `finanalysis --version`

### 2. Prepare Financial Data

- **fs_index.json** from finanalysis CLI (parsed PDF)
- **Prior year fs_index.json** for YoY comparison (optional but recommended)
- **Understanding of the company's business model** (for qualitative analysis)

---

## Coordinator Workflow

### Phase 1: Preparation (Automated)

```bash
python scripts/generate_report.py \
  --company <NAME> \
  --pdfs 2024:path/to/2024.pdf 2023:path/to/2023.pdf \
  --output-dir output/<NAME> \
  --workspace workspace
```

**What this does**:
- Multi-year PDF parsing (supports 1-3 years)
- Metrics calculation (profitability, solvency, growth, cash flow)
- Data bundle generation with multi-year trends
- Worker workspace preparation

**Output**: `workspace/data_bundles.json` (pre-calculated data for all workers)

---

### Phase 2: Launch Workers 1-6b (Parallel)

Workers receive pre-loaded data bundles (90% of needs) + optional file paths for deep-dive access (10% of needs). Each worker only sees its own bundle — this keeps context focused and avoids confusion.

**Launch all 7 workers in a single turn**:
```python
workers = [
    Agent(subagent_type="general-purpose", description=f"Worker {i}", prompt=prompts[i])
    for i in [1, 2, 3, 4, 5, 6, "6b"]
]
```

**Anti-pattern** (❌ DO NOT DO THIS):
```python
# ❌ Workers reading files individually
worker_2 = Agent(prompt="Read workspace/data_bundles.json and write sections.")
# This causes 7 workers to read the same file = 7x slower!
```

**How to build each worker prompt**:
1. Read the worker's instruction file (e.g., `references/worker_2_core_performance.md`)
2. Read the worker's pre-extracted bundle (e.g., `workspace/bundles/worker_2_bundle.json`)
3. Combine: `f"{instructions}\n\n**Your Data Bundle**:\n```json\n{bundle_json}\n```"`

**Important**: Each worker has a "Canonical Data Ownership" section that tells it which metrics to own vs. cross-reference. The coordinator does NOT need to enforce this — the worker instructions handle it.

See [manual_workflow.md](references/manual_workflow.md) for a complete step-by-step example.

---

### Phase 3: Assemble Report

After all workers complete, assemble the final report:

```bash
python scripts/assemble_report.py \
  --workspace workspace \
  --output CHINHIN-2024-revised.md \
  --company CHINHIN \
  --period FY2024
```

This combines worker outputs in correct section order: I-III, IV-V, VI-VIII, IX-XI, XII-XIII, XIV-XV, XVI-XVIII

**Output**: `<TICKER>-<PERIOD>-revised.md` (full 18-section report)

---

### Phase 4: Generate Executive Summary (Worker 7)

Spawn Worker 7 with the pre-extracted data bundle (same source Workers 1-6b used). Worker 7 synthesizes the full report into a 4-section executive summary — it reads the assembled report for qualitative context but uses raw bundle values for all calculations to avoid rounding errors.

```python
worker_7_instructions = Read("references/worker_7_summary.md")
worker_7_bundle = Read("workspace/bundles/worker_7_bundle.json")  # or relevant workers' bundles

worker_7 = Agent(
    subagent_type="general-purpose",
    description="Executive summary generation",
    prompt=f"""
{worker_7_instructions}

**Company**: CHINHIN
**Period**: FY2024
**Assembled Report**: CHINHIN-2024-revised.md

**Your Data Bundle** (use for all calculations — do NOT derive values from the report's rounded numbers):
```json
{worker_7_bundle}
```

Write to: CHINHIN-summary.md
    """,
    model="sonnet"
)
```

**Output**: `<TICKER>-<PERIOD>-summary.md` (4-section executive summary)

---

## Output Format

### Full Report Structure (18 Sections)

```
Ⅰ. Company Profile
Ⅱ. Analysis Purpose
Ⅲ. Data Description
Ⅳ. Core Conclusions - [Descriptive Title]
Ⅴ. Core Financial Performance - [Descriptive Title]
Ⅵ. Analysis of Changes in Core Business - [Descriptive Title]
Ⅶ. Industry Change Analysis - [Descriptive Title]
Ⅷ. Strategic Initiatives Analysis - [Descriptive Title]
Ⅸ. Risk Scan - [Descriptive Title] (Enhanced with Risk Matrix)
Ⅹ. Analysis of Major Items in the Three Statements
Ⅺ. Expense Analysis
Ⅻ. Profitability Analysis
ⅩⅢ. Growth Capability Analysis
ⅩⅣ. Solvency Analysis
ⅩⅤ. Operating Capability Analysis
ⅩⅥ. Cash Flow Analysis
ⅩⅦ. Asset Quality Analysis
ⅩⅧ. Future Forecast
```

**Section format**: Tables + insights + conclusion

**Example**:
```markdown
# Ⅳ. Core Conclusions - Scale Expansion with Margin Pressure

**Table 1: Key Performance Indicators**
| Metric | FY2024 | FY2023 | YoY | Comment |
|---|---:|---:|---:|---|
| Revenue | 3,252,347 | 2,057,210 | +58.1% | Construction recovery |

**Insights**
1. [First insight with evidence]
2. [Second insight connecting data points]

**Conclusion**: [Summary paragraph]
```

**For complete format specification**, see [output_format_specification.md](references/output_format_specification.md)

### Executive Summary (4 Sections)

```
1. Key Conclusions - From Section IV
2. Data Parsing - Core metrics and profitability
3. Trend Analysis - Revenue, margin, solvency trajectories
4. Risk Warning - Top risks from Section IX
```

**Length**: 2-3 pages

---

## Worker Assignments

| Worker | Sections | Topics | Instruction File |
|--------|----------|--------|------------------|
| 1 | I-III | Company Profile, Purpose, Data Description | worker_1_context_setup.md |
| 2 | IV-V | Core Conclusions, Core Performance | worker_2_core_performance.md |
| 3 | VI-VIII | Segment Analysis, Industry, Strategy | worker_3_business_analysis.md |
| 4 | XIV-XV | Solvency, Operational Capability | worker_4_operational_health.md |
| 5 | XII-XIII | Profitability, Growth Capability | worker_5_profitability_growth.md |
| 6 | IX-XI | Risk Scan, Major Items, Expense Analysis | worker_6_risk_cashflow.md |
| 6b | XVI-XVIII | Cash Flow, Asset Quality, Future Forecast | worker_6b_cashflow_forecast.md |
| 7 | Summary | Executive Summary (4 sections) | worker_7_summary.md |

**Important**: Workers only see their assigned instruction file, keeping context focused.

---

## Quality Standards

Each worker must follow these principles:

1. **Explain WHY, not just WHAT** - Numbers tell a story; interpret it
2. **Be specific, not generic** - Use actual data from the bundle
3. **Connect the dots** - Link insights within your sections
4. **Be forward-looking** - Assess implications and risks
5. **Write for the user** - Professional but accessible
6. **Calculate precisely** - Never derive from rounded values
7. **Respect data ownership** - Do NOT restate metrics owned by other sections (see [canonical_data_registry.md](references/canonical_data_registry.md))

### Anti-Redundancy Rules

Each key metric has exactly one "owner" section. Other sections must cross-reference, not restate:

| Metric | Owner | Do NOT repeat in |
|--------|-------|-----------------|
| Revenue, growth % | V | IV, VI, XII, XIII, XIV, XVI |
| Gross margin | V | IV, X, XI, XII |
| PBT, PAT, PATMI | V | IV, XII, XIII |
| Admin expenses, finance costs | XI | IV, V, VI, IX, XIV, XVI |
| D/E, gearing, current ratio | XIV | IV, IX, XVII |
| Bank borrowings | XIV | IX, X, XVI, XVII |
| OCF, FCF | XVI | IV, IX, XV |
| Segment revenue/PBT | VI | V |
| NCI % of PAT, ROE | XII | V, XVII |

See [canonical_data_registry.md](references/canonical_data_registry.md) for the full table.

### Line Budget

Each section should produce output within these targets (excluding blank lines and table separators):

| Section | Content | Target Lines |
|---------|---------|-------------|
| I-III | Company Profile, Purpose, Data | ~15 |
| IV | Core Conclusions (3 bullets) | ~12 |
| V | Core Performance (2 tables + 2 paragraphs) | ~45 |
| VI | Business Analysis (2 segment tables + 1 paragraph) | ~35 |
| VII | Industry Change (1 table + 2-3 sentences) | ~20 |
| VIII | Strategic Initiatives (1 table + 1 paragraph) | ~25 |
| IX | Risk Scan (1 matrix + 2 paragraphs) | ~50 |
| X | Major Items (3 tables + 1 paragraph) | ~40 |
| XI | Expense Analysis (1 table + 2 paragraphs) | ~30 |
| XII | Profitability (2 tables + 2 paragraphs) | ~30 |
| XIII | Growth (2 tables + 2 paragraphs) | ~30 |
| XIV | Solvency (2 tables + 2 paragraphs) | ~40 |
| XV | Operating Capability (2 tables + 1 paragraph) | ~30 |
| XVI | Cash Flow (2 tables + 2 paragraphs) | ~35 |
| XVII | Asset Quality (1 table + 1 paragraph) | ~25 |
| XVIII | Future Forecast (1 table + 2 paragraphs) | ~45 |
| **Total** | | **~507** |

With table formatting, markdown headers, and spacing, the full report should land at **700-900 lines**. If a section exceeds its target significantly, trim redundant analysis or tables.

### Precision Standards

**CRITICAL**: Calculate from source data BEFORE rounding. Never use rounded values as calculation inputs.

**The Rounding Error Pattern**:
```
❌ WRONG: Round → Calculate
   PAT: 215.5m, PATMI: 114.8m
   NCI = 215.5 - 114.8 = 100.7m  ← ERROR (actual: 97.1m)

✅ CORRECT: Calculate → Round
   NCI = 215,492 - 114,818 = 97,078
   Display: 97.1m (97,078 / 1000)
```

See [writing_standards.md](references/writing_standards.md) for detailed examples.

---

## Quality Check

Before delivering, verify the **COMPLETE 18-SECTION REPORT**:

- [ ] **All 18 sections present** in correct Roman numeral order (Ⅰ-ⅩⅤⅢ)
- [ ] **CRITICAL**: Sections IX, X, XI exist (Risk Scan, Major Items, Expense Analysis) - **most frequently missed**
- [ ] **Section order**: Ⅰ→Ⅱ→Ⅲ→Ⅳ→Ⅴ→Ⅵ→Ⅶ→Ⅷ→Ⅸ→Ⅹ→Ⅺ→Ⅻ→ⅩⅢ→ⅩⅣ→ⅩⅤ→ⅩⅥ→ⅩⅦ→ⅩⅧ
- [ ] **No redundancy**: Key metrics appear only in their owner section (check [canonical_data_registry.md](references/canonical_data_registry.md))
- [ ] **No macro filler**: Section VII has no GDP/OPR/industry statistics, Section VIII has no digital/ESG bullet lists
- [ ] **No balance sheet re-presentation**: Section XVII focuses on asset quality, not full balance sheet
- [ ] **Report length**: Total should be 700-900 lines (if significantly over, check for repeated data points)
- [ ] Tables formatted correctly
- [ ] Consistent metrics across sections
- [ ] **Section IX**: Risk matrix with severity ratings (Critical/High/Medium/Low)

---

## Troubleshooting

### Top 3 Issues

1. **finanalysis CLI not found**
   - Install: `pip install git+https://github.com/GuoxinShan/finanalysis.git`
   - Or use `--skip-pdf-parsing` if fs_index.json exists

2. **Sections IX, X, XI missing**
   - Worker 6 handles sections IX, X, XI
   - Verify Worker 6 output contains all 3 sections

3. **Worker output incomplete**
   - Verify worker instructions list section headers
   - Check data bundle contains required metrics

**For comprehensive troubleshooting**, see [troubleshooting.md](references/troubleshooting.md)

---

## Manual Workflow

For users who need fine-grained control, see [manual_workflow.md](references/manual_workflow.md) for:
- Step-by-step data extraction
- Manual worker spawning
- Custom data bundle preparation
- Detailed troubleshooting for manual workflow

---

## Data Formats

**For complete data format specification**, see [data_format.md](references/data_format.md)

**Quick Reference**:
- **fs_index.json**: Structured financial data (236 line items, 100% accurate)
- **metrics.json**: Pre-calculated ratios (profitability, solvency, growth, cash flow)
- **text_blocks.jsonl**: Extracted text (optional, for qualitative analysis)
- **data_bundles.json**: Pre-calculated data for all workers (~2000-3000 lines)
- **worker_N_bundle.json**: Individual worker bundles (~200-500 lines each)

---

## Benefits of Parallel Architecture

✅ **Context Efficiency**: Each worker sees ~100-300 lines, not the full skill
✅ **Scalability**: Can add more sections without hitting context limits
✅ **Parallel Execution**: 8 workers run efficiently
✅ **Focused Expertise**: Each worker specializes in specific sections
✅ **Consistent Data**: All workers use same pre-calculated metrics
✅ **Enhanced Risk Analysis**: Severity-rated risk matrix with mitigation timelines

---

## Summary

This skill uses parallel agents to generate comprehensive financial analysis reports without context overflow. As the coordinator, you:

1. **Prepare data** using `generate_report.py` (or manual extraction)
2. **Launch 7 workers** (1-6 and 6b) in parallel with pre-loaded data
3. **Collect outputs** and assemble with `assemble_report.py`
4. **Generate summary** (Worker 7)
5. **Deliver** a professional 18-section report + executive summary

**Next Steps**:
- See [quick_start_examples.md](references/quick_start_examples.md) for usage examples
- See [output_format_specification.md](references/output_format_specification.md) for report structure
- See [troubleshooting.md](references/troubleshooting.md) if issues arise

Now go create insightful financial reports! 🎯
