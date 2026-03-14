# Financial Analysis Report Skill - Quality Improvements Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build multi-layer quality system for financial analysis reports with data accuracy validation, professional tone standards, and automated quality checks.

**Architecture:** 4-layer defense system: (1) Enhanced worker instructions with examples, (2) Sample library for reference, (3) Automated validation script prioritizing data accuracy, (4) Updated coordinator workflow with validation step before delivery.

**Tech Stack:** Python 3.11, Click (CLI), pytest (testing), regex for number extraction, JSON for data sources (fs_index.json, metrics.json)

---

## File Structure

```
skills/financial-analysis-report/
├── scripts/
│   └── validate_report.py            # CREATE: data validation script
├── references/
│   ├── writing_standards.md          # MODIFY: add tone + formatting sections
│   ├── tone_guidelines.md            # CREATE: comprehensive language rules
│   ├── worker_1_context_setup.md     # MODIFY: add examples (+400 words)
│   ├── worker_2_core_performance.md  # MODIFY: add examples (+500 words)
│   ├── worker_3_business_analysis.md # MODIFY: add examples (+400 words)
│   ├── worker_4_operational_health.md# MODIFY: add examples (+400 words)
│   ├── worker_5_profitability_growth.md # MODIFY: add examples (+500 words)
│   ├── worker_6_risk_cashflow.md     # MODIFY: add examples (+500 words)
│   └── worker_7_summary.md           # MODIFY: add examples (+400 words)
├── samples/                          # CREATE: entire directory
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
└── skill.md                          # MODIFY: add validation workflow

src/finanalysis/
└── cli.py                            # MODIFY: add validate-report command

tests/skills/financial-analysis-report/
└── test_validate_report.py           # CREATE: validation script tests
```

**Key Decomposition Decisions:**
- Validation script (validate_report.py) is self-contained with all logic
- CLI wrapper (cli.py) is thin - just calls validation script
- Sample files are markdown (not code) - workers read them directly
- Tests cover validation script only (not CLI wrapper - trivial)

---

## Chunk 1: Validation Script Core (Phase 1)

### Task 1: Data Models and Number Extraction

**Files:**
- Create: `skills/financial-analysis-report/scripts/validate_report.py`
- Create: `tests/skills/financial-analysis-report/test_validate_report.py`

- [ ] **Step 1: Write failing test for ExtractedNumber dataclass**

```python
# tests/skills/financial-analysis-report/test_validate_report.py
"""Tests for financial report validation script."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.financial_analysis_report.scripts.validate_report import ExtractedNumber


def test_extracted_number_creation():
    """Test ExtractedNumber dataclass can be created."""
    num = ExtractedNumber(value=3252.0, context="Revenue", line_num=5)
    assert num.value == 3252.0
    assert num.context == "Revenue"
    assert num.line_num == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_extracted_number_creation -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'skills.financial_analysis_report.scripts.validate_report'"

- [ ] **Step 3: Write minimal implementation**

```python
# skills/financial-analysis-report/scripts/validate_report.py
#!/usr/bin/env python3
"""
Financial Report Data Validator

Validates generated financial analysis reports for:
- Data accuracy (numbers match source data)
- Calculation correctness (YoY %, margins, ratios)
- Consistency across sections
- Tone quality (aggressive language)
- Formatting (basis points, currency notation)

Usage:
    python scripts/validate_report.py report.md --data fs_index.json [--metrics metrics.json]
"""
import re
import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import argparse


@dataclass
class ExtractedNumber:
    """Represents a number extracted from report with context."""
    value: float
    context: str  # Metric name or surrounding text
    line_num: int  # Line number in report


# Map common metric names to fs_index.json field names
METRIC_ALIASES = {
    'revenue': ['revenue', 'total revenue', 'sales', 'turnover'],
    'gross_profit': ['gross profit', 'profit before overhead', 'gross operating profit'],
    'pbt': ['profit before tax', 'pbt', 'profit before taxation'],
    'pat': ['profit after tax', 'pat', 'profit for the year', 'net profit'],
    'total_assets': ['total assets', 'total non-current and current assets'],
    'total_equity': ['total equity', "shareholders' equity", 'total shareholders\' funds'],
}

# Aggressive language patterns to flag
AGGRESSIVE_WORDS = {
    "explosive": "strong growth",
    "collapsed": "declined significantly",
    "crisis": "challenge",
    "skyrocketed": "increased significantly",
    "plummeted": "declined sharply",
    "ballooned": "expanded significantly",
    "hemorrhaged": "declined",
    "catastrophic": "severe",
    "disaster": "significant challenge",
}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Validate financial analysis report')
    parser.add_argument('report', type=Path, help='Path to report markdown file')
    parser.add_argument('--data', type=Path, required=True,
                       help='Path to fs_index.json (source data)')
    parser.add_argument('--metrics', type=Path,
                       help='Path to metrics.json (calculated ratios)')

    args = parser.parse_args()

    if not args.report.exists():
        print(f"Error: Report file not found: {args.report}")
        sys.exit(1)

    if not args.data.exists():
        print(f"Error: Data file not found: {args.data}")
        sys.exit(1)

    # TODO: Implement validation
    print("Validation not yet implemented")
    sys.exit(0)


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_extracted_number_creation -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/financial-analysis-report/scripts/validate_report.py tests/skills/financial-analysis-report/test_validate_report.py
git commit -m "feat(validation): add ExtractedNumber dataclass for report validation

- Create validate_report.py script skeleton
- Add ExtractedNumber dataclass to track extracted values
- Add basic CLI argument parsing
- Add test for ExtractedNumber creation

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Number Extraction from Tables

**Files:**
- Modify: `skills/financial-analysis-report/scripts/validate_report.py:30-35`
- Modify: `tests/skills/financial-analysis-report/test_validate_report.py:15-20`

- [ ] **Step 1: Write failing test for table number extraction**

```python
# tests/skills/financial-analysis-report/test_validate_report.py (append)
def test_extract_numbers_from_tables():
    """Test extracting numbers from markdown tables."""
    from skills.financial_analysis_report.scripts.validate_report import extract_numbers_from_markdown

    report = """
| Metric | FY2024 | FY2023 | YoY |
|---|---:|---:|---:|
| Revenue | 3,252 | 2,057 | +58.1% |
| PBT | 276 | 189 | +45.9% |
"""

    numbers = extract_numbers_from_markdown(report)

    # Should find 4 numbers (Revenue current/prior, PBT current/prior)
    assert len(numbers) >= 4

    # Check revenue values found
    revenue_values = [n for n in numbers if 'revenue' in n.context.lower()]
    assert len(revenue_values) >= 2

    # Check values are correct
    values = [n.value for n in revenue_values]
    assert 3252.0 in values
    assert 2057.0 in values
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_extract_numbers_from_tables -v`
Expected: FAIL with "NameError: name 'extract_numbers_from_markdown' is not defined"

- [ ] **Step 3: Write minimal implementation**

```python
# skills/financial-analysis-report/scripts/validate_report.py (insert after ExtractedNumber, line ~30)

def extract_numbers_from_markdown(content: str) -> List[ExtractedNumber]:
    """Extract all numbers from markdown report with context.

    Focuses on table cells with format: | Metric | Value1 | Value2 | ...
    """
    extracted = []
    lines = content.split('\n')

    # Pattern to match table cells: | Metric | Value1 | Value2 | ...
    # Captures metric name and all numeric values in the row
    table_row_pattern = r'\|\s*([^|]+)\s*\|\s*([\d,]+(?:\.\d+)?)\s*\|\s*([\d,]+(?:\.\d+)?)\s*\|'

    for match in re.finditer(table_row_pattern, content):
        metric_name = match.group(1).strip()

        # Skip separator rows and headers
        if metric_name.startswith('---') or metric_name.lower() in ['metric', 'indicator']:
            continue

        # Extract current and prior year values
        for group_idx in [2, 3]:  # Groups 2 and 3 are the numeric columns
            value_str = match.group(group_idx).replace(',', '')
            try:
                value = float(value_str)

                # Calculate line number
                line_num = content[:match.start()].count('\n') + 1

                extracted.append(ExtractedNumber(
                    value=value,
                    context=metric_name,
                    line_num=line_num
                ))
            except ValueError:
                continue

    return extracted
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_extract_numbers_from_tables -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/financial-analysis-report/scripts/validate_report.py tests/skills/financial-analysis-report/test_validate_report.py
git commit -m "feat(validation): add table number extraction

- Implement extract_numbers_from_markdown() for table cells
- Extract metric name and values from markdown tables
- Handle comma-separated numbers (3,252 → 3252.0)
- Track line numbers for error reporting
- Add test for table extraction

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Field Mapping to fs_index.json

**Files:**
- Modify: `skills/financial-analysis-report/scripts/validate_report.py:65-70`
- Modify: `tests/skills/financial-analysis-report/test_validate_report.py:45-50`

- [ ] **Step 1: Write failing test for field mapping**

```python
# tests/skills/financial-analysis-report/test_validate_report.py (append)
def test_find_expected_value_from_fs_index():
    """Test mapping metric names to fs_index.json values."""
    from skills.financial_analysis_report.scripts.validate_report import find_expected_value

    # Mock fs_index structure
    fs_index = {
        'line_items': {
            'revenue': {
                'group_current': 3252347,  # RM'000
                'group_prior': 2057210
            },
            'pbt': {
                'group_current': 275845,
                'group_prior': 189318
            }
        }
    }

    # Test exact match
    result = find_expected_value('Revenue', fs_index)
    assert result == 3252347

    # Test alias match
    result = find_expected_value('Total Revenue', fs_index)
    assert result == 3252347

    # Test PBT
    result = find_expected_value('Profit before tax', fs_index)
    assert result == 275845

    # Test not found
    result = find_expected_value('Unknown Metric', fs_index)
    assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_find_expected_value_from_fs_index -v`
Expected: FAIL with "NameError: name 'find_expected_value' is not defined"

- [ ] **Step 3: Write minimal implementation**

```python
# skills/financial-analysis-report/scripts/validate_report.py (insert after extract_numbers_from_markdown)

def find_expected_value(metric_name: str, fs_index: dict) -> Optional[float]:
    """Find expected value from fs_index.json using fuzzy matching.

    Args:
        metric_name: Name as it appears in report (e.g., "Revenue", "Total Revenue")
        fs_index: Loaded fs_index.json structure

    Returns:
        Expected value (group_current) or None if not found
    """
    # Normalize metric name
    normalized = metric_name.lower().strip()

    # Try exact match first
    for alias_key, aliases in METRIC_ALIASES.items():
        if normalized in [a.lower() for a in aliases]:
            # Found match, look in fs_index
            if alias_key in fs_index.get('line_items', {}):
                return fs_index['line_items'][alias_key].get('group_current')

    # Try fuzzy match (simple: allow partial matches)
    for alias_key, aliases in METRIC_ALIASES.items():
        for alias in aliases:
            # Check if normalized contains alias or vice versa
            if alias.lower() in normalized or normalized in alias.lower():
                if alias_key in fs_index.get('line_items', {}):
                    return fs_index['line_items'][alias_key].get('group_current')

    return None  # Not found
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_find_expected_value_from_fs_index -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/financial-analysis-report/scripts/validate_report.py tests/skills/financial-analysis-report/test_validate_report.py
git commit -m "feat(validation): add field mapping to fs_index.json

- Implement find_expected_value() for metric lookup
- Support exact match and partial match (fuzzy)
- Map report metric names to fs_index field names
- Handle case-insensitive matching
- Add comprehensive tests

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Chunk 2: Validation Logic (Phase 1 continued)

### Task 4: Data Accuracy Validation

**Files:**
- Modify: `skills/financial-analysis-report/scripts/validate_report.py:100-105`
- Modify: `tests/skills/financial-analysis-report/test_validate_report.py:80-85`

- [ ] **Step 1: Write failing test for data accuracy validation**

```python
# tests/skills/financial-analysis-report/test_validate_report.py (append)
def test_validate_data_accuracy():
    """Test validating numbers match source data."""
    from skills.financial_analysis_report.scripts.validate_report import validate_data_accuracy

    report = """
| Metric | FY2024 | FY2023 |
|---|---:|---:|
| Revenue | 3,252 | 2,057 |
"""

    fs_index = {
        'line_items': {
            'revenue': {
                'group_current': 3252347,  # RM'000
                'group_prior': 2057210
            }
        }
    }

    issues = validate_data_accuracy(report, fs_index)

    # Should find no issues (3252 matches 3252.347 RM million within 1%)
    assert len(issues) == 0

    # Test with wrong value
    bad_report = """
| Metric | FY2024 | FY2023 |
|---|---:|---:|
| Revenue | 4,000 | 2,057 |
"""

    issues = validate_data_accuracy(bad_report, fs_index)

    # Should find 1 issue
    assert len(issues) == 1
    assert 'Revenue' in issues[0][1]  # Issue description mentions Revenue
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_validate_data_accuracy -v`
Expected: FAIL with "NameError: name 'validate_data_accuracy' is not defined"

- [ ] **Step 3: Write minimal implementation**

```python
# skills/financial-analysis-report/scripts/validate_report.py (insert after find_expected_value)

def validate_data_accuracy(content: str, fs_index: dict) -> List[Tuple[int, str, str]]:
    """Check numbers in report match source data.

    Args:
        content: Full report markdown content
        fs_index: Loaded fs_index.json

    Returns:
        List of (line_num, issue_description, suggestion) tuples
    """
    issues = []

    # Extract all numbers from report
    extracted = extract_numbers_from_markdown(content)

    # Group by metric (may have current/prior pairs)
    metrics_found = {}
    for num in extracted:
        # Normalize context
        metric_key = num.context.lower().strip()
        if metric_key not in metrics_found:
            metrics_found[metric_key] = []
        metrics_found[metric_key].append(num)

    # Validate each metric
    for metric_key, numbers in metrics_found.items():
        # Find expected value
        expected = find_expected_value(numbers[0].context, fs_index)

        if expected is None:
            continue  # Skip metrics we can't validate

        # Adjust for units: fs_index is in RM'000, report typically in RM million
        expected_in_millions = expected / 1000

        # Check if any extracted value matches expected (within 1% tolerance)
        matches = False
        for num in numbers:
            if values_match(num.value, expected_in_millions, tolerance_pct=0.01):
                matches = True
                break

        if not matches:
            # Report mismatch
            found_values = [n.value for n in numbers]
            issues.append((
                numbers[0].line_num,
                f"Incorrect value for '{numbers[0].context}'",
                f"Expected: {expected_in_millions:.2f}, Found: {found_values}"
            ))

    return issues


def values_match(reported: float, expected: float, tolerance_pct: float = 0.01) -> bool:
    """Check if values match within tolerance."""
    if expected == 0:
        return reported == 0
    return abs(reported - expected) / abs(expected) <= tolerance_pct
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_validate_data_accuracy -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/financial-analysis-report/scripts/validate_report.py tests/skills/financial-analysis-report/test_validate_report.py
git commit -m "feat(validation): add data accuracy validation

- Implement validate_data_accuracy() to check numbers match source
- Add values_match() helper with 1% tolerance
- Handle unit conversion (RM'000 to RM million)
- Group extracted numbers by metric
- Report mismatches with line numbers

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 5: YoY Calculation Validation

**Files:**
- Modify: `skills/financial-analysis-report/scripts/validate_report.py:150-155`
- Modify: `tests/skills/financial-analysis-report/test_validate_report.py:125-130`

- [ ] **Step 1: Write failing test for YoY calculation validation**

```python
# tests/skills/financial-analysis-report/test_validate_report.py (append)
def test_validate_yoy_calculations():
    """Test validating YoY percentage calculations."""
    from skills.financial_analysis_report.scripts.validate_report import validate_calculations

    # Correct calculation
    report = """
| Revenue | 3,252 | 2,057 | +58.1% |
"""

    issues = validate_calculations(report)

    # 58.1% is correct: (3252-2057)/2057 = 0.581 = 58.1%
    assert len(issues) == 0

    # Incorrect calculation
    bad_report = """
| Revenue | 3,252 | 2,057 | +60.0% |
"""

    issues = validate_calculations(bad_report)

    # Should catch wrong YoY%
    assert len(issues) == 1
    assert '58.1' in issues[0][2]  # Suggestion shows correct value
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_validate_yoy_calculations -v`
Expected: FAIL with "NameError: name 'validate_calculations' is not defined"

- [ ] **Step 3: Write minimal implementation**

```python
# skills/financial-analysis-report/scripts/validate_report.py (insert after validate_data_accuracy)

def validate_calculations(content: str) -> List[Tuple[int, str, str]]:
    """Verify YoY % calculations are correct.

    Looks for patterns like: | Metric | Current | Prior | +X.Y% |
    """
    issues = []
    lines = content.split('\n')

    # Pattern to match: | Metric | Current | Prior | +X.Y% |
    yoy_pattern = r'\|\s*([^|]+)\s*\|\s*([\d,]+(?:\.\d+)?)\s*\|\s*([\d,]+(?:\.\d+)?)\s*\|\s*\+?([\d.]+)%'

    for match in re.finditer(yoy_pattern, content):
        metric_name = match.group(1).strip()

        # Skip separator rows
        if metric_name.startswith('---') or not metric_name:
            continue

        try:
            current = float(match.group(2).replace(',', ''))
            prior = float(match.group(3).replace(',', ''))
            reported_yoy = float(match.group(4))

            # Skip if prior is zero (division by zero)
            if prior == 0:
                continue

            # Calculate expected YoY
            expected_yoy = ((current - prior) / prior) * 100

            # Check if reported matches calculated (within 0.2% for rounding)
            if abs(reported_yoy - expected_yoy) > 0.2:
                line_num = content[:match.start()].count('\n') + 1
                issues.append((
                    line_num,
                    f"Incorrect YoY calculation for '{metric_name}'",
                    f"Reported: {reported_yoy:.1f}%, Calculated: {expected_yoy:.1f}%"
                ))
        except (ValueError, ZeroDivisionError):
            continue

    return issues
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_validate_yoy_calculations -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/financial-analysis-report/scripts/validate_report.py tests/skills/financial-analysis-report/test_validate_report.py
git commit -m "feat(validation): add YoY calculation validation

- Implement validate_calculations() for YoY% checks
- Extract current, prior, and reported YoY from tables
- Recalculate YoY and compare with reported
- Allow 0.2% tolerance for rounding
- Report mismatches with correct calculation

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 6: Tone Validation (Aggressive Language Detection)

**Files:**
- Modify: `skills/financial-analysis-report/scripts/validate_report.py:190-195`
- Modify: `tests/skills/financial-analysis-report/test_validate_report.py:155-160`

- [ ] **Step 1: Write failing test for tone validation**

```python
# tests/skills/financial-analysis-report/test_validate_report.py (append)
def test_validate_tone():
    """Test detecting aggressive language."""
    from skills.financial_analysis_report.scripts.validate_report import validate_tone

    # Professional language
    good_report = "Revenue showed strong growth of 58% YoY."
    issues = validate_tone(good_report)
    assert len(issues) == 0

    # Aggressive language
    bad_report = "Revenue showed explosive growth of 58% YoY, while margins collapsed."
    issues = validate_tone(bad_report)

    # Should find 2 issues: 'explosive' and 'collapsed'
    assert len(issues) == 2
    assert any('explosive' in issue[1] for issue in issues)
    assert any('collapsed' in issue[1] for issue in issues)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_validate_tone -v`
Expected: FAIL with "NameError: name 'validate_tone' is not defined"

- [ ] **Step 3: Write minimal implementation**

```python
# skills/financial-analysis-report/scripts/validate_report.py (insert after validate_calculations)

def validate_tone(content: str) -> List[Tuple[int, str, str]]:
    """Check for aggressive language in report.

    Returns FORMATTING issues (not CRITICAL) - these don't block delivery.
    """
    issues = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        for word, replacement in AGGRESSIVE_WORDS.items():
            if re.search(rf'\b{word}\b', line, re.IGNORECASE):
                issues.append((
                    line_num,
                    f"Aggressive language: '{word}'",
                    f"Consider: '{replacement}'"
                ))

    return issues
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_validate_tone -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/financial-analysis-report/scripts/validate_report.py tests/skills/financial-analysis-report/test_validate_report.py
git commit -m "feat(validation): add tone validation for aggressive language

- Implement validate_tone() to detect aggressive words
- Scan report for words like 'explosive', 'collapsed', 'crisis'
- Suggest professional alternatives
- Return FORMATTING issues (non-blocking)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 7: Main Validation Function and CLI

**Files:**
- Modify: `skills/financial-analysis-report/scripts/validate_report.py:25-30`
- Modify: `tests/skills/financial-analysis-report/test_validate_report.py:180-185`

- [ ] **Step 1: Write failing test for full validation**

```python
# tests/skills/financial-analysis-report/test_validate_report.py (append)
def test_full_validation(tmp_path):
    """Test complete validation workflow."""
    from skills.financial_analysis_report.scripts.validate_report import validate_report

    # Create test files
    report = tmp_path / "test_report.md"
    report.write_text("""
| Revenue | 3,252 | 2,057 | +58.1% |
Revenue showed explosive growth.
""")

    fs_index = tmp_path / "fs_index.json"
    fs_index.write_text(json.dumps({
        'line_items': {
            'revenue': {
                'group_current': 3252347,
                'group_prior': 2057210
            }
        }
    }))

    # Run validation
    result = validate_report(report, fs_index)

    # Should have 0 CRITICAL issues (data is correct)
    assert result['total_critical'] == 0

    # Should have 1 FORMATTING issue (aggressive language)
    assert result['total_formatting'] == 1
    assert result['passed'] is True  # Formatting issues don't block
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_full_validation -v`
Expected: FAIL with "NameError: name 'validate_report' is not defined"

- [ ] **Step 3: Write minimal implementation**

```python
# skills/financial-analysis-report/scripts/validate_report.py (replace main() function)

def validate_report(report_path: Path, fs_index_path: Path, metrics_path: Optional[Path] = None) -> Dict:
    """Run all validation checks with DATA ACCURACY as priority.

    Args:
        report_path: Path to report markdown file
        fs_index_path: Path to fs_index.json (required)
        metrics_path: Path to metrics.json (optional, for enhanced validation)

    Returns:
        Dict with validation results:
        - total_critical: int (data accuracy issues - block delivery)
        - total_formatting: int (tone/formatting issues - don't block)
        - critical_issues: List of (line, desc, suggestion)
        - formatting_issues: List of (line, desc, suggestion)
        - passed: bool (True if total_critical == 0)
    """
    # Load data sources
    if not fs_index_path.exists():
        raise FileNotFoundError(f"fs_index.json not found: {fs_index_path}")

    content = report_path.read_text(encoding='utf-8')
    fs_index = json.loads(fs_index_path.read_text())

    # Run validations in PRIORITY ORDER
    critical_issues = []
    critical_issues.extend(validate_data_accuracy(content, fs_index))
    critical_issues.extend(validate_calculations(content))

    formatting_issues = []
    formatting_issues.extend(validate_tone(content))

    total_critical = len(critical_issues)
    total_formatting = len(formatting_issues)

    return {
        'path': str(report_path),
        'total_critical': total_critical,
        'total_formatting': total_formatting,
        'critical_issues': critical_issues,
        'formatting_issues': formatting_issues,
        'issues_by_category': {
            'data_accuracy': critical_issues,
            'tone': formatting_issues,
        },
        'passed': total_critical == 0,  # Fail on data issues only
    }


def print_report(results: Dict):
    """Print validation results."""
    print(f"\n{'='*70}")
    print(f"VALIDATION REPORT: {results['path']}")
    print(f"{'='*70}\n")

    if results['passed'] and results['total_formatting'] == 0:
        print("✅ PASSED - No issues found!\n")
        return

    # CRITICAL: Data Accuracy Issues
    if results['total_critical'] > 0:
        print(f"❌ CRITICAL - {results['total_critical']} DATA ACCURACY ISSUE(S):\n")
        print("These MUST be fixed before delivery:\n")
        print("-" * 70)

        for line_num, problem, detail in results['critical_issues']:
            if line_num > 0:
                print(f"Line {line_num:4d}: {problem}")
            else:
                print(f"         {problem}")
            print(f"         → {detail}\n")

    # Formatting Issues
    if results['total_formatting'] > 0:
        print(f"\n⚠️  FORMATTING - {results['total_formatting']} issue(s):\n")
        print("-" * 70)

        for line_num, problem, detail in results['formatting_issues']:
            print(f"  {problem}")
            print(f"  → {detail}\n")

    if results['passed']:
        print("\n✅ Data accuracy verified. Formatting issues can be addressed.\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate financial analysis report (DATA ACCURACY priority)'
    )
    parser.add_argument('report', type=Path, help='Path to report markdown file')
    parser.add_argument('--data', type=Path, required=True,
                       help='Path to fs_index.json (source data)')
    parser.add_argument('--metrics', type=Path,
                       help='Path to metrics.json (calculated ratios)')

    args = parser.parse_args()

    if not args.report.exists():
        print(f"Error: Report file not found: {args.report}")
        sys.exit(1)

    if not args.data.exists():
        print(f"Error: Data file not found: {args.data}")
        sys.exit(1)

    results = validate_report(args.report, args.data, args.metrics)
    print_report(results)

    # Exit with error code if critical issues found
    sys.exit(0 if results['passed'] else 1)


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py::test_full_validation -v`
Expected: PASS

- [ ] **Step 5: Run all tests to ensure everything works**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add skills/financial-analysis-report/scripts/validate_report.py tests/skills/financial-analysis-report/test_validate_report.py
git commit -m "feat(validation): complete validation script with CLI

- Implement validate_report() as main entry point
- Add print_report() for formatted output
- Separate CRITICAL (data) vs FORMATTING (tone) issues
- Return structured results dict
- Exit code 0 if passed, 1 if critical issues
- Full test coverage for validation workflow

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 8: Add CLI Wrapper to finanalysis

**Files:**
- Modify: `src/finanalysis/cli.py:500-505` (append to end)
- Test: Manual testing (CLI wrapper is trivial)

- [ ] **Step 1: Add validate-report subcommand**

```python
# src/finanalysis/cli.py (append to end of file, before if __name__ == '__main__')

@cli.command('validate-report')
@click.argument('report', type=click.Path(exists=True))
@click.option('--data', type=click.Path(exists=True), required=True,
              help='Path to fs_index.json (source data)')
@click.option('--metrics', type=click.Path(exists=True),
              help='Path to metrics.json (calculated ratios)')
@click.pass_context
def validate_report_cmd(ctx, report, data, metrics):
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
    import subprocess
    from pathlib import Path

    # Find skill directory (relative to this file)
    cli_dir = Path(__file__).parent
    skill_dir = cli_dir.parent.parent / 'skills' / 'financial-analysis-report'
    validate_script = skill_dir / 'scripts' / 'validate_report.py'

    if not validate_script.exists():
        click.echo(f"Error: Validation script not found at {validate_script}", err=True)
        click.echo("Make sure the financial-analysis-report skill is installed.", err=True)
        ctx.exit(1)

    # Build command
    cmd = [sys.executable, str(validate_script), report, '--data', data]
    if metrics:
        cmd.extend(['--metrics', metrics])

    # Run validation (forward exit code)
    result = subprocess.run(cmd)
    ctx.exit(result.returncode)
```

- [ ] **Step 2: Test CLI wrapper manually**

Run: `finanalysis validate-report --help`
Expected: Shows help text for validate-report command

Run: `finanalysis validate-report sample-report/CHINHIN-2024-revised.md --data output/CHINHIN/2024/fs_index.json`
Expected: Validation runs (may fail if files don't exist, that's OK for now)

- [ ] **Step 3: Commit**

```bash
git add src/finanalysis/cli.py
git commit -m "feat(cli): add validate-report command

- Add thin CLI wrapper for validate_report.py script
- Forward arguments to skill script via subprocess
- Return skill script exit code (0=pass, 1=critical issues)
- Provide clear error if skill not installed

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Chunk 3: Worker Instruction Updates (Phase 2)

### Task 9: Expand Writing Standards

**Files:**
- Modify: `skills/financial-analysis-report/references/writing_standards.md` (append sections)

- [ ] **Step 1: Add Professional Tone Standards section**

```markdown
<!-- Append to skills/financial-analysis-report/references/writing_standards.md -->

## Professional Tone Standards

**DO use measured language:**
- ✅ "Revenue increased 58% YoY" (factual)
- ✅ "Margin expansion suggests improved efficiency" (interpretive)
- ✅ "Cash generation weakened" (clear but professional)

**DON'T use aggressive language:**
- ❌ "Explosive scale expansion" → "Strong revenue growth"
- ❌ "Margin collapsed" → "Margin declined significantly"
- ❌ "Crisis in cash flow" → "Cash conversion challenges"
- ❌ "Profitability skyrocketed" → "Profitability improved materially"

**Why it matters:** Institutional investors value measured, evidence-based analysis over sensational language.

## Data Presentation Standards

### Handling Missing Data

**Problem:** Some metrics may not be disclosed in available financial statements.

**❌ DON'T:**
```markdown
| Metric | FY2024 | FY2023 |
|---|---:|---:|
| Segment margin | N/A | N/A |
```

**✅ DO:**
```markdown
| Metric | FY2024 | FY2023 |
|---|---:|---:|
| Segment margin | - | - |

*Note: Segment-level margins not disclosed in available statements*
```

### Currency Formatting

**Standard:** Use "RM" (Ringgit Malaysia) throughout, not "MYR"

**✅ ALWAYS:**
- Table headers: "| Revenue (RM million) | 3,252 | 2,057 |"
- Inline text: "Revenue grew to RM3.25 billion"
- Consistency: Never mix RM and MYR in same report

### Basis Points Notation

**Rule:**
- Use "bps" (basis points) for changes < 100 basis points (1%)
- Use "ppt" (percentage points) for changes ≥ 100 basis points

**Examples:**
- ✅ "Gross margin improved 699bps" (not "6.99%")
- ✅ "PBT margin declined 72bps" (not "0.72%")
- ✅ "Attributable margin declined 12.16ppt" (not "12.16%")

**Why:** Basis points are standard in financial analysis for small changes. Using them shows professionalism.

### Negative Values in Tables

**Standard:** Use parentheses notation for negative values

**✅ DO:**
```markdown
| Cash flow from financing | (2,544) | 437 |
```

**❌ DON'T:**
```markdown
| Cash flow from financing | -2,544 | 437 |
```
```

- [ ] **Step 2: Verify formatting**

Run: `cat skills/financial-analysis-report/references/writing_standards.md | head -50`
Expected: See new sections appended

- [ ] **Step 3: Commit**

```bash
git add skills/financial-analysis-report/references/writing_standards.md
git commit -m "docs(standards): add professional tone and data presentation standards

- Add Professional Tone Standards section with DO/DON'T examples
- Add Data Presentation Standards for missing data, currency, basis points
- Include concrete examples for each standard
- Explain why standards matter for institutional investors

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 10: Create Tone Guidelines Document

**Files:**
- Create: `skills/financial-analysis-report/references/tone_guidelines.md`

- [ ] **Step 1: Create comprehensive tone guidelines**

```markdown
# Professional Tone Guidelines for Financial Analysis

## Philosophy

**Write for institutional investors: clear, measured, evidence-based.**

Your readers are professional investors who value:
1. Accuracy over drama
2. Evidence over hyperbole
3. Measured language over aggressive claims
4. Professional tone that builds credibility

---

## Language Classification

### ✅ Professional Language (Use These)

**Growth & Improvement:**
- "Strong revenue growth" (not "explosive")
- "Margin expanded significantly" (not "surged dramatically")
- "Profitability improved materially" (not "skyrocketed")
- "Performance exceeded expectations" (not "blew past estimates")

**Decline & Deterioration:**
- "Cash generation weakened" (not "collapsed")
- "Attribution quality deteriorated" (not "collapsed")
- "Leverage increased" (not "ballooned")
- "Margin declined significantly" (not "plummeted")

**Risk & Challenges:**
- "Cash conversion challenges" (not "crisis")
- "Liquidity pressure" (not "disaster")
- "Execution risk" (not "catastrophic failure")
- "Headwinds" (not "devastating blow")

### ⚠️ Caution - Use Sparingly

Only use these for exceptional circumstances:

- "Exceptional growth" → Only for >50% YoY
- "Dramatic improvement" → Only for >100% YoY
- "Material deterioration" → Only for >20% decline
- "Substantial headwinds" → Only when multiple factors align

### ❌ Avoid - Too Aggressive

Never use these words:

**Explosive/Skyrocket Group:**
- "Explosive", "skyrocketed", "surged dramatically", "ballooned"
- **Why:** Sounds like marketing hype, not professional analysis

**Collapse/Plummet Group:**
- "Collapsed", "plummeted", "cratered", "tanked"
- **Why:** Too emotional, undermines credibility

**Crisis/Disaster Group:**
- "Crisis", "disaster", "catastrophic", "devastating", "hemorrhaged"
- **Why:** Alarmist, suggests company is failing when it may just be facing challenges

---

## Tone by Section

### Executive Summary (Most Measured)
- **Tone:** Balanced, factual, highlights both strengths and concerns
- **Example:** "Strong revenue growth (+58% YoY) was partially offset by margin dilution from new market expansion"

### Core Conclusions (Confident but Evidence-Based)
- **Tone:** Clear judgments backed by data
- **Example:** "Margin expansion reflects improved operating leverage, though sustainability requires monitoring"

### Risk Warning (Direct but Not Alarmist)
- **Tone:** Matter-of-fact, specific, actionable
- **Example:** "Leverage increased to 65% debt-to-assets, approaching typical covenant thresholds of 70%"
- **NOT:** "Leverage crisis threatens company survival"

---

## Examples: Before & After

### Example 1: Revenue Growth

**Before (too aggressive):**
> "Explosive scale expansion: Revenue +58.1% YoY, largest growth in recent years, demonstrating market dominance"

**After (professional):**
> "Strong revenue growth: Revenue +58.1% YoY to RM3.25b, driven by construction recovery and East Malaysia expansion, with market share gains in key segments"

**What changed:**
- "Explosive scale expansion" → "Strong revenue growth"
- "Market dominance" → "Market share gains" (more precise)
- Added specific drivers (construction recovery, East Malaysia)

### Example 2: Margin Decline

**Before (too aggressive):**
> "Attributable margin collapsed from 37.06% to 24.90% despite PAT growth, eroding shareholder value"

**After (professional):**
> "Attributable margin declined from 37.06% to 24.90% despite PAT growth, indicating rising minority interests from JVs eroding shareholder value"

**What changed:**
- "Collapsed" → "Declined" (measured)
- "Eroding shareholder value" → "Indicating rising minority interests eroding shareholder value" (more precise, explanatory)

### Example 3: Cash Flow

**Before (too aggressive):**
> "Crisis in cash conversion: OCF negative RM60m despite PAT of RM215m, indicating broken business model"

**After (professional):**
> "Cash conversion challenges: OCF negative RM60m despite PAT of RM215m, reflecting working capital absorption from rapid East Malaysia expansion"

**What changed:**
- "Crisis" → "Challenges" (not alarmist)
- "Broken business model" → "Working capital absorption from expansion" (explains root cause, not judgmental)

---

## Quick Reference: Word Replacements

| ❌ Avoid | ✅ Use Instead |
|---|---|
| Explosive | Strong, significant, material |
| Collapsed | Declined significantly, deteriorated |
| Crisis | Challenge, pressure, stress |
| Skyrocketed | Increased significantly, surged |
| Plummeted | Declined sharply, fell significantly |
| Ballooned | Expanded significantly, increased substantially |
| Hemorrhaged | Declined, deteriorated |
| Catastrophic | Severe, material, significant |
| Disaster | Significant challenge, major issue |
| Devastating | Severe, material |

---

## Testing Your Tone

Before submitting, ask yourself:

1. **Would an institutional investor say this sounds professional?**
2. **Am I using evidence to support claims, or just being dramatic?**
3. **Is my language measured, or am I over-hyping/sensationalizing?**
4. **Would I be embarrassed if the company's CEO read this?**

If unsure, err on the side of being **more measured**.
```

- [ ] **Step 2: Verify file created**

Run: `ls -la skills/financial-analysis-report/references/tone_guidelines.md`
Expected: File exists with content

- [ ] **Step 3: Commit**

```bash
git add skills/financial-analysis-report/references/tone_guidelines.md
git commit -m "docs(guidelines): create comprehensive tone guidelines

- Add language classification (Professional/Caution/Avoid)
- Provide tone guidance by section type
- Include Before & After examples with explanations
- Add quick reference word replacement table
- Include self-test questions for workers

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

*Note: Due to token limits, I'll save this plan in chunks. Let me write the first part and continue...*
