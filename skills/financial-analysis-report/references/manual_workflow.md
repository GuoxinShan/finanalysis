# Manual Workflow Guide

Step-by-step instructions for users who need fine-grained control over the report generation process.

---

## Overview

This guide covers the manual workflow for generating financial analysis reports. Use this approach when you:
- Already have `fs_index.json` files and don't need PDF parsing
- Want full control over each step
- Need to inspect intermediate outputs
- Are debugging issues with the automated workflow

**For most users**: The automated workflow via `generate_report.py` is recommended. See `quick_start_examples.md` for details.

---

## Prerequisites

Before starting, ensure you have:
1. **fs_index.json** - Parsed financial data from finanalysis CLI
2. **Prior year fs_index.json** - For YoY comparison (optional but recommended)
3. **text_blocks.jsonl** - Extracted text from PDF (optional, for qualitative analysis)
4. **finanalysis CLI installed** - `pip install git+https://github.com/GuoxinShan/finanalysis.git`

---

## Step 1: Extract and Prepare Data Bundles

### Multi-Year Setup (3 years - Recommended)

```bash
python scripts/data_extractor.py output/2024/fs_index.json \
  --company CHINHIN \
  --prior output/2023/fs_index.json \
  --prior output/2022/fs_index.json \
  --text-blocks output/2024/text_blocks.jsonl \
  --output workspace/data_bundles.json
```

### 2-Year Setup (Minimum for YoY)

```bash
python scripts/data_extractor.py output/2024/fs_index.json \
  --company CHINHIN \
  --prior output/2023/fs_index.json \
  --text-blocks output/2024/text_blocks.jsonl \
  --output workspace/data_bundles.json
```

### Single Year (No Trends)

```bash
python scripts/data_extractor.py output/2024/fs_index.json \
  --company CHINHIN \
  --text-blocks output/2024/text_blocks.jsonl \
  --output workspace/data_bundles.json
```

### What This Does

**Hybrid Extraction (v3.0)**:
- **Structured data**: Extracts 100% accurate financial metrics from fs_index.json
- **Qualitative data**: Provides search access to text_blocks.jsonl
- **Page hints**: Identifies likely pages for MD&A, segments, strategy sections
- **No fragile regex**: Workers use LLM intelligence to extract industry, segments, geography
- **Multi-year trends**: Automatically generates 3-year comparisons and CAGRs

**Real Data Extraction**: Extracts actual values from fs_index.json line_items:
- Revenue, gross profit, PBT, PAT, attributable profit
- Operating margins, PBT margins, PAT margins
- Balance sheet items: assets, liabilities, equity
- Current ratio, quick ratio, working capital

---

## Step 1.5: (Optional) Extract Individual Worker Bundles

**Why do this?** Instead of passing the entire data_bundles.json to workers, extract worker-specific bundles for better efficiency.

### Extract All Worker Bundles

```bash
python scripts/extract_worker_bundle.py \
  --all \
  --input workspace/data_bundles.json \
  --output-dir workspace/bundles
```

This creates:
- `workspace/bundles/worker_1_bundle.json`
- `workspace/bundles/worker_2_bundle.json`
- `workspace/bundles/worker_3_bundle.json`
- `workspace/bundles/worker_4_bundle.json`
- `workspace/bundles/worker_5_bundle.json`
- `workspace/bundles/worker_6_bundle.json`

### Extract Single Worker Bundle

```bash
python scripts/extract_worker_bundle.py \
  --worker 2 \
  --input workspace/data_bundles.json \
  --output workspace/bundles/worker_2_bundle.json
```

### List Available Workers

```bash
python scripts/extract_worker_bundle.py --list --input workspace/data_bundles.json
```

**Benefits of Individual Bundles**:
- ✅ Smaller files for workers (200-500 lines vs. 2000+ lines)
- ✅ Each worker only sees their data (less confusion)
- ✅ Faster worker startup
- ✅ Easier debugging (inspect individual bundles)
- ✅ Can regenerate single worker bundle if needed

---

## Step 2: Launch Parallel Workers (Workers 1-6)

**🚫 CRITICAL PATTERN**: Coordinator reads data bundles ONCE and passes data directly in worker prompts. Workers should NOT read files.

### Approach A: Pre-Extract Worker Bundles (RECOMMENDED - Most Efficient)

```python
# 1. Extract all worker bundles to separate files (ONE TIME)
# Run this once after data_extractor.py
import subprocess
subprocess.run([
    "python", "scripts/extract_worker_bundle.py",
    "--all",
    "--input", "workspace/data_bundles.json",
    "--output-dir", "workspace/bundles"
])

# 2. Read individual worker bundles (6 small reads instead of 1 large read)
import json

worker_bundles = {}
for i in range(1, 7):
    bundle_path = f"workspace/bundles/worker_{i}_bundle.json"
    bundle_json = Read(bundle_path)  # Use Read tool
    worker_bundles[i] = json.loads(bundle_json)

# 3. Read worker instruction files
worker_instructions = {}
for i in range(1, 7):
    instruction_file = f"references/worker_{i}_*.md"  # Use appropriate filename
    worker_instructions[i] = Read(instruction_file)

# 4. Pass to workers (workers don't read files)
worker_2 = Agent(
    subagent_type="general-purpose",
    description="Core performance analysis",
    prompt=f"""
{worker_instructions[2]}

**Your Pre-Loaded Data Bundle** (use this - DO NOT read files):
```json
{json.dumps(worker_bundles[2], indent=2)}
```

Write Sections II-III using the data above.
    """,
    model="sonnet"
)
```

**Benefits**:
- ✅ 6 small file reads (200-500 lines each) vs 1 large read (2000+ lines)
- ✅ Workers only see their data (less confusion)
- ✅ Faster worker startup
- ✅ Easier debugging

---

### Approach B: Single Large Bundle (Simpler but Slower)

```python
import json

# 1. Read data bundles file ONCE
data_bundles_json = Read("workspace/data_bundles.json")
data_bundles = json.loads(data_bundles_json)

# 2. Read worker instruction files
worker_2_instructions = Read("references/worker_2_core_performance.md")

# 3. Pass data DIRECTLY in prompt (workers don't read files)
worker_2 = Agent(
    subagent_type="general-purpose",
    description="Core performance analysis",
    prompt=f"""
{worker_2_instructions}

**Your Pre-Loaded Data Bundle** (use this data - DO NOT read files):
```json
{json.dumps(data_bundles['worker_2'], indent=2)}
```

**Multi-Year Trends** (if available):
```json
{json.dumps(data_bundles.get('_multi_year_trends', {}), indent=2)}
```

**Task**: Write Sections II and III using the pre-loaded data above.
Output ONLY the markdown content for these two sections.
    """,
    model="sonnet"  # Use sonnet for quality
)
```

**Benefits**:
- ✅ Simpler code (one file read instead of 6)
- ✅ Good for small data bundles

**Trade-offs**:
- ⚠️ Slower for large bundles (each worker prompt contains 2000+ lines)
- ⚠️ Workers see entire data structure (potential confusion)

---

### ❌ Anti-Pattern: Workers Reading Files (DO NOT DO THIS)

```python
# ❌ INEFFICIENT: Workers reading files individually
worker_2 = Agent(
    prompt="""
Read workspace/data_bundles.json and extract worker_2 data.
Then write sections.
    """
)
# This causes 6 workers to read the same file = 6x slower!
```

**Why this is bad**:
- Each worker reads the same file independently
- 6 workers = 6x redundant file I/O
- Wastes tokens on repeated data
- Slower overall execution

---

### Launch All 6 Workers in Parallel

```python
# Read all instruction files
worker_1_instructions = Read("references/worker_1_context_setup.md")
worker_2_instructions = Read("references/worker_2_core_performance.md")
worker_3_instructions = Read("references/worker_3_business_analysis.md")
worker_4_instructions = Read("references/worker_4_operational_health.md")
worker_5_instructions = Read("references/worker_5_profitability_growth.md")
worker_6_instructions = Read("references/worker_6_risk_cashflow.md")

# Create worker prompts with pre-loaded data
workers = [
    Agent(subagent_type="general-purpose", description="Context setup",
          prompt=f"{worker_1_instructions}\n\n**Your Pre-Loaded Data**:\n```json\n{json.dumps(worker_bundles[1], indent=2)}\n```"),
    Agent(subagent_type="general-purpose", description="Core performance",
          prompt=f"{worker_2_instructions}\n\n**Your Pre-Loaded Data**:\n```json\n{json.dumps(worker_bundles[2], indent=2)}\n```"),
    Agent(subagent_type="general-purpose", description="Business analysis",
          prompt=f"{worker_3_instructions}\n\n**Your Pre-Loaded Data**:\n```json\n{json.dumps(worker_bundles[3], indent=2)}\n```"),
    Agent(subagent_type="general-purpose", description="Operational health",
          prompt=f"{worker_4_instructions}\n\n**Your Pre-Loaded Data**:\n```json\n{json.dumps(worker_bundles[4], indent=2)}\n```"),
    Agent(subagent_type="general-purpose", description="Profitability & growth",
          prompt=f"{worker_5_instructions}\n\n**Your Pre-Loaded Data**:\n```json\n{json.dumps(worker_bundles[5], indent=2)}\n```"),
    Agent(subagent_type="general-purpose", description="Risk & cash flow",
          prompt=f"{worker_6_instructions}\n\n**Your Pre-Loaded Data**:\n```json\n{json.dumps(worker_bundles[6], indent=2)}\n```"),
]

# All workers execute in parallel
```

---

## Step 3: Collect Worker Outputs

Each worker returns markdown content for their assigned sections. Collect all outputs:

```python
# Wait for all workers to complete
outputs = [wait_for_agent(w) for w in workers]

# Organize by section
sections = {
    "I": outputs[0],      # Worker 1
    "II-III": outputs[1],  # Worker 2
    "IV": outputs[2],      # Worker 3
    "VII": outputs[3],     # Worker 4
    "V": outputs[4],       # Worker 5
    "VI, VIII-IX": outputs[5],  # Worker 6
}

# Save individual worker outputs
for i, output in enumerate(outputs, 1):
    with open(f"workspace/worker_{i}_output.md", "w") as f:
        f.write(output)
```

---

## Step 4: Assemble Full Report

Combine worker outputs in correct section order:

### Option A: Manual Assembly

```markdown
# Financial Analysis Report: [Company Name] - [Period]

[Worker 1: Section I]

[Worker 2: Sections II-III]

[Worker 3: Section IV]

[Worker 6: Section VI]

[Worker 5: Section V]

[Worker 4: Section VII]

[Worker 6: Sections VIII-IX]
```

### Option B: Use assemble_report.py Script

```bash
python scripts/assemble_report.py \
  --workspace workspace \
  --output CHINHIN-2024-revised.md \
  --company CHINHIN \
  --period FY2024
```

**What the script does**:
1. Reads worker output files from workspace
2. Combines in proper section order (I, II-III, IV, V, VI, VII, VIII-IX)
3. Adds report header with company name and period
4. Writes final report

**Output**: `<TICKER>-<PERIOD>-revised.md` (full 9-section report)

---

## Step 5: Generate Executive Summary (Worker 7)

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

**What Worker 7 does**:
1. Reads the full 9-section report
2. Extracts key insights from:
   - Section II (Core Conclusions)
   - Section III (Core Performance)
   - Section VI (Risk Assessment)
   - Section V (Profitability & Growth)
   - Section VII (Financial Health)
3. Synthesizes into 4-section executive summary
4. Maintains narrative coherence and identifies most important insights

**Output**: `<TICKER>-<PERIOD>-summary.md` (4-section executive summary)

---

## Step 6: Quality Check

Before delivering, verify the **COMPLETE 9-SECTION REPORT**:

### Checklist

- [ ] **All 9 sections present** in correct Roman numeral order (Ⅰ-Ⅸ)
- [ ] **CRITICAL**: Section VI exists (Risk Assessment) - **most frequently missed**
- [ ] **Section order**: Ⅰ→Ⅱ→Ⅲ→Ⅳ→Ⅴ→Ⅵ→Ⅶ→Ⅷ→Ⅸ
- [ ] Tables formatted correctly with consistent headers
- [ ] No duplicate or missing content between workers
- [ ] Consistent terminology and metrics across all sections
- [ ] All metrics from data bundles appear in relevant sections
- [ ] **Section VI**: Enhanced risk matrix with severity ratings (Critical/High/Medium/Low), probability, impact, priority rankings (1-4), and time-bound mitigation actions

### Common Issues

1. **Section VI missing**: Worker 6 handles 3 sections (VI, VIII, IX). Verify all 3 are present.

2. **Section order wrong**: The correct order is:
   - I (Worker 1)
   - II-III (Worker 2)
   - IV (Worker 3)
   - V (Worker 5)
   - VI (Worker 6)
   - VII (Worker 4)
   - VIII-IX (Worker 6)

3. **Duplicate content**: Workers should not overlap. Each worker has unique section assignments.

4. **Missing metrics**: If a metric from data_bundles.json doesn't appear in the report, check that the worker received the correct data bundle.

---

## Worker Assignments Reference

| Worker | Sections | Instruction File | Output File |
|--------|----------|------------------|-------------|
| Worker 1 | I (Company Overview) | worker_1_context_setup.md | worker_1_output.md |
| Worker 2 | II-III (Core Conclusions, Core Performance) | worker_2_core_performance.md | worker_2_output.md |
| Worker 3 | IV (Business & Strategy) | worker_3_business_analysis.md | worker_3_output.md |
| Worker 4 | VII (Financial Health) | worker_4_operational_health.md | worker_4_output.md |
| Worker 5 | V (Profitability & Growth) | worker_5_profitability_growth.md | worker_5_output.md |
| Worker 6 | VI, VIII-IX (Risk Assessment, Cash Flow, Outlook) | worker_6_risk_cashflow.md | worker_6_output.md |
| Worker 7 | Executive Summary (4 sections) | worker_7_summary.md | worker_7_output.md |

---

## Troubleshooting Manual Workflow

### Problem: `data_extractor.py` fails with "fs_index.json not found"

**Solution**: Ensure you've run finanalysis CLI to parse the PDF:
```bash
finanalysis parse report.pdf --company CHINHIN -o output/CHINHIN/2024
```

### Problem: Worker outputs are incomplete or missing sections

**Solution**:
1. Verify worker instructions explicitly list section headers
2. Check that data bundle contains all required metrics
3. Ensure worker prompt includes output format template
4. Review worker instruction file for completeness

### Problem: Section VI missing from final report

**Solution**:
- Worker 6 generates 3 sections total: VI (Risk Assessment), VIII (Cash Flow), IX (Outlook)
- Verify Worker 6 output file contains all 3 sections before assembly
- Check that assemble_report.py includes Worker 6 output in correct position
- The correct order is: Ⅰ→Ⅱ→Ⅲ→Ⅳ→Ⅴ→Ⅵ→Ⅶ→Ⅷ→Ⅸ

### Problem: Inconsistent metrics across sections

**Solution**:
- Ensure all workers use the same data_bundles.json (no recalculation)
- Verify data_extractor.py extracted real values (check `_verification` metadata)
- Run `finanalysis calculate` once and reuse the metrics.json

### Problem: Duplicate content between workers

**Solution**:
- Review worker assignments for overlapping responsibilities
- Each worker should only see their assigned instruction file
- Workers should output ONLY their assigned sections

---

## Summary

The manual workflow provides maximum control at the cost of more steps:

1. **Extract data bundles**: `data_extractor.py` → `data_bundles.json`
2. **(Optional) Extract individual bundles**: `extract_worker_bundle.py` → `worker_N_bundle.json`
3. **Launch 6 parallel workers**: Pass pre-loaded data in prompts
4. **Collect worker outputs**: Save to `worker_N_output.md`
5. **Assemble report**: `assemble_report.py` → final report
6. **Generate summary**: Worker 7 reads full report → executive summary
7. **Quality check**: Verify all 9 sections present

**For most users**: The automated workflow via `generate_report.py` is faster and less error-prone. Use manual workflow only when you need fine-grained control.
