# Quick Start Examples

Detailed examples for different use cases of the financial-analysis-report skill.

## Multi-Year Analysis (3 Years - Recommended)

**Best for**: Comprehensive trend analysis with statistical significance

```bash
# Using actual file paths from your filesystem
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:testdata/CHINHIN_Annual_Report_2024.pdf 2023:testdata/CHINHIN_Annual_Report_2023.pdf 2022:testdata/CHINHIN_Annual_Report_2022.pdf \
  --output-dir output/CHINHIN \
  --workspace workspace
```

**Or with relative paths**:
```bash
# From the finanalysis project root
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:../testdata/CHINHIN_Annual_Report_2024.pdf \
  --output-dir output/CHINHIN
```

**Benefits of 3-Year Analysis**:
- ✅ **Trend identification**: 3-year patterns are more reliable than 2-year
- ✅ **CAGR calculations**: Compound growth rates with statistical significance
- ✅ **Cyclical analysis**: Identify if current year is peak/trough/normal
- ✅ **Better forecasts**: 3 data points improve projection confidence
- ✅ **Professional standards**: Most equity research includes 3-5 year histories

**What happens**:
1. Script parses all 3 PDFs with finanalysis CLI
2. Calculates derived metrics for each year
3. Generates 3-year trend data with CAGRs
4. Prepares enhanced data bundles for workers with historical context
5. Workers can identify patterns: accelerating/decelerating growth, cyclical trends

---

## 2-Year Analysis (Minimum for YoY)

**Best for**: Basic year-over-year comparison

```bash
# Example with actual file paths
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:testdata/CHINHIN_Annual_Report_2024.pdf 2023:testdata/CHINHIN_Annual_Report_2023.pdf \
  --output-dir output/CHINHIN \
  --workspace workspace
```

**What you get**:
- YoY change calculations
- Basic trend analysis
- 2-year comparison tables

**Limitations**:
- No CAGR calculations (need 3+ years)
- Limited pattern recognition
- Less reliable trend identification

---

## Single Year Analysis (No Trends)

**Best for**: First-time analysis or when prior year data unavailable

```bash
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:testdata/CHINHIN_Annual_Report_2024.pdf \
  --output-dir output/CHINHIN \
  --workspace workspace
```

**What you get**:
- Complete 9-section analysis for single year
- No YoY comparisons
- No trend analysis
- Still comprehensive operational analysis

**Limitations**:
- Cannot assess whether performance improved or declined
- No growth trajectory context
- Limited strategic insights

---

## After Preparation Completes

Once the script finishes, you'll have:
- `output/CHINHIN/2024/fs_index.json` - Current year data
- `output/CHINHIN/2023/fs_index.json` - Prior year data (if provided)
- `output/CHINHIN/2022/fs_index.json` - Prior-prior year data (if provided)
- `output/CHINHIN/2024/metrics.json` - Calculated financial ratios
- `workspace/data_bundles.json` - Pre-calculated data for workers
- `workspace/bundles/worker_N_bundle.json` - Individual worker bundles (optional)

**Next steps**:
1. Spawn 6 parallel workers (Workers 1-6) for report sections
2. Collect worker outputs
3. Run `assemble_report.py` to combine into final report
4. Spawn Worker 7 to generate executive summary

---

## Manual Workflow (For Control)

If you already have `fs_index.json` files and want step-by-step control:

```bash
# Step 1: Extract data bundles
python scripts/data_extractor.py output/2024/fs_index.json \
  --company CHINHIN \
  --prior output/2023/fs_index.json \
  --prior output/2022/fs_index.json \
  --text-blocks output/2024/text_blocks.jsonl \
  --output workspace/data_bundles.json

# Step 2: (Optional) Extract individual worker bundles
python scripts/extract_worker_bundle.py \
  --all \
  --input workspace/data_bundles.json \
  --output-dir workspace/bundles

# Step 3: Spawn workers (6 parallel agents)
# ... (see SKILL.md for worker spawning instructions)

# Step 4: Assemble report
python scripts/assemble_report.py \
  --workspace workspace \
  --output CHINHIN-2024-revised.md \
  --company CHINHIN \
  --period FY2024

# Step 5: Generate executive summary (Worker 7)
# ... (spawn Worker 7 to read full report and generate summary)
```

**Benefits of manual workflow**:
- Full control over each step
- Can inspect intermediate outputs
- Can rerun individual steps without redoing everything
- Useful for debugging

**Trade-offs**:
- More commands to run
- Need to track progress manually
- Easier to make mistakes

---

## Using Skip Flags for Incremental Runs

If you've already run the script and want to skip certain steps:

```bash
# Skip PDF parsing (if fs_index.json already exists)
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:report.pdf \
  --skip-pdf-parsing \
  --output-dir output/CHINHIN

# Skip metrics calculation (if metrics.json already exists)
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:report.pdf \
  --skip-metrics \
  --output-dir output/CHINHIN

# Skip data bundle generation (if data_bundles.json already exists)
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:report.pdf \
  --skip-bundles \
  --output-dir output/CHINHIN

# Combine flags as needed
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:report.pdf \
  --skip-pdf-parsing \
  --skip-metrics \
  --output-dir output/CHINHIN
```

---

## Common Scenarios

### Scenario 1: First-time setup
```bash
# Install finanalysis CLI
pip install git+https://github.com/GuoxinShan/finanalysis.git

# Verify installation
finanalysis --version

# Run end-to-end
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:annual_2024.pdf 2023:annual_2023.pdf 2022:annual_2022.pdf \
  --output-dir output/CHINHIN \
  --workspace workspace
```

### Scenario 2: Update existing report with new data
```bash
# Add a new year to existing analysis
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2025:annual_2025.pdf 2024:annual_2024.pdf 2023:annual_2023.pdf \
  --output-dir output/CHINHIN \
  --workspace workspace
```

### Scenario 3: Quick single-company analysis
```bash
# Minimal command for quick analysis
python scripts/generate_report.py \
  --pdfs 2024:report.pdf \
  --company MYCOMPANY \
  --workspace workspace
```

### Scenario 4: Debug mode
```bash
# Run with verbose output to debug issues
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:report.pdf \
  --output-dir output/CHINHIN \
  --workspace workspace \
  --verbose 2>&1 | tee debug.log
```
