# Troubleshooting Guide

Common issues and solutions when using the financial-analysis-report skill.

---

## Installation & Setup Issues

### Problem: `generate_report.py` cannot find finanalysis CLI

**Symptoms**: Error message "Could not find finanalysis CLI"

**Root Cause**: The finanalysis package is not installed or not in PATH

**Solutions**:

**Option 1: Install from GitHub (Recommended)**
```bash
pip install git+https://github.com/GuoxinShan/finanalysis.git
```

**Option 2: Activate virtual environment**
```bash
# If finanalysis is in a sibling directory
source ../finanalysis/.venv/bin/activate
```

**Option 3: Skip PDF parsing if fs_index.json exists**
```bash
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:report.pdf \
  --skip-pdf-parsing \
  --output-dir output/CHINHIN
```

**Option 4: Install from PyPI (if published)**
```bash
pip install finanalysis
```

**Verification**:
```bash
finanalysis --version
finanalysis --help
```

---

### Problem: `pip install` fails with dependency errors

**Symptoms**: Installation fails with messages about missing dependencies or version conflicts

**Solution**:
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with --no-deps to isolate
pip install --no-deps git+https://github.com/GuoxinShan/finanalysis.git

# Then install dependencies manually if needed
pip install pandas openpyxl pypdf2
```

---

## Data Extraction Issues

### Problem: `data_extractor.py` fails with "fs_index.json not found"

**Symptoms**: Error when running data extraction

**Root Cause**: PDF hasn't been parsed yet

**Solution**: Run finanalysis CLI first
```bash
# Parse current year
finanalysis parse annual_2024.pdf --company CHINHIN -o output/CHINHIN/2024

# Parse prior year (for YoY comparison)
finanalysis parse annual_2023.pdf --company CHINHIN -o output/CHINHIN/2023

# Then run data extractor
python scripts/data_extractor.py output/CHINHIN/2024/fs_index.json \
  --company CHINHIN \
  --prior output/CHINHIN/2023/fs_index.json \
  --output workspace/data_bundles.json
```

---

### Problem: Data bundles contain zeros or placeholders

**Symptoms**: Worker outputs show "0" values or placeholder text like "[DATA NOT AVAILABLE]"

**Root Cause**: fs_index.json has empty line_items or extraction failed

**Diagnosis**:
```bash
# Check if fs_index.json has data
cat output/CHINHIN/2024/fs_index.json | grep "line_items" -A 5

# Verify extraction quality
cat workspace/data_bundles.json | grep "data_quality"
# Should show: "data_quality": "REAL_DATA_EXTRACTED"
```

**Solutions**:

1. **Verify PDF parsing succeeded**:
```bash
finanalysis parse report.pdf --company CHINHIN -o output/CHINHIN/2024 --verbose
```

2. **Check fs_index.json structure**:
```bash
# Should have non-empty line_items
jq '.line_items | length' output/CHINHIN/2024/fs_index.json
# Should be > 100 for a typical annual report
```

3. **Re-run data extraction with verbose output**:
```bash
python scripts/data_extractor.py output/CHINHIN/2024/fs_index.json \
  --company CHINHIN \
  --output workspace/data_bundles.json \
  --verbose
```

---

### Problem: Multi-year trends not appearing in worker data

**Symptoms**: Workers don't receive `_multi_year_trends` section

**Root Cause**: Only 1 year of data provided, or prior year paths incorrect

**Solution**:
```bash
# Ensure you provide multiple years
python scripts/data_extractor.py output/2024/fs_index.json \
  --company CHINHIN \
  --prior output/2023/fs_index.json \
  --prior output/2022/fs_index.json \
  --text-blocks output/2024/text_blocks.jsonl \
  --output workspace/data_bundles.json

# Verify multi-year trends exist
cat workspace/data_bundles.json | grep "_multi_year_trends" -A 10
```

---

## Worker Execution Issues

### Problem: Worker output missing required sections

**Symptoms**: Worker returns incomplete output, missing assigned sections

**Diagnosis**:
1. Check worker instructions explicitly list section headers
2. Verify data bundle contains required metrics
3. Ensure worker prompt includes output format template

**Solutions**:

1. **Verify worker instruction file**:
```bash
cat references/worker_2_core_performance.md | grep "## Your Task"
# Should clearly state which sections to write
```

2. **Check data bundle has required metrics**:
```python
import json
with open('workspace/bundles/worker_2_bundle.json') as f:
    data = json.load(f)
    print(data.keys())  # Should have 'worker_2' key
    print(data['worker_2'].keys())  # Should have metrics, ratios, etc.
```

3. **Ensure worker prompt is complete**:
```python
# Good prompt includes:
prompt = f"""
{worker_instructions}

**Your Pre-Loaded Data**:
{json.dumps(worker_data, indent=2)}

**Task**: Write Sections II and III.
Output ONLY markdown content.
"""
```

---

### Problem: Section VI missing from final report

**Symptoms**: Risk Assessment section absent

**Root Cause**: Worker 5 handles Section VI (Risk Assessment) - may have incomplete output

**This is the #1 most common issue!**

**Solutions**:

1. **Verify Worker 5 output exists**:
```bash
# Check worker 5 output
grep -E "^# [Ⅵ]" workspace/worker_5_sections.md
# Should show section VI
```

2. **Check worker 5 instruction file**:
```bash
cat references/worker_5_risk.md | grep "## Your Task"
# Should list risk assessment requirements
```

3. **Verify assembly script includes Worker 5 output**:
```bash
python scripts/assemble_report.py \
  --workspace workspace \
  --output report.md \
  --company CHINHIN \
  --period FY2024

# Check assembled report
grep -E "^# [Ⅵ]" report.md
# Should show section VI
```

4. **Correct section order**: Ⅰ→Ⅱ→Ⅲ→Ⅳ→Ⅴ→Ⅵ→Ⅶ→Ⅷ→Ⅸ

---

### Problem: Worker completion times vary widely

**Symptoms**: Some workers finish in 30s, others take 3+ minutes

**Root Cause**: Different analysis complexity

**Expected behavior**:
- Worker 2 (Core Performance): Longest (complex analysis)
- Worker 1 (Context Setup): Shortest (simple extraction)
- Workers 3-6: Moderate time

**Solutions**:
1. Use `sonnet` model for all workers (not `haiku`) for consistent quality
2. If variance is extreme (>5x), check worker instructions for unnecessary complexity
3. Consider splitting Worker 6 into two workers (6A and 6B) if consistently slow

---

### Problem: Inconsistent metrics across sections

**Symptoms**: Different sections show different values for the same metric

**Root Cause**: Workers recalculating metrics instead of using pre-calculated values

**Solutions**:
1. **Ensure all workers use same data_bundles.json** (no recalculation)
2. **Verify extraction metadata**:
```bash
cat workspace/data_bundles.json | grep "_verification"
# Should show: "data_quality": "REAL_DATA_EXTRACTED"
```

3. **Run metrics calculation once**:
```bash
# Calculate metrics once
finanalysis calculate output/CHINHIN/2024/fs_index.json \
  --prior output/CHINHIN/2023/fs_index.json \
  --output output/CHINHIN/2024/metrics.json

# Reuse metrics.json for all workers
```

---

### Problem: Duplicate content between workers

**Symptoms**: Same content appears in multiple sections

**Root Cause**: Overlapping worker responsibilities

**Solutions**:
1. **Review worker assignments**:
   - Worker 1: I
   - Worker 2: II-III
   - Worker 3: IV
   - Worker 4: V, VII
   - Worker 5: VI
   - Worker 6: VIII-IX
   - Worker 7: Executive Summary

2. **Each worker should only see their instruction file**:
```python
# Good: Worker-specific instructions
worker_2 = Agent(prompt=f"{worker_2_instructions}\n\nData: {worker_2_data}")

# Bad: All instructions
worker_2 = Agent(prompt=f"{all_worker_instructions}\n\nData: {worker_2_data}")
```

3. **Workers should output ONLY their assigned sections**

---

### Problem: Context still too large for worker

**Symptoms**: Worker fails with context length error

**Root Cause**: Data bundle or instructions too large

**Solutions**:

1. **Use individual worker bundles** (not full data_bundles.json):
```bash
python scripts/extract_worker_bundle.py \
  --all \
  --input workspace/data_bundles.json \
  --output-dir workspace/bundles
```

2. **Check worker instruction file sizes**:
```bash
wc -l references/worker_*.md
# Worker 6 should be ~200-300 lines
# Other workers should be ~100-200 lines
```

3. **Simplify data bundle format** if still too large:
   - Remove unnecessary metadata
   - Use compact JSON (no pretty-printing)
   - Include only required metrics for each worker

---

## Report Assembly Issues

### Problem: assemble_report.py fails

**Symptoms**: Assembly script errors or produces incomplete report

**Diagnosis**:
```bash
# Check worker output files exist
ls -la workspace/worker_*_sections.md

# Verify all worker files present
```

**Note**: Worker 4 outputs two files: `worker_4_sections_v.md` and `worker_4_sections_vii.md`.

**Solutions**:

1. **Ensure all worker outputs exist**:
```bash
for i in {1..6}; do
  if [ ! -f "workspace/worker_${i}_sections.md" ] && [ $i -ne 4 ]; then
    echo "Missing worker $i output"
  fi
done
# Worker 4 has two files: worker_4_sections_v.md and worker_4_sections_vii.md
if [ ! -f "workspace/worker_4_sections_v.md" ] || [ ! -f "workspace/worker_4_sections_vii.md" ]; then
    echo "Missing Worker 4 output"
fi
```

2. **Run assembly with verbose output**:
```bash
python scripts/assemble_report.py \
  --workspace workspace \
  --output report.md \
  --company CHINHIN \
  --period FY2024 \
  --verbose
```

3. **Manually check section order**:
   - Correct: I, II-III, IV, V, VI, VII, VIII-IX
   - Common mistake: Sections placed in wrong order

---

### Problem: Quality check shows missing sections

**Symptoms**: Final report has < 9 sections

**Solution**: Run comprehensive quality check
```bash
# Check all 9 sections present
grep -E "^# [Ⅰ-Ⅸ]" report.md | wc -l
# Should equal 9

# List which sections exist
grep -E "^# [Ⅰ-Ⅸ]" report.md
```

**Quality checklist**:
- [ ] All 9 sections present (Ⅰ-Ⅸ)
- [ ] **CRITICAL**: Section VI exists (Risk Assessment)
- [ ] Section order correct
- [ ] Tables formatted correctly
- [ ] No duplicate content
- [ ] Consistent metrics across sections
- [ ] Section VI has enhanced risk matrix

---

## Multi-Year Analysis Issues

### Problem: Only 2 years of data available

**Symptoms**: Can't provide 3 years of data

**Solution**: 2-year analysis is acceptable
```bash
# 2-year minimum for YoY
python scripts/generate_report.py \
  --company CHINHIN \
  --pdfs 2024:report.pdf 2023:report.pdf \
  --output-dir output/CHINHIN

# Workers can still do trend analysis
# But no multi-year CAGRs
```

**Trade-offs**:
- ✅ YoY comparison works
- ⚠️ No 3-year trend patterns
- ⚠️ No CAGR calculations
- ⚠️ Limited historical context

**Recommendation**: Download prior year reports when possible for better analysis quality

---

### Problem: Multi-year trend analysis not working

**Symptoms**: Workers don't use multi-year data

**Diagnosis**:
```bash
# Check if multi-year trends exist
cat workspace/data_bundles.json | jq '._multi_year_trends'
# Should show years array and trends object
```

**Solutions**:

1. **Ensure 3+ years provided**:
```bash
python scripts/data_extractor.py output/2024/fs_index.json \
  --prior output/2023/fs_index.json \
  --prior output/2022/fs_index.json \
  --output workspace/data_bundles.json
```

2. **Verify worker prompt includes multi-year data**:
```python
prompt = f"""
{worker_instructions}

**Your Data**:
{json.dumps(worker_data, indent=2)}

**Multi-Year Trends** (if available):
{json.dumps(multi_year_trends, indent=2)}
"""
```

3. **Workers should use 3-year tables**:
```markdown
| Year | Revenue | YoY Growth | CAGR (2yr) |
|------|---------|------------|------------|
| FY2022 | 1.82b | - | - |
| FY2023 | 2.06b | +13.0% | - |
| FY2024 | 3.25b | +58.1% | +33.6% |
```

---

## Performance Issues

### Problem: Workers take too long to complete

**Symptoms**: Workers running for 5+ minutes each

**Solutions**:

1. **Check model selection**:
```python
# Use sonnet for quality
Agent(model="sonnet", ...)  # Good

# Avoid haiku for complex analysis
Agent(model="haiku", ...)  # May be slower due to retries
```

2. **Optimize data bundle size**:
```bash
# Use individual worker bundles
python scripts/extract_worker_bundle.py --all \
  --input workspace/data_bundles.json \
  --output-dir workspace/bundles
```

3. **Simplify worker instructions**:
- Remove redundant examples
- Focus on essential guidance
- Remove unused sections

---

### Problem: Running out of tokens

**Symptoms**: "Context length exceeded" errors

**Solutions**:

1. **Use individual worker bundles** (see above)
2. **Split Worker 4 into two workers** if consistently slow:
   - Worker 4A: V (Profitability & Growth)
   - Worker 4B: VII (Financial Health)
3. **Compress JSON formatting**:
```python
# Instead of:
json.dumps(data, indent=2)  # ~5000 tokens

# Use:
json.dumps(data, separators=(',', ':'))  # ~3000 tokens
```

---

## Manual Workflow Issues

### Problem: Manual assembly required - no automation

**Symptoms**: Have to combine worker outputs manually

**Solution**: Use `assemble_report.py`:
```bash
python scripts/assemble_report.py \
  --workspace workspace \
  --output report.md \
  --company CHINHIN \
  --period FY2024
```

This automatically:
- Reads worker output files
- Combines in correct section order
- Adds report header
- Writes final report

---

### Problem: Workers reading files instead of using pre-loaded data

**Symptoms**: Workers attempt to read fs_index.json or data_bundles.json

**Root Cause**: Worker prompt doesn't emphasize pre-loaded data

**Solution**: Strengthen prompt instructions:
```python
prompt = f"""
{worker_instructions}

**🚫 CRITICAL: DO NOT READ FILES 🚫**

Your data is PRE-LOADED below. You have:
```json
{json.dumps(worker_data, indent=2)}
```

DO NOT:
- ❌ Read fs_index.json
- ❌ Read data_bundles.json
- ❌ Use the Read tool

USE THE DATA PROVIDED ABOVE.
"""
```

---

## Getting Help

If issues persist:

1. **Check log files**:
   - `workspace/generate_report.log`
   - Worker output files for errors

2. **Run with verbose output**:
```bash
python scripts/generate_report.py --verbose ... 2>&1 | tee debug.log
```

3. **Validate inputs**:
```bash
# Check fs_index.json structure
jq '.line_items | keys | length' output/2024/fs_index.json

# Check metrics.json
jq '.metrics | keys' output/2024/metrics.json

# Check data bundles
jq '.worker_2 | keys' workspace/data_bundles.json
```

4. **Review worker instruction files** for completeness

5. **Check for updates**:
```bash
pip install --upgrade git+https://github.com/GuoxinShan/finanalysis.git
```

---

## Quick Reference: Most Common Issues

| Issue | Frequency | Solution |
|-------|-----------|----------|
| Section VI missing | #1 | Verify Worker 5 output has risk matrix |
| finanalysis CLI not found | #2 | Install: `pip install git+...` |
| Data bundles contain zeros | #3 | Check fs_index.json has real data |
| Inconsistent metrics | #4 | Use same data_bundles.json for all workers |
| Worker output incomplete | #5 | Verify instructions list all sections |
| Multi-year trends missing | #6 | Provide 3+ years with `--prior` flags |
