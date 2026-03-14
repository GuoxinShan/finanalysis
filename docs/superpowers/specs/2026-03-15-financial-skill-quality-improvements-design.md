# Financial Analysis Report Skill - Quality Improvement Design

**Date**: 2026-03-15
**Author**: Claude (with user collaboration)
**Status**: Draft for review
**Approach**: Multi-Layer Quality System (Comprehensive)

---

## Problem Statement

The current `financial-analysis-report` skill generates professional reports but has quality issues:

1. **Tone Problems**:
   - Overly aggressive language ("explosive", "collapsed", "crisis")
   - Unsuitable for institutional investors
   - Example: "Explosive scale expansion" vs "Strong revenue growth"

2. **Data Presentation Issues**:
   - Poor handling of missing data ("N/A" entries break flow)
   - Inconsistent currency notation (RM vs MYR mixed)
   - Missing basis points notation (uses "%" instead of "bps" for small changes)

3. **Data Accuracy Risk**:
   - No automated validation that numbers match source data
   - Incorrect YoY calculations possible
   - Inconsistent values across sections

4. **Quality Control Gap**:
   - No validation step before delivery
   - Errors only caught by manual review

**Impact**: Reports are less professional and risk data accuracy issues that undermine credibility.

---

## Solution: Multi-Layer Quality System

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│         Multi-Layer Quality System                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Layer 1: Enhanced Instructions                          │
│  ├─ writing_standards.md (expanded)                      │
│  ├─ tone_guidelines.md (NEW)                             │
│  └─ worker_1-7_*.md (rewritten with examples)           │
│                                                          │
│  Layer 2: Sample Library                                 │
│  ├─ samples/sections/good/ (10-15 examples)             │
│  ├─ samples/sections/bad/ (10-15 anti-patterns)         │
│  └─ samples/comparison_guide.md                          │
│                                                          │
│  Layer 3: Automated Validation (DATA ACCURACY PRIORITY)  │
│  ├─ scripts/validate_report.py (NEW)                    │
│  ├─ Quality checks: data, calculations, tone, formatting│
│  └─ CLI wrapper: finanalysis validate-report            │
│                                                          │
│  Layer 4: Updated Workflow                               │
│  └─ skill.md (add validation step before delivery)      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Key Innovation**: Data accuracy validation takes priority over formatting. Critical issues must be fixed before delivery.

---

## Layer 1: Enhanced Instructions

### 1.1 Writing Standards Expansion

**File**: `references/writing_standards.md`

**Changes**:
- Add "Professional Tone Standards" section
- Add "Data Presentation Standards" section
- Include "Good vs. Bad" examples for each principle

**Key Additions**:

```markdown
## Professional Tone Standards

**DO use measured language:**
- ✅ "Revenue increased 58% YoY" (factual)
- ✅ "Margin expansion suggests improved efficiency" (interpretive)
- ✅ "Cash generation weakened" (clear but professional)

**DON'T use aggressive language:**
- ❌ "Explosive scale expansion" → "Strong revenue growth"
- ❌ "Margin collapsed" → "Margin declined significantly"
- ❌ "Crisis in cash flow" → "Cash conversion challenges"

## Data Presentation Standards

**Handling Missing Data:**
- ❌ DON'T: "| Metric | N/A | N/A |"
- ✅ DO: "| Metric | - | - | *Not disclosed in available statements*"

**Currency Formatting:**
- Standardize to "RM" throughout (not MYR)
- Always include "RM million" in table headers
- Example: "| Revenue (RM million) | 3,252 | 2,057 |"

**Basis Points Notation:**
- Use "bps" for changes < 100 basis points
- Use "ppt" for changes ≥ 100 basis points
- Examples:
  - "Gross margin improved 699bps" (not "6.99%")
  - "PBT margin declined 72bps" (not "0.72%")
  - "Attributable margin declined 12.16ppt" (not "12.16%")
```

### 1.2 Tone Guidelines Document (NEW)

**File**: `references/tone_guidelines.md` (NEW)

**Purpose**: Comprehensive language rules for professional financial writing

**Structure**:
- Philosophy: "Write for institutional investors: clear, measured, evidence-based"
- Language classification: ✅ Professional, ⚠️ Caution, ❌ Avoid
- Tone by section: Executive Summary (most measured), Risk Warning (direct but not alarmist)
- Before & After examples

**Key Content**:

```markdown
## Language Classification

### ✅ Professional Language (Use These)
- "Strong revenue growth" (not "explosive")
- "Margin expanded significantly" (not "surged dramatically")
- "Profitability improved materially" (not "skyrocketed")
- "Cash generation weakened" (not "collapsed")
- "Attribution quality deteriorated" (not "collapsed")
- "Leverage increased" (not "ballooned")

### ⚠️ Caution - Use Sparingly
- "Exceptional growth" (only for >50% YoY)
- "Dramatic improvement" (only for >100% YoY)
- "Material deterioration" (only for >20% decline)

### ❌ Avoid - Too Aggressive
- "Explosive", "collapsed", "crisis", "skyrocketed"
- "Plummeted", "ballooned", "hemorrhaged"
- "Disaster", "catastrophic", "devastating"

## Examples: Before & After

**Before (too aggressive):**
> "Attributable margin collapsed from 37.06% to 24.90% despite PAT growth"

**After (professional):**
> "Attributable margin declined from 37.06% to 24.90% despite PAT growth, indicating rising minority interests eroding shareholder value"
```

### 1.3 Worker Instruction Rewrites

**Files**: All 7 worker instruction files (`worker_1_context_setup.md` through `worker_7_summary.md`)

**Update Strategy**:
- **Add 2-3 examples per worker** (max 500 words total addition)
- **Prioritize sections with most errors** (based on CHINHIN issues)
- **Keep instructions focused** (avoid context bloat)

**Template Structure for Each Worker File**:

```markdown
# Worker N: [Section Name]

## Your Task
[Existing content - preserve]

## What to Avoid ⭐ NEW
[2-3 specific anti-patterns with corrections]

## Good vs. Bad Examples ⭐ NEW
[1-2 concrete before/after examples]

## Your Data Bundle
[Existing content - preserve]

## Output Format
[Existing content - preserve]

## Quality Checklist (Expanded) ⭐ UPDATED
[Add 3-4 new tone/formatting items to existing checklist]
```

**Detailed Changes to Each**:

**Worker 1** (`worker_1_context_setup.md`):
- Add: Professional tone in company description (avoid "industry leader", "dominant")
- Add: Data handling for missing fiscal year end
- Example: Good vs bad company profile tone

**Worker 2** (`worker_2_core_performance.md`) - **PRIORITY** (most issues found):
- Add: 3 tone examples (aggressive → professional)
- Add: YoY calculation verification reminder
- Add: Basis points notation examples
- Add: Table formatting examples

**Worker 3** (`worker_3_business_analysis.md`):
- Add: Handling missing segment data gracefully
- Add: Professional geographic analysis tone
- Add: Industry context without hyperbole

**Worker 4** (`worker_4_operational_health.md`):
- Add: Solvency ratio language (avoid "crisis", "collapsed")
- Add: Working capital terminology standards
- Add: Liquidity analysis professional phrasing

**Worker 5** (`worker_5_profitability_growth.md`) - **PRIORITY** (many issues):
- Add: Margin terminology (expanded vs improved vs increased)
- Add: ROE/ROA phrasing standards
- Add: Growth quality assessment language

**Worker 6** (`worker_6_risk_cashflow.md`) - **PRIORITY** (tone critical):
- Add: Risk language standards (avoid "disaster", "crisis", "catastrophic")
- Add: Cash flow terminology (weakened vs collapsed)
- Add: Forecast language (measured, probability-weighted)

**Worker 7** (`worker_7_summary.md`):
- Add: Summary tone (most measured of all sections)
- Add: Risk warning phrasing (direct but not alarmist)
- Add: Trend interpretation language

**Concrete Update Example** (Worker 2 - `worker_2_core_performance.md`):

```markdown
## What to Avoid

❌ **Aggressive language:**
- "Explosive growth" → Use "Strong growth"
- "Margin collapsed" → Use "Margin declined significantly"
- "Crisis in profitability" → Use "Profitability challenges"

❌ **Poor data handling:**
- Don't use "N/A" in tables
- Don't mix currency notation (RM vs MYR)
- Don't forget basis points for small changes

## Good vs. Bad Examples

**Bad (too aggressive):**
> - **Explosive scale expansion**: Revenue +58.1% YoY, largest growth in recent years

**Good (professional):**
> - **Strong revenue growth**: Revenue +58.1% YoY to RM3.25b, driven by construction recovery and East Malaysia expansion

## Quality Checklist (Expanded)

✅ Tone is measured and professional
✅ No aggressive language ("explosive", "collapsed", "crisis")
✅ Missing data handled gracefully (not "N/A")
✅ Currency notation consistent ("RM" throughout)
✅ Basis points used for changes < 100bps
✅ Numbers match data bundle
✅ YoY calculations verified
```

---

## Layer 2: Sample Library

### 2.1 Directory Structure

Create `skills/financial-analysis-report/samples/`:

```
samples/
├── sections/
│   ├── good/
│   │   ├── section_iv_good_example.md     (Core Conclusions - 4677.KL)
│   │   ├── section_v_good_example.md      (Core Performance - 4677.KL)
│   │   ├── section_vi_good_example.md     (Business Analysis - 4677.KL)
│   │   ├── section_ix_good_example.md     (Risk Scan - 4677.KL)
│   │   ├── section_xii_good_example.md    (Profitability - 4677.KL)
│   │   ├── summary_good_example.md        (Full Summary - 4677.KL)
│   │   └── table_formatting_good.md       (Table examples)
│   │
│   └── bad/
│       ├── aggressive_language_bad.md     (CHINHIN issues)
│       ├── na_usage_bad.md                (N/A handling issues)
│       ├── currency_inconsistent_bad.md   (RM vs MYR mixing)
│       └── missing_bps_bad.md             (Basis points issues)
│
└── comparison_guide.md                    (How to use samples)
```

### 2.2 Sample Content

**Good Example** (`sections/good/section_iv_good_example.md`):
- Taken from 4677.KL report (professional standard)
- Shows measured tone, proper formatting, complete data
- Workers can use as template

**Bad Example** (`sections/bad/aggressive_language_bad.md`):
- Shows CHINHIN issues with annotations
- Highlights what NOT to do
- Provides corrected versions

**Comparison Guide** (`comparison_guide.md`):
- Quick reference table mapping section types to samples
- Key differences summary (4677.KL vs CHINHIN)
- Instructions for workers on how to use samples

---

## Layer 3: Automated Validation (DATA ACCURACY PRIORITY)

### 3.1 Validation Script

**File**: `scripts/validate_report.py` (NEW)

**Priority Order**:
1. **CRITICAL**: Data accuracy (must fix before delivery)
   - Numbers match source data (fs_index.json)
   - Calculations are correct (YoY %, margins, ratios)
   - Metrics are consistent across sections
   - Units are correct (RM'000 vs RM million)

2. **IMPORTANT**: Formatting (can fix later)
   - Tone quality (aggressive language)
   - Basis points notation
   - Currency consistency
   - N/A usage

**Key Features**:

```python
class DataValidator:
    """Validates financial data accuracy in reports."""

    def validate_data_accuracy(self, content: str) -> List[Tuple[int, str, str]]:
        """Check numbers in report match source data."""
        # Verifies critical metrics: revenue, PBT, PAT, assets, equity
        # Matches expected values from fs_index.json within 1% tolerance
        # Reports missing or incorrect values

    def validate_calculations(self, content: str) -> List[Tuple[int, str, str]]:
        """Verify YoY % and margin calculations are correct."""
        # Extracts reported YoY percentages
        # Recalculates from current/prior values
        # Flags discrepancies > 0.1%

    def validate_consistency(self, content: str) -> List[Tuple[int, str, str]]:
        """Check same metric has consistent values across sections."""
        # Extracts all mentions of key metrics
        # Checks values are consistent (within 1%)
        # Reports all inconsistent values found

    def validate_units(self, content: str) -> List[Tuple[int, str, str]]:
        """Check units are correct and consistent."""
        # Detects RM'000 vs RM million confusion
        # Prevents 1000x errors from unit mix-ups
```

### 3.1.1 Validation Implementation Approach

**Number Extraction Strategy**:

```python
# Regex patterns for common number formats in financial reports
NUMBER_PATTERNS = {
    'with_commas': r'([\d,]+(?:\.\d+)?)',           # 3,252.4
    'with_units': r'(?:RM\s*)?([\d.]+)\s*[mb]illion',  # RM3.25b or 3.25 million
    'percentage': r'([\d.]+)%',                      # 58.1%
    'parentheses': r'\(([\d,]+(?:\.\d+)?)\)',       # (1,234) for negative
    'shorthand': r'([\d.]+)\s*[kmb]',               # 3.2b for 3,200,000,000
}

def extract_numbers_from_markdown(content: str) -> List[ExtractedNumber]:
    """Extract all numbers with context from markdown report."""
    extracted = []

    # 1. Find all table cells with numbers
    table_pattern = r'\|?\s*([\w\s]+?)\s*\|?\s*([\d,]+(?:\.\d+)?)\s*\|'
    for match in re.finditer(table_pattern, content):
        metric_name = match.group(1).strip()
        value_str = match.group(2).replace(',', '')
        try:
            value = float(value_str)
            extracted.append(ExtractedNumber(
                value=value,
                context=metric_name,
                line_num=content[:match.start()].count('\n') + 1
            ))
        except ValueError:
            continue

    # 2. Find inline numbers with context (5 words before/after)
    # Pattern: "Revenue increased to RM3,252 million"
    inline_pattern = r'([\w\s]{0,50})\s+(?:RM\s*)?([\d,]+(?:\.\d+)?)\s*(?:million|billion)?'
    # ... extract with surrounding context

    return extracted
```

**Field Mapping Strategy**:

```python
# Map common metric names to fs_index.json field names
METRIC_ALIASES = {
    'revenue': ['revenue', 'total revenue', 'sales', 'turnover'],
    'gross_profit': ['gross profit', 'profit before overhead', 'gross operating profit'],
    'pbt': ['profit before tax', 'pbt', 'profit before taxation'],
    'pat': ['profit after tax', 'pat', 'profit for the year', 'net profit'],
    'total_assets': ['total assets', 'total non-current and current assets'],
    'total_equity': ['total equity', "shareholders' equity", 'total shareholders\' funds'],
}

def find_expected_value(metric_name: str, fs_index: dict) -> Optional[float]:
    """Find expected value from fs_index.json using fuzzy matching."""
    # Normalize metric name
    normalized = metric_name.lower().strip()

    # Try exact match first
    for alias_key, aliases in METRIC_ALIASES.items():
        if normalized in aliases:
            # Found match, look in fs_index
            if alias_key in fs_index['line_items']:
                return fs_index['line_items'][alias_key]['group_current']

    # Try fuzzy match (Levenshtein distance)
    for alias_key, aliases in METRIC_ALIASES.items():
        for alias in aliases:
            if levenshtein_distance(normalized, alias) <= 3:  # Allow 3 char diff
                if alias_key in fs_index['line_items']:
                    return fs_index['line_items'][alias_key]['group_current']

    return None  # Not found
```

**Example Validation Flow**:

```python
# Example: Validate revenue in report

# 1. Extract from report
report_text = """
| Revenue (RM million) | 3,252 | 2,057 | +58.1% |
Revenue increased to RM3,252 million from RM2,057 million...
"""

extracted = extract_numbers_from_markdown(report_text)
# Found: ExtractedNumber(value=3252.0, context='Revenue', line_num=5)
#        ExtractedNumber(value=2057.0, context='Revenue', line_num=5)

# 2. Load expected from fs_index.json
fs_index = json.load('fs_index.json')
expected_current = fs_index['line_items']['revenue']['group_current']  # 3,252,347
expected_prior = fs_index['line_items']['revenue']['group_prior']      # 2,057,210

# 3. Compare with tolerance
def values_match(reported: float, expected: float, tolerance_pct: float = 0.01) -> bool:
    """Check if values match within tolerance (default 1%)."""
    if expected == 0:
        return reported == 0
    return abs(reported - expected) / abs(expected) <= tolerance_pct

# 4. Validate
reported_value = 3252.0  # RM million
expected_value = 3252.347  # RM million (from fs_index which is in RM'000)

# Adjust for units (report uses RM million, fs_index uses RM'000)
expected_in_millions = expected_value / 1000  # 3,252.347

if not values_match(reported_value, expected_in_millions):
    print(f"❌ Revenue mismatch: reported {reported_value}, expected {expected_in_millions}")
```

**Error Handling for Missing Data Sources**:

```python
def validate_with_fallback(report_path: Path, fs_index_path: Path, metrics_path: Optional[Path]):
    """Validate report, gracefully degrading if data sources missing."""

    # Always require fs_index.json
    if not fs_index_path.exists():
        print("❌ CRITICAL: fs_index.json not found - cannot validate data accuracy")
        print("   Run: finanalysis parse <pdf> --company <NAME>")
        sys.exit(1)

    fs_index = json.loads(fs_index_path.read_text())

    # Metrics.json is optional (enhanced validation)
    metrics = {}
    if metrics_path and metrics_path.exists():
        metrics = json.loads(metrics_path.read_text())
        print("✓ Using metrics.json for ratio validation")
    else:
        print("⚠ metrics.json not provided - ratio validation skipped")
        print("  Run: finanalysis calculate fs_index.json --output metrics.json")

    # Run validation with available data
    validator = DataValidator(fs_index, metrics)
    issues = validator.validate(report_path.read_text())

    return issues
```

### 3.3 Data Source Requirements

**Required Data Sources**:

| Validation Type | Required Source | Generated By | Command |
|---|---|---|---|
| Data Accuracy | `fs_index.json` | Stage 4 (FSIndex) | `finanalysis parse <pdf>` |
| Calculation Validation | `metrics.json` | MetricsCalculator | `finanalysis calculate fs_index.json` |
| Unit Validation | `fs_index.json` | Stage 4 (FSIndex) | `finanalysis parse <pdf>` |
| Consistency Validation | `fs_index.json` | Stage 4 (FSIndex) | `finanalysis parse <pdf>` |

**Graceful Degradation**:

```python
# Validation behavior based on available sources

# SCENARIO 1: Only fs_index.json available (minimal validation)
$ python validate_report.py report.md --data fs_index.json

Validates:
  ✓ Numbers match fs_index.json (data accuracy)
  ✓ YoY calculations correct
  ✓ Units consistent
  ✓ Values consistent across sections

Skips:
  ⚠ Ratio calculations (requires metrics.json)
  ⚠ Margin calculations (requires metrics.json)

# SCENARIO 2: Both fs_index.json and metrics.json available (full validation)
$ python validate_report.py report.md --data fs_index.json --metrics metrics.json

Validates:
  ✓ All SCENARIO 1 checks PLUS:
  ✓ Gross margin calculation matches metrics.json
  ✓ PBT margin calculation matches metrics.json
  ✓ Current ratio matches metrics.json
  ✓ ROE/ROA calculations match metrics.json
```

**Workflow Integration**:

```bash
# Option 1: Auto-generate metrics.json if missing
if [ ! -f "metrics.json" ]; then
    echo "metrics.json not found, generating..."
    finanalysis calculate fs_index.json --output metrics.json
fi

# Then validate
finanalysis validate-report report.md --data fs_index.json --metrics metrics.json

# Option 2: Validate with what's available (graceful degradation)
finanalysis validate-report report.md --data fs_index.json
# Outputs warning but continues with available validation
```

**Usage**:

```bash
# Validate report with source data
python scripts/validate_report.py CHINHIN-2024-revised.md \
  --data output/CHINHIN/2024/fs_index.json \
  --metrics output/CHINHIN/2024/metrics.json
```

**Exit Codes**:
- `0` = All checks passed (or only formatting issues)
- `1` = Critical data accuracy issues found

**Example Output**:

```
======================================================================
VALIDATION REPORT: CHINHIN-2024-revised.md
======================================================================

❌ CRITICAL - 3 DATA ACCURACY ISSUE(S):

These MUST be fixed before delivery:

----------------------------------------------------------------------
         Incorrect YoY calculation for 'Revenue'
         → Reported: 58.1%, Calculated: 58.2%

         Incorrect gross margin calculation
         → Reported: 16.15%, Calculated: 16.14%

         Inconsistent revenue values across report
         → Found values: 3,252, 3,253


⚠️  FORMATTING - 2 issue(s):

----------------------------------------------------------------------
  Aggressive language: 'explosive'
  → Consider: 'strong growth'
```

### 3.2 CLI Integration

**File**: `src/finanalysis/cli.py` (UPDATED)

Add new subcommand:

```python
@cli.command('validate-report')
@click.argument('report', type=click.Path(exists=True))
@click.option('--data', type=click.Path(exists=True), required=True,
              help='Path to fs_index.json (source data)')
@click.option('--metrics', type=click.Path(exists=True),
              help='Path to metrics.json (calculated ratios)')
@click.pass_context
def validate_report(ctx, report, data, metrics):
    """Validate financial analysis report for data accuracy.

    Checks:
    - Numbers match source data (fs_index.json)
    - Calculations are correct (YoY %, margins)
    - Metrics are consistent across sections
    - Units are correct

    Exit codes:
        0 = All checks passed
        1 = Critical data accuracy issues found
    """
    # Thin wrapper that calls skill script
    # Allows users to use either:
    #   finanalysis validate-report report.md --data fs_index.json
    #   OR
    #   python skills/.../validate_report.py report.md --data fs_index.json
```

**Rationale**: Hybrid approach provides convenience (CLI) while keeping validation logic with skill (maintainability).

---

## Layer 4: Updated Workflow

### 4.1 Coordinator Workflow Update

**File**: `skill.md` (UPDATED)

Add validation step between assembly and delivery:

```markdown
## Coordinator Workflow (Updated)

### Phase 1-3: Preparation, Workers, Assembly (unchanged)

### Phase 4: Quality Validation ⭐ NEW

**CRITICAL: Validate data accuracy before delivery**

```bash
# Validate report with source data
python skills/financial-analysis-report/scripts/validate_report.py \
  CHINHIN-2024-revised.md \
  --data output/CHINHIN/2024/fs_index.json \
  --metrics output/CHINHIN/2024/metrics.json
```

**If validation fails:**

#### 4.1.1 Error Resolution Workflow

**For CRITICAL Issues (Data Accuracy)** - MUST FIX:

1. **Identify Issue Type**:
   ```bash
   # Validation output shows:
   ❌ CRITICAL - 3 DATA ACCURACY ISSUE(S):

   1. Incorrect YoY calculation for 'Revenue'
      → Reported: 58.1%, Calculated: 58.2%

   2. Gross margin mismatch
      → Reported: 16.15%, Expected: 16.14%

   3. Inconsistent revenue values
      → Found: 3,252 in Section IV, 3,253 in Section V
   ```

2. **Coordinator Fix Strategy**:
   - **Option A: Direct Fix** (for simple errors)
     - Coordinator reads problematic section
     - Updates incorrect values
     - Re-runs validation
     - Max 2 attempts per section

   - **Option B: Regenerate Section** (for complex errors)
     - Coordinator re-spawns specific worker with corrected data
     - Worker rewrites section with validation feedback
     - Coordinator replaces section in assembled report
     - Re-run validation
     - Max 1 regeneration per section

   - **Option C: Human Escalation** (if automated fixes fail)
     - After 2 fix attempts + 1 regeneration still failing
     - Coordinator delivers report with validation issues flagged
     - Provides human-readable summary of issues
     - User decides whether to proceed or fix manually

3. **Fix Loop Limit**:
   ```
   Max retries per issue: 2 direct fixes + 1 regeneration = 3 total attempts
   If still failing after 3 attempts → Escalate to human
   ```

**For FORMATTING Issues** - OPTIONAL:

- Coordinator logs formatting issues for future reference
- Does NOT block delivery
- User can optionally request fixes post-delivery

**Example Fix Loop**:

```bash
# Iteration 1: Initial validation
$ finanalysis validate-report report.md --data fs_index.json
❌ CRITICAL: Revenue YoY calculation incorrect (58.1% vs 58.2%)

# Iteration 2: Coordinator fixes directly
Coordinator reads Section IV, finds: "| Revenue | 3,252 | 2,057 | +58.1% |"
Updates to: "| Revenue | 3,252 | 2,057 | +58.2% |"

$ finanalysis validate-report report.md --data fs_index.json
✅ PASSED - Data accuracy verified
⚠️  FORMATTING: Aggressive language in 2 locations (optional fix)
```

**Issue Classification**:

| Issue Type | Priority | Fix Required | Max Attempts |
|---|---|---|---|
| Incorrect number vs source | CRITICAL | Yes | 2 direct + 1 regenerate |
| Wrong YoY/margin calculation | CRITICAL | Yes | 2 direct + 1 regenerate |
| Inconsistent values across sections | CRITICAL | Yes | 2 direct + 1 regenerate |
| Unit confusion (RM'000 vs RMm) | CRITICAL | Yes | 2 direct + 1 regenerate |
| Aggressive language | FORMATTING | Optional | N/A |
| Missing basis points | FORMATTING | Optional | N/A |
| Currency notation (RM vs MYR) | FORMATTING | Optional | N/A |

**Detailed Issue Types**:

- ❌ **CRITICAL issues (data accuracy)**: Fix immediately before delivery
  - Incorrect numbers: Reported value doesn't match fs_index.json
  - Wrong calculations: YoY %, margins, ratios calculated incorrectly
  - Inconsistent values: Same metric has different values in different sections
  - Unit errors: RM'000 confused with RM million (1000x error)

- ⚠️ **FORMATTING issues**: Optional fixes, report still valid
  - Aggressive language
  - Missing basis points
  - Currency notation

**Alternative: Use CLI wrapper**
```bash
finanalysis validate-report CHINHIN-2024-revised.md \
  --data output/CHINHIN/2024/fs_index.json \
  --metrics output/CHINHIN/2024/metrics.json
```

### Phase 5: Executive Summary (only after validation passes)

Generate summary from validated report.

### Phase 6: Final Delivery

Deliver both files:
- `<TICKER>-<PERIOD>-revised.md` (validated full report)
- `<TICKER>-<PERIOD>-summary.md` (executive summary)
```

### 4.2 Updated File Structure

```
skills/financial-analysis-report/
├── skill.md                          # UPDATED: add validation step
├── references/
│   ├── writing_standards.md          # EXPANDED: tone + formatting rules
│   ├── tone_guidelines.md            # NEW: comprehensive language rules
│   ├── worker_1_context_setup.md     # REWRITTEN: better examples
│   ├── worker_2_core_performance.md  # REWRITTEN: better examples
│   ├── worker_3_business_analysis.md # REWRITTEN: better examples
│   ├── worker_4_operational_health.md# REWRITTEN: better examples
│   ├── worker_5_profitability_growth.md # REWRITTEN: better examples
│   ├── worker_6_risk_cashflow.md     # REWRITTEN: better examples
│   └── worker_7_summary.md           # REWRITTEN: better examples
│
├── scripts/
│   ├── generate_report.py            # Existing
│   ├── assemble_report.py            # Existing
│   ├── data_extractor.py             # Existing
│   └── validate_report.py            # NEW: data validation (priority)
│
├── samples/                          # NEW: sample library
│   ├── sections/
│   │   ├── good/
│   │   │   ├── section_iv_good_example.md
│   │   │   ├── section_v_good_example.md
│   │   │   ├── section_ix_good_example.md
│   │   │   ├── section_xii_good_example.md
│   │   │   ├── summary_good_example.md
│   │   │   └── table_formatting_good.md
│   │   └── bad/
│   │       ├── aggressive_language_bad.md
│   │       ├── na_usage_bad.md
│   │       ├── currency_inconsistent_bad.md
│   │       └── missing_bps_bad.md
│   └── comparison_guide.md
│
└── sample-report/                    # Existing sample reports
    ├── 4677.KL-2024-12-31-revised.md
    └── 4677-summary.md

src/finanalysis/
└── cli.py                            # UPDATED: add validate-report command
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Priority 1)
1. Create `validate_report.py` script with data validation focus
2. Add CLI wrapper to `cli.py`
3. Update `skill.md` with validation workflow

### Phase 2: Instruction Improvements (Priority 2)
4. Expand `writing_standards.md` with tone and formatting sections
5. Create `tone_guidelines.md`
6. Rewrite all 7 worker instruction files

### Phase 3: Sample Library (Priority 3)
7. Create `samples/` directory structure
8. Extract good examples from 4677.KL report
9. Create bad examples from CHINHIN issues
10. Write `comparison_guide.md`

### Phase 4: Testing & Validation
11. Regenerate CHINHIN report with new workflow
12. Validate against 4677.KL quality standard
13. Run benchmark tests to verify no regressions

---

## Success Criteria

1. **Data Accuracy**: Zero data accuracy issues in generated reports
   - All numbers match source data
   - All calculations correct
   - No inconsistent values

2. **Tone Quality**: Professional language suitable for institutional investors
   - No aggressive language ("explosive", "collapsed", "crisis")
   - Measured, evidence-based tone
   - Matches 4677.KL standard

3. **Formatting Quality**: Consistent presentation
   - Missing data handled gracefully (no "N/A")
   - Currency notation standardized ("RM")
   - Basis points notation correct

4. **Validation Coverage**: Critical issues caught before delivery
   - Data validation runs automatically
   - Critical issues block delivery
   - Formatting issues reported but don't block

5. **Worker Compliance**: Workers follow guidelines
   - Use good examples as templates
   - Avoid bad patterns
   - Meet quality checklists

---

## Testing Strategy

### Test Case 1: CHINHIN Report Regeneration
**Input**: CHINHIN 2024 data
**Expected**: Report matches 4677.KL quality standard
**Validation**: Run validate_report.py, expect 0 critical issues

### Test Case 2: Data Accuracy Detection
**Input**: Report with intentional data errors
**Expected**: Validation catches all errors
**Validation**: Inject errors, verify detection

### Test Case 3: Tone Improvement
**Input**: Generate new report with updated instructions
**Expected**: No aggressive language
**Validation**: Manual review + tone validation

### Test Case 4: Worker Compliance
**Input**: Workers with new instruction files
**Expected**: Output matches good examples
**Validation**: Compare worker outputs to good samples

---

## Risks & Mitigation

### Risk 1: Validation False Positives
**Risk**: Validation flags correct values as errors
**Mitigation**: Use 1% tolerance for rounding, test on multiple reports

### Risk 2: Worker Instructions Too Long
**Risk**: Workers hit context limits with expanded instructions
**Mitigation**: Keep instructions focused, use sample library for examples

### Risk 3: Validation Script Complexity
**Risk**: Script becomes difficult to maintain
**Mitigation**: Start simple, add checks incrementally, good test coverage

### Risk 4: CLI Integration Issues
**Risk**: Path resolution fails in different environments
**Mitigation**: Test on multiple setups, provide fallback direct script usage

---

## Alternatives Considered

### Alternative 1: Minimal Surgical Fixes
**Description**: Update only writing standards, no validation
**Rejected**: Doesn't address data accuracy risk, relies solely on LLM compliance

### Alternative 2: Add to finanalysis CLI Only
**Description**: Move validation to core CLI, not skill
**Rejected**: Mixes concerns (parsing vs report quality), validation is skill-specific

### Alternative 3: Manual Quality Checklist
**Description**: Coordinator manually checks quality
**Rejected**: Error-prone, not scalable, data accuracy too important to trust to manual review

**Chosen Approach**: Multi-layer quality system provides defense in depth - better instructions + automated validation + workflow enforcement.

---

## Future Enhancements

1. **Machine Learning Validation**: Train model on good/bad examples for automatic tone detection
2. **Continuous Benchmarking**: Track quality metrics across all generated reports
3. **Worker Performance Metrics**: Track which workers generate best quality
4. **Auto-fix Capability**: Script automatically fixes formatting issues
5. **Integration Tests**: Automated test suite runs on every skill change

---

## Conclusion

This design creates a robust, multi-layer quality system that:

1. **Prioritizes data accuracy** - Critical validation before delivery
2. **Improves instructions** - Workers have better guidance
3. **Provides examples** - Workers can reference good patterns
4. **Automates validation** - Catches issues even if workers don't follow instructions
5. **Updates workflow** - Quality check built into process

The result: Professional, accurate reports suitable for institutional investors, with data accuracy guaranteed through automated validation.

---

**Implementation Time Estimate**: 4-5 hours
- Phase 1 (Core): 1.5 hours
- Phase 2 (Instructions): 1.5 hours
- Phase 3 (Samples): 1 hour
- Phase 4 (Testing): 1 hour
