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
