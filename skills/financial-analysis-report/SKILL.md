---
name: financial-analysis-report
description: >
  Create professional 9-section financial analysis reports and executive summaries using parallel agents for context efficiency.
  Spawns 6 specialized workers: Context Setup, Core Performance, Business Analysis, Profitability & Health,
  Risk Assessment, and Cash Flow & Outlook. Each worker handles 1-2 focused sections with deeper analysis.

  ALWAYS use this skill when the user wants to: create financial analysis reports, analyze company performance,
  generate investment research, compare financials across years, assess risk profile, write research reports,
  analyze financial statements, or produce professional financial analysis documents. Triggers on:
  "analyze this company", "create financial report", "generate analysis report", "analyze financial performance",
  "write research report", "assess financial health", "compare financial statements", or when user provides
  financial data (PDFs, fs_index.json files) and asks for analysis.
---

# Financial Analysis Report - Parallel Agent Architecture

Generate professional 9-section financial analysis reports using a **coordinator + parallel workers** pattern. Each section goes deeper with fewer, more focused chapters.

## Architecture

```
Coordinator Agent (you)
    ↓
    1. Parse PDFs → Extract financial data (automated)
    2. Generate worker-specific data bundles
    3. Launch 6 parallel workers
    4. Assemble worker outputs into final report
    ↓
6 Parallel Workers
    ├─ Worker 1:  Company Overview (Section I)
    ├─ Worker 2:  Core Performance (Sections II-III)
    ├─ Worker 3:  Business & Strategy (Section IV)
    ├─ Worker 4:  Profitability & Health (Sections V, VII)
    ├─ Worker 5:  Risk Assessment (Section VI)
    └─ Worker 6:  Cash Flow & Outlook (Sections VIII-IX)
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

**After preparation**, spawn 6 workers in parallel, assemble report, then spawn Worker 7 for executive summary.

**For detailed examples**, see [quick_start_examples.md](references/quick_start_examples.md)

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

**Output**: `workspace/data_bundles.json` (pre-calculated data for all workers)

---

### Phase 2: Launch Workers 1-6 (Parallel)

Workers receive pre-loaded data bundles + optional file paths for deep-dive access. Each worker only sees its own bundle.

**Launch all 6 workers in a single turn**:
```python
for worker_id in [1, 2, 3, 4, 5, 6]:
    bundle = Read(f"workspace/bundles/worker_{worker_id}_bundle.json")
    instructions = Read(f"references/worker_{worker_id}_*.md")

    Agent(
        subagent_type="general-purpose",
        description=f"Worker {worker_id}",
        prompt=f"""
{instructions}

**Your Pre-Loaded Data Bundle**:
```json
{bundle}
```

Write your sections using the data above.
Output: workspace/worker_{worker_id}_sections.md
    """,
        model="sonnet"
    )
```

See [manual_workflow.md](references/manual_workflow.md) for a complete step-by-step example.

---

### Phase 3: Assemble Report

```bash
python scripts/assemble_report.py \
  --workspace workspace \
  --output CHINHIN-2024-revised.md \
  --company CHINHIN \
  --period FY2024
```

---

### Phase 4: Generate Executive Summary (Worker 7)

```python
worker_7_instructions = Read("references/worker_7_summary.md")
worker_7_bundle = Read("workspace/bundles/worker_7_bundle.json")

worker_7 = Agent(
    subagent_type="general-purpose",
    description="Executive summary generation",
    prompt=f"""
{worker_7_instructions}

**Company**: CHINHIN
**Period**: FY2024
**Assembled Report**: CHINHIN-2024-revised.md

**Your Data Bundle** (use for all calculations):
```json
{worker_7_bundle}
```

Write to: CHINHIN-summary.md
    """,
    model="sonnet"
)
```

---

## Output Format

### Full Report Structure (9 Sections)

```
Ⅰ. Company Overview
Ⅱ. Core Conclusions - [Descriptive Title]
Ⅲ. Financial Performance - [Descriptive Title]
Ⅳ. Business & Strategy - [Descriptive Title]
Ⅴ. Profitability & Growth - [Descriptive Title]
Ⅵ. Risk Assessment - [Descriptive Title]
Ⅶ. Financial Health - [Descriptive Title]
Ⅷ. Cash Flow & Capital Allocation - [Descriptive Title]
Ⅸ. Outlook - [Descriptive Title]
```

**Section format**: Tables + deep analysis + conclusion

**Example**:
```markdown
# Ⅲ. Financial Performance - Revenue Surge with Margin Compression

**Table 1: Income Statement Performance**
| Metric | FY2024 | FY2023 | YoY | Comment |
|---|---:|---:|---:|---|
| Revenue | 3,252,347 | 2,057,210 | +58.1% | Construction recovery |

**Table 2: Margin Waterfall**
| Margin | FY2024 | FY2023 | Change | Driver |
|---|---:|---:|---:|---|
| Gross Margin | 16.15% | 9.16% | +6.99pp | Vertical integration |

**Analysis**
1. [Deep insight connecting revenue drivers to margin impact]
2. [Cost structure evolution and operating leverage assessment]
3. [Earnings quality: one-time items, NCI dilution impact]

**Conclusion**: [Synthesis paragraph]
```

**For complete format specification**, see [output_format_specification.md](references/output_format_specification.md)

### Executive Summary (4 Sections)

```
1. Key Conclusions - From Section II
2. Data Parsing - Core metrics and profitability
3. Trend Analysis - Revenue, margin, solvency trajectories
4. Risk Warning - Top risks from Section VI
```

**Length**: 2-3 pages

---

## Worker Assignments

| Worker | Sections | Topics | Instruction File |
|--------|----------|--------|------------------|
| 1 | I | Company Overview | worker_1_context_setup.md |
| 2 | II-III | Core Conclusions, Financial Performance, Expenses | worker_2_core_performance.md |
| 3 | IV | Business Segments, Industry, Strategy | worker_3_business_analysis.md |
| 4 | V, VII | Profitability & Growth, Financial Health | worker_4_profitability_health.md |
| 5 | VI | Risk Assessment (matrix + analysis) | worker_5_risk.md |
| 6 | VIII-IX | Cash Flow, Asset Quality, Outlook | worker_6_cashflow_outlook.md |
| 7 | Summary | Executive Summary (4 sections) | worker_7_summary.md |

---

## Quality Standards

Each worker must follow these principles:

1. **Explain WHY, not just WHAT** - Numbers tell a story; interpret it
2. **Go deep, not wide** - Fewer metrics, more analysis per metric
3. **Connect the dots** - Link insights across your sections
4. **Be forward-looking** - Assess implications and risks
5. **Calculate precisely** - Never derive from rounded values
6. **Respect data ownership** - Do NOT restate metrics owned by other sections (see [canonical_data_registry.md](references/canonical_data_registry.md))

### Anti-Redundancy Rules

| Metric | Owner | Do NOT repeat in |
|--------|-------|-----------------|
| Revenue, growth % | III | II, IV, V, VII, VIII |
| Gross margin | III | II, V, VII |
| PBT, PAT, PATMI | III | II, V, VII |
| Expense breakdown | III | II, IV |
| Segment revenue/PBT | IV | III |
| ROE, ROA, DuPont | V | III, VII |
| Growth breadth (profit vs EPS) | V | III |
| D/E, gearing, current ratio | VII | II, VI, VIII |
| Working capital metrics | VII | V, VIII |
| Risk matrix | VI | Standalone |
| OCF, FCF | VIII | II, V, VII |

See [canonical_data_registry.md](references/canonical_data_registry.md) for the full table.

### Line Budget

| Section | Content | Target Lines |
|---------|---------|-------------|
| I | Company Overview | ~30 |
| II | Core Conclusions (3-5 bullets) | ~15 |
| III | Financial Performance (3 tables + 3-4 paragraphs) | ~80 |
| IV | Business & Strategy (3 tables + 3 paragraphs) | ~80 |
| V | Profitability & Growth (2 tables + 3 paragraphs) | ~60 |
| VI | Risk Assessment (1 matrix + 2 paragraphs) | ~50 |
| VII | Financial Health (2 tables + 3 paragraphs) | ~70 |
| VIII | Cash Flow & Capital (2 tables + 3 paragraphs) | ~60 |
| IX | Outlook (1 table + 2 paragraphs) | ~45 |
| **Total** | | **~490** |

With table formatting and spacing, the full report should land at **600-800 lines**.

### Precision Standards

**CRITICAL**: Calculate from source data BEFORE rounding. Never use rounded values as calculation inputs.

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

Before delivering, verify the **COMPLETE 9-SECTION REPORT**:

- [ ] **All 9 sections present** in correct Roman numeral order (Ⅰ-Ⅸ)
- [ ] **No redundancy**: Key metrics appear only in their owner section
- [ ] **No macro filler**: Section IV has no GDP/OPR/industry statistics
- [ ] **Report length**: Total should be 600-800 lines
- [ ] Tables formatted correctly
- [ ] Consistent metrics across sections
- [ ] **Section VI**: Risk matrix with severity ratings

---

## Troubleshooting

### Top 3 Issues

1. **finanalysis CLI not found**
   - Install: `pip install git+https://github.com/GuoxinShan/finanalysis.git`
   - Or use `--skip-pdf-parsing` if fs_index.json exists

2. **Section VI missing**
   - Worker 5 handles risk assessment
   - Verify Worker 5 output contains the risk matrix

3. **Worker output incomplete**
   - Verify worker instructions list section headers
   - Check data bundle contains required metrics

**For comprehensive troubleshooting**, see [troubleshooting.md](references/troubleshooting.md)

---

## Manual Workflow

For users who need fine-grained control, see [manual_workflow.md](references/manual_workflow.md).

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

## Summary

This skill uses parallel agents to generate focused financial analysis reports. As the coordinator, you:

1. **Prepare data** using `generate_report.py` (or manual extraction)
2. **Launch 6 workers** in parallel with pre-loaded data
3. **Collect outputs** and assemble with `assemble_report.py`
4. **Generate summary** (Worker 7)
5. **Deliver** a professional 9-section report + executive summary

**Next Steps**:
- See [quick_start_examples.md](references/quick_start_examples.md) for usage examples
- See [output_format_specification.md](references/output_format_specification.md) for report structure
- See [troubleshooting.md](references/troubleshooting.md) if issues arise
