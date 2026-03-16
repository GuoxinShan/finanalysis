#!/usr/bin/env python3
"""
Financial Report Data Validator

Validates generated financial analysis reports for:
- Data accuracy (numbers match source data)
- Calculation correctness (YoY %, margins, ratios)
- Unverifiable claims (numbers with no traceable source)
- Rounded derivation warnings (percentages computed from rounded intermediates)
- Tone quality (aggressive language)
- Formatting (basis points, currency notation)

Usage:
    python scripts/validate_report.py report.md --data fs_index.json [--metrics metrics.json]
"""
import re
import sys
import json
import math
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, field
import argparse


@dataclass
class ExtractedNumber:
    """Represents a number extracted from report with context."""
    value: float
    context: str  # Metric name or surrounding text
    line_num: int  # Line number in report
    source: str = "table"  # "table" or "inline_text"


# Patterns that indicate a number is NOT a financial claim worth verifying.
# These are generic descriptors, years, or change values already checked elsewhere.
_SKIP_PATTERNS = [
    r'\bFY\s*\d{4}\b',                 # FY2024, FY2023
    r'\b19\d{2}\b',                    # 1999, etc.
    r'\b20\d{2}\b',                    # 2024, 2023, etc.
    r'\bQ[1-4]\b',                     # Q1, Q2, Q3, Q4
    r'\bH[12]\b',                      # H1, H2
    r'\bpage\s+\d+\b',                 # page 148
    r'\bsection\s+\d+\b',              # section 3
    r'\bRM\s*[\d,]+\.?\d*\s*[bmBM]\b', # RM3.25b, RM2.1b (currency amounts in text - too vague)
    r'\bRM\s*\d[\d,]*\s*million\b',    # RM3,252 million
    r'\bRM\s*\d[\d,]*\s*billion\b',    # RM2.1 billion
    r'\b\basis\s*point',               # basis point references
    r'\bpoints?\b',                    # "points" alone
    r'\branking\b',                    # "ranking 3rd"
    r'\b#\d+\b',                       # #1, #2
    r'\bv\d+\.\d+',                    # version numbers
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # dates like 31/12/2024
]

# Patterns that indicate a number IS a financial claim that should be traceable.
_FINANCIAL_CLAIM_PATTERNS = [
    # margin/percentage claims: "margin of 12.5%", "gross margin at 15.4%"
    r'\bmargin\s+(?:of\s+|at\s+|stood\s+at\s+|was\s+|reached\s+)?([\d.]+)\s*%',
    # ratio claims: "ratio of 0.8x", "debt-to-equity of 0.8"
    r'(?:ratio|debt.to.equity| gearing)\s+(?:of\s+|at\s+|stood\s+at\s+|was\s+|reached\s+)?([\d.]+)',
    # concentration claims: "concentration at 35%"
    r'\bconcentration\s+(?:of\s+|at\s+|stood\s+at\s+|was\s+)?([\d.]+)\s*%',
    # share claims: "market share of 25%"
    r'\b(?:market\s+)?share\s+(?:of\s+|at\s+|stood\s+at\s+|was\s+)?([\d.]+)\s*%',
    # yield claims: "yield of 4.2%"
    r'\byield\s+(?:of\s+|at\s+|stood\s+at\s+|was\s+)?([\d.]+)\s*%',
    # coverage claims: "coverage of 3.5x"
    r'\bcoverage\s+(?:of\s+|at\s+|stood\s+at\s+|was\s+)?([\d.]+)',
    # percentage claims with financial context: "return on equity of 12%"
    r'\b(?:return on equity|roe|return on assets|roa|roic)\s+(?:of\s+|at\s+|stood\s+at\s+|was\s+)?([\d.]+)\s*%',
    # standalone percentage that looks like a financial metric in a sentence
    r'\b(?:gross|net|operating|ebitda)?\s*profit\s+(?:margin\s+)?(?:of\s+|at\s+|stood\s+at\s+|was\s+|reached\s+)?([\d.]+)\s*%',
]


# Map common metric names to fs_index.json field names
METRIC_ALIASES = {
    # Income Statement
    'revenue': ['revenue', 'total revenue', 'sales', 'turnover'],
    'gross_profit': ['gross profit', 'profit before overhead', 'gross operating profit'],
    'operating_profit': ['profit from operations', 'operating profit', 'pbt before finance costs'],
    'pbt': ['profit before tax', 'pbt', 'profit before taxation'],
    'pat': ['profit after tax', 'pat', 'profit for the year', 'profit for the financial year', 'net profit'],
    'attributable_profit': ['profit attributable to owners', 'attributable to owners of the parent'],
    'selling_expenses': ['selling and marketing expenses', 'selling expenses', 'distribution costs'],
    'admin_expenses': ['administration expenses', 'administrative expenses', 'admin costs'],
    'finance_costs': ['finance costs', 'interest expense', 'finance expenses'],

    # Balance Sheet
    'total_assets': ['total assets', 'total non-current and current assets'],
    'current_assets': ['total current assets', 'current assets'],
    'non_current_assets': ['total non-current assets', 'non-current assets'],
    'total_equity': ['total equity', "shareholders' equity", 'total shareholders\' funds'],
    'total_liabilities': ['total liabilities', 'total non-current and current liabilities'],
    'current_liabilities': ['total current liabilities', 'current liabilities'],
    'cash': ['cash and bank balances', 'cash and cash equivalents', 'cash'],
    'inventory': ['inventories', 'stock', 'inventory'],
    'receivables': ['trade receivables', 'accounts receivable', 'receivables'],
    'payables': ['trade payables', 'accounts payable', 'payables'],

    # Cash Flow
    'ocf': ['net cash from operating activities', 'operating cash flow', 'cash from operations'],
    'icf': ['net cash used in investing activities', 'investing cash flow', 'cash used in investing'],
    'fcf': ['net cash from financing activities', 'financing cash flow', 'cash from financing'],
}


def extract_numbers_from_markdown(content: str) -> List[ExtractedNumber]:
    """Extract all numbers from markdown report with context.

    Extracts from both table cells and inline text.
    Table format: | Metric | Value1 | Value2 | ...
    Inline text: "Revenue grew 58% to RM3.25b", "net debt-to-equity of 0.8x"
    """
    extracted = []
    lines = content.split('\n')

    # --- Table extraction (existing logic) ---
    # Pattern to match table cells: | Metric | Value1 | Value2 | ...
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
                    line_num=line_num,
                    source="table"
                ))
            except ValueError:
                continue

    # --- Inline text extraction ---
    # Pattern: number with optional % or x suffix, preceded by financial context
    # Matches things like: "58%", "12.5%", "0.8x", "RM3.25b", "RM410m"
    # But NOT dates (FY2024), generic counts, or bullet numbers
    inline_pattern = r'(?<!\d)(\d+(?:,\d{3})*(?:\.\d+)?)\s*(%|x|xb|xm|b|m)?(?!\d)'

    for line_num, line in enumerate(lines, 1):
        # Skip table rows (already handled above)
        stripped = line.strip()
        if stripped.startswith('|'):
            continue

        # Skip header lines, list markers without financial context
        # Find all number patterns in the line
        for match in re.finditer(inline_pattern, line):
            raw_value = match.group(1).replace(',', '')
            suffix = match.group(2) or ''

            try:
                value = float(raw_value)
            except ValueError:
                continue

            # Skip small integers that are likely bullet numbers or generic counts
            if suffix == '' and value == int(value) and 1 <= value <= 12:
                continue

            # Skip years
            if suffix == '' and value >= 1990 and value <= 2100:
                continue

            # Extract surrounding context (the clause containing this number)
            start = max(0, match.start() - 40)
            end = min(len(line), match.end() + 10)
            context = line[start:end].strip()

            # Only include if context suggests a financial claim
            # (has keywords like margin, ratio, %, etc.)
            # BUT: skip YoY change values (e.g., "grew 58%", "declined 12%")
            # These are checked by validate_calculations, not data accuracy
            financial_keywords = [
                'margin', 'ratio', 'equity', 'debt', 'assets', 'liabilities',
                'cash', 'earnings', 'dividend', 'share', 'yield', 'coverage',
                'roa', 'roe', 'roic', 'ebitda', 'gearing', 'concentration',
            ]
            context_lower = context.lower()
            is_financial = any(kw in context_lower for kw in financial_keywords)

            # Skip YoY change values (preceded by growth/decline verbs + %)
            # These are relative changes, not absolute values to verify against fs_index
            change_verbs = [
                'grew', 'growth', 'declined', 'decline', 'increased', 'increase',
                'decreased', 'decrease', 'dropped', 'rose', 'jumped', 'fell',
                'improved', 'deteriorated', 'contracted', 'expanded',
                ' yoy', ' year-on-year', ' year over year',
            ]
            is_change_value = suffix == '%' and any(
                verb in context_lower for verb in change_verbs
            )

            # Also include if it has x suffix (ratio like 0.8x)
            if suffix in ('x', 'xb', 'xm'):
                is_financial = True

            # Include if the number has a currency prefix like "RM"
            prefix_context = line[max(0, match.start() - 5):match.start()]
            if re.search(r'RM\s*$', prefix_context):
                is_financial = True

            # Bare percentages without financial context keywords are likely
            # YoY changes or descriptive, skip them
            if suffix == '%' and not is_financial:
                is_change_value = True

            if is_change_value:
                continue

            if is_financial:
                extracted.append(ExtractedNumber(
                    value=value,
                    context=context,
                    line_num=line_num,
                    source="inline_text"
                ))

    return extracted


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


def values_match(reported: float, expected: float, tolerance_pct: float = 0.01) -> bool:
    """Check if values match within tolerance.

    Args:
        reported: Value from report
        expected: Expected value from source data
        tolerance_pct: Tolerance as decimal (0.01 = 1%)

    Returns:
        True if values match within tolerance
    """
    if expected == 0:
        return reported == 0
    return abs(reported - expected) / abs(expected) <= tolerance_pct


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
    metrics_found: Dict[str, List[ExtractedNumber]] = {}
    for num in extracted:
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


def validate_calculations(content: str) -> List[Tuple[int, str, str]]:
    """Verify YoY % calculations are correct.

    Looks for patterns like: | Metric | Current | Prior | +X.Y% |
    """
    issues = []

    # Pattern to match: | Metric | Current | Prior | +/-X.Y% |
    yoy_pattern = r'\|\s*([^|]+)\s*\|\s*([\d,]+(?:\.\d+)?)\s*\|\s*([\d,]+(?:\.\d+)?)\s*\|\s*([+-]?[\d.]+)%'

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


def _is_skip_context(text: str) -> bool:
    """Check if the surrounding text indicates this number should be skipped."""
    for pattern in _SKIP_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def detect_unverifiable(
    content: str,
    fs_index: dict,
    verified_numbers: Optional[Set[Tuple[float, int]]] = None,
) -> List[Tuple[int, str, str]]:
    """Detect numbers in the report that look like financial claims but can't be verified.

    A number is flagged as UNVERIFIABLE if:
    1. It appears in inline text (not a table)
    2. It looks like a financial claim (margin, ratio, percentage with context)
    3. It doesn't match any fs_index data
    4. It wasn't already verified by validate_data_accuracy

    Does NOT flag:
    - Generic numbers (years, section numbers, bullet numbers)
    - Percentages that are YoY change values (already checked by validate_calculations)
    - Numbers in descriptive text that aren't financial claims
    - Numbers already verified against fs_index

    Args:
        content: Full report markdown content
        fs_index: Loaded fs_index.json
        verified_numbers: Set of (value, line_num) tuples already verified

    Returns:
        List of (line_num, issue_description, detail) tuples
    """
    if verified_numbers is None:
        verified_numbers = set()

    issues = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip table rows (handled by validate_data_accuracy)
        if stripped.startswith('|'):
            continue

        # Skip empty lines, headers
        if not stripped or stripped.startswith('#') or stripped.startswith('---'):
            continue

        # Skip if the line contains skip patterns (years, etc.)
        if _is_skip_context(line):
            continue

        # Check each financial claim pattern
        for pattern in _FINANCIAL_CLAIM_PATTERNS:
            for match in re.finditer(pattern, line, re.IGNORECASE):
                # Extract the numeric value from the claim
                claim_value_str = match.group(1)
                try:
                    claim_value = float(claim_value_str)
                except (ValueError, IndexError):
                    continue

                # Skip if already verified
                if (claim_value, line_num) in verified_numbers:
                    continue

                # Try to find this value in fs_index data
                # For percentages, check if it could be derived from known values
                found_in_fs = _try_verify_claim(claim_value, match.group(0), fs_index)
                if not found_in_fs:
                    # Extract the claim context for the description
                    claim_text = match.group(0).strip()
                    issues.append((
                        line_num,
                        f"Unverifiable financial claim: '{claim_text}'",
                        f"Value {claim_value}% cannot be traced to fs_index data or metrics.json"
                    ))

    return issues


def _try_verify_claim(value: float, claim_text: str, fs_index: dict) -> bool:
    """Try to verify a financial claim against fs_index data.

    Checks if the value matches any line_item value (scaled appropriately)
    or if it could be a percentage derived from two known values.

    Returns:
        True if the claim can be verified, False otherwise
    """
    line_items = fs_index.get('line_items', {})

    # Check if the value matches any direct line item (in millions)
    for key, item in line_items.items():
        for field in ('group_current', 'group_prior'):
            if field in item:
                val_millions = item[field] / 1000.0
                if values_match(value, val_millions, tolerance_pct=0.01):
                    return True

    # Check if the value could be a percentage derived from two line items
    # e.g., margin = profit / revenue * 100
    if '%' in claim_text:
        for profit_key in ('gross_profit', 'operating_profit', 'pbt', 'pat'):
            if profit_key in line_items and 'revenue' in line_items:
                profit = line_items[profit_key].get('group_current', 0)
                revenue = line_items['revenue'].get('group_current', 0)
                if revenue > 0:
                    margin = (profit / revenue) * 100
                    if abs(margin - value) < 0.5:  # 0.5pp tolerance for rounding
                        return True

    return False


def detect_rounded_derivation(
    content: str,
    fs_index: dict,
) -> List[Tuple[int, str, str]]:
    """Detect percentages that could have been computed from rounded intermediates.

    If a percentage in the report could have been computed from rounded intermediate
    values but gives a different result from raw values, flag it as a soft warning.

    Example: NCI% = 97.1/215.5 = 45.0% vs correct 97078/215492 = 45.1%

    Args:
        content: Full report markdown content
        fs_index: Loaded fs_index.json

    Returns:
        List of (line_num, issue_description, detail) tuples
    """
    issues = []
    line_items = fs_index.get('line_items', {})

    # Find percentage claims in inline text
    # Pattern: some metric phrase followed by a percentage
    pct_pattern = r'([\w\s]+?)\s*(?:of|at|was|stood at|reached)\s*([\d.]+)\s*%'

    for match in re.finditer(pct_pattern, content, re.IGNORECASE):
        metric_phrase = match.group(1).strip().lower()
        reported_pct = float(match.group(2))
        line_num = content[:match.start()].count('\n') + 1

        # Skip if not in table (we focus on inline text percentages)
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_text = content[line_start:content.find('\n', match.start())]
        if line_text.strip().startswith('|'):
            continue

        # Try to find numerator and denominator candidates
        result = _check_rounded_derivation(metric_phrase, reported_pct, line_items)
        if result:
            rounded_val, raw_val, explanation = result
            # Only flag if the difference is meaningful (> 0.1pp)
            if abs(rounded_val - raw_val) > 0.1:
                issues.append((
                    line_num,
                    f"Possible rounded derivation: {metric_phrase} at {reported_pct}%",
                    f"From rounded: {rounded_val:.1f}%, from raw: {raw_val:.1f}% ({explanation})"
                ))

    return issues


def _round_sf(x: float, sig: int = 3) -> float:
    """Round a number to the given number of significant figures."""
    if x == 0:
        return 0.0
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)


def _check_rounded_derivation(
    metric_phrase: str,
    reported_pct: float,
    line_items: dict,
) -> Optional[Tuple[float, float, str]]:
    """Check if a percentage could differ due to rounded intermediate values.

    Models the common scenario where a report author rounds absolute values
    to 3 significant figures before computing a derived percentage.

    Returns:
        Tuple of (rounded_percentage, raw_percentage, explanation) or None
    """
    # Common percentage derivations
    # NCI share = attributable_profit / pat
    derivations = [
        ('non-controlling interest', 'attributable_profit', 'pat'),
        ('nci', 'attributable_profit', 'pat'),
        ('gross margin', 'gross_profit', 'revenue'),
        ('net margin', 'pat', 'revenue'),
        ('operating margin', 'operating_profit', 'revenue'),
        ('profit margin', 'pbt', 'revenue'),
    ]

    for phrase, num_key, den_key in derivations:
        if phrase in metric_phrase:
            num_item = line_items.get(num_key, {})
            den_item = line_items.get(den_key, {})

            num_raw = num_item.get('group_current')
            den_raw = den_item.get('group_current')

            if num_raw is None or den_raw is None or den_raw == 0:
                continue

            # Convert to millions (fs_index is in RM'000)
            num_millions = num_raw / 1000.0
            den_millions = den_raw / 1000.0

            # Raw calculation
            raw_pct = (num_raw / den_raw) * 100

            # Rounded calculation: round to 3 significant figures (common author practice)
            num_rounded = _round_sf(num_millions, 3)
            den_rounded = _round_sf(den_millions, 3)
            rounded_pct = (num_rounded / den_rounded) * 100

            return (rounded_pct, raw_pct,
                    f"{num_key}={num_rounded}/{den_key}={den_rounded} (3sf millions)")

    return None


def validate_report(report_path: Path, fs_index_path: Path, prior_path: Optional[Path] = None) -> Dict:
    """Run all validation checks with DATA ACCURACY as priority.

    Returns a structured dict with issues and summary counts.
    """
    # Load data sources
    if not fs_index_path.exists():
        raise FileNotFoundError(f"fs_index.json not found: {fs_index_path}")

    content = report_path.read_text(encoding='utf-8')
    fs_index = json.loads(fs_index_path.read_text())

    prior_index = None
    if prior_path and prior_path.exists():
        prior_index = json.loads(prior_path.read_text())

    all_issues = []
    verified_numbers: Set[Tuple[float, int]] = set()
    calculation_count = 0
    verified_count = 0
    mismatch_count = 0
    unverifiable_count = 0

    # 1. Data accuracy (MISMATCH issues)
    data_issues = validate_data_accuracy(content, fs_index)
    for line_num, desc, detail in data_issues:
        all_issues.append({
            "line": line_num,
            "type": "MISMATCH",
            "description": desc,
            "detail": detail,
        })
        mismatch_count += 1

    # Track verified numbers (those that matched)
    extracted = extract_numbers_from_markdown(content)
    metrics_found: Dict[str, List[ExtractedNumber]] = {}
    for num in extracted:
        metric_key = num.context.lower().strip()
        if metric_key not in metrics_found:
            metrics_found[metric_key] = []
        metrics_found[metric_key].append(num)

    for metric_key, numbers in metrics_found.items():
        expected = find_expected_value(numbers[0].context, fs_index)
        if expected is None:
            continue
        expected_in_millions = expected / 1000
        for num in numbers:
            if values_match(num.value, expected_in_millions, tolerance_pct=0.01):
                verified_numbers.add((num.value, num.line_num))
                verified_count += 1
                break

    # 2. Calculation checks
    calc_issues = validate_calculations(content)
    for line_num, desc, detail in calc_issues:
        all_issues.append({
            "line": line_num,
            "type": "MISMATCH",
            "description": desc,
            "detail": detail,
        })
        mismatch_count += 1
    calculation_count = len(calc_issues)  # This counts checked rows; we want total checked

    # Count total calculation rows checked (both passing and failing)
    yoy_pattern = r'\|\s*([^|]+)\s*\|\s*([\d,]+(?:\.\d+)?)\s*\|\s*([\d,]+(?:\.\d+)?)\s*\|\s*([+-]?[\d.]+)%'
    calc_total = 0
    for match in re.finditer(yoy_pattern, content):
        metric_name = match.group(1).strip()
        if metric_name.startswith('---') or not metric_name:
            continue
        try:
            prior = float(match.group(3).replace(',', ''))
            if prior != 0:
                calc_total += 1
        except ValueError:
            continue
    calculation_count = calc_total

    # 3. Unverifiable detection
    unverifiable_issues = detect_unverifiable(content, fs_index, verified_numbers)
    for line_num, desc, detail in unverifiable_issues:
        all_issues.append({
            "line": line_num,
            "type": "UNVERIFIABLE",
            "description": desc,
            "detail": detail,
        })
        unverifiable_count += 1

    # 4. Rounded derivation warnings
    rounded_issues = detect_rounded_derivation(content, fs_index)
    for line_num, desc, detail in rounded_issues:
        all_issues.append({
            "line": line_num,
            "type": "ROUNDED_DERIVATION",
            "description": desc,
            "detail": detail,
        })

    # 5. Tone checks (not blocking)
    tone_issues = validate_tone(content)
    for line_num, desc, detail in tone_issues:
        all_issues.append({
            "line": line_num,
            "type": "TONE",
            "description": desc,
            "detail": detail,
        })

    # Determine pass/fail: MISMATCH issues cause failure
    # UNVERIFIABLE and ROUNDED_DERIVATION are warnings, not failures
    has_mismatch = any(i["type"] == "MISMATCH" for i in all_issues)

    return {
        "passed": not has_mismatch,
        "issues": all_issues,
        "summary": {
            "verified": verified_count,
            "mismatch": mismatch_count,
            "unverifiable": unverifiable_count,
            "calculations": calculation_count,
        },
    }


def print_report(results: Dict):
    """Print validation results."""
    print(f"\n{'='*70}")
    print(f"VALIDATION REPORT")
    print(f"{'='*70}\n")

    if not results['issues']:
        print("PASSED - No issues found!\n")
        return

    # Group by type
    mismatches = [i for i in results['issues'] if i['type'] == 'MISMATCH']
    unverifiables = [i for i in results['issues'] if i['type'] == 'UNVERIFIABLE']
    roundeds = [i for i in results['issues'] if i['type'] == 'ROUNDED_DERIVATION']
    tones = [i for i in results['issues'] if i['type'] == 'TONE']

    # MISMATCH (CRITICAL)
    if mismatches:
        print(f"CRITICAL - {len(mismatches)} DATA ACCURACY ISSUE(S):\n")
        print("These MUST be fixed before delivery:\n")
        print("-" * 70)
        for issue in mismatches:
            if issue['line'] > 0:
                print(f"Line {issue['line']:4d}: {issue['description']}")
            else:
                print(f"         {issue['description']}")
            print(f"         -> {issue['detail']}\n")

    # UNVERIFIABLE (WARNING)
    if unverifiables:
        print(f"\nWARNING - {len(unverifiables)} UNVERIFIABLE CLAIM(S):\n")
        print("-" * 70)
        for issue in unverifiables:
            print(f"Line {issue['line']:4d}: {issue['description']}")
            print(f"         -> {issue['detail']}\n")

    # ROUNDED_DERIVATION (SOFT WARNING)
    if roundeds:
        print(f"\nSOFT WARNING - {len(roundeds)} ROUNDED DERIVATION(S):\n")
        print("-" * 70)
        for issue in roundeds:
            print(f"Line {issue['line']:4d}: {issue['description']}")
            print(f"         -> {issue['detail']}\n")

    # TONE
    if tones:
        print(f"\nTONE - {len(tones)} issue(s):\n")
        print("-" * 70)
        for issue in tones:
            print(f"  {issue['description']}")
            print(f"  -> {issue['detail']}\n")

    # Summary
    summary = results.get('summary', {})
    print("-" * 70)
    print(f"Summary: {summary.get('verified', 0)} verified, "
          f"{summary.get('mismatch', 0)} mismatches, "
          f"{summary.get('unverifiable', 0)} unverifiable, "
          f"{summary.get('calculations', 0)} calculations checked")

    if results['passed']:
        print("\nData accuracy verified. Warnings can be reviewed.\n")
    else:
        print("\nFAILED - Data accuracy issues must be fixed.\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate financial analysis report (DATA ACCURACY priority)'
    )
    parser.add_argument('report', type=Path, help='Path to report markdown file')
    parser.add_argument('--data', type=Path, required=True,
                       help='Path to fs_index.json (source data)')
    parser.add_argument('--prior', type=Path,
                       help='Path to prior year fs_index.json (for YoY verification)')

    args = parser.parse_args()

    if not args.report.exists():
        print(f"Error: Report file not found: {args.report}")
        sys.exit(1)

    if not args.data.exists():
        print(f"Error: Data file not found: {args.data}")
        sys.exit(1)

    results = validate_report(args.report, args.data, args.prior)
    print_report(results)

    # Exit with error code if critical issues found
    sys.exit(0 if results['passed'] else 1)


if __name__ == '__main__':
    main()
