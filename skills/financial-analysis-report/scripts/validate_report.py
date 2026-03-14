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
    metrics_found = {}
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
