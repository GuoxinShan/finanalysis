#!/usr/bin/env python3
"""
Assemble worker outputs into final report in correct section order.

This script reads all worker output files and combines them into the final
9-section financial analysis report in the correct order.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional


def assemble_report(workspace_dir: str, output_path: str, company_name: str = "Company", period: str = "FY2024"):
    """
    Read worker outputs and assemble final report.

    Args:
        workspace_dir: Directory containing worker output files
        output_path: Path to write the final report
        company_name: Company name for report title
        period: Period for report title (e.g., "FY2024")
    """
    workspace = Path(workspace_dir)

    # Section order mapping - Worker outputs to final report order
    # Worker 1: Section I
    # Worker 2: Sections II-III
    # Worker 3: Section IV
    # Worker 4: Sections V, VII
    # Worker 5: Section VI
    # Worker 6: Sections VIII-IX

    # Read all worker files
    worker_files = {}
    for i in range(1, 7):
        filename = f'worker_{i}_sections.md'
        filepath = workspace / filename
        if filepath.exists():
            worker_files[i] = filepath.read_text()

    # Build final report in correct section order
    section_order = [
        (1, 'I',        'Worker 1'),
        (2, 'II-III',   'Worker 2'),
        (3, 'IV',       'Worker 3'),
        (4, 'V, VII',   'Worker 4'),
        (5, 'VI',       'Worker 5'),
        (6, 'VIII-IX',  'Worker 6'),
    ]

    final_report = []
    final_report.append(f"# Financial Analysis Report: {company_name} - {period}\n\n")
    final_report.append("---\n\n")

    sections_found = []
    sections_missing = []

    for worker_id, sections, description in section_order:
        content = worker_files.get(worker_id, '')
        found = worker_id in worker_files

        if found and content.strip():
            final_report.append(content)
            final_report.append("\n\n---\n\n")
            sections_found.append(sections)
        else:
            sections_missing.append(sections)
            print(f"⚠️  Warning: Worker {worker_id} output not found (Sections {sections})")

    # Write final report
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(''.join(final_report))

    # Summary
    print(f"\n✅ Report assembled: {output_path}")
    print(f"\n📊 Sections included:")
    for s in sections_found:
        print(f"  ✓ Sections {s}")
    if sections_missing:
        print(f"\n⚠️  Sections missing:")
        for s in sections_missing:
            print(f"  ✗ Sections {s}")

    return output_file


def main():
    """CLI interface for report assembly."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Assemble worker outputs into final financial analysis report"
    )
    parser.add_argument(
        "workspace_dir",
        help="Directory containing worker output files"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for final report (e.g., CHINHIN-2024-revised.md)"
    )
    parser.add_argument(
        "--company",
        default="Company",
        help="Company name for report title"
    )
    parser.add_argument(
        "--period",
        default="FY2024",
        help="Period for report title (e.g., FY2024)"
    )

    args = parser.parse_args()

    assemble_report(
        workspace_dir=args.workspace_dir,
        output_path=args.output,
        company_name=args.company,
        period=args.period
    )


if __name__ == "__main__":
    main()
