#!/usr/bin/env python3
"""
Assemble worker outputs into final report in correct section order.

This script reads all worker output files and combines them into the final
9-section financial analysis report in the correct order.

Section order: I, II-III, IV, V, VI, VII, VIII-IX
Worker files:  worker_1_sections.md, worker_2_sections.md, worker_3_sections.md,
             worker_4_sections_v.md, worker_5_sections.md, worker_4_sections_vii.md,
             worker_6_sections.md
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional


def assemble_report(workspace_dir: str, output_path: str, company_name: str = "Company", period: str = "FY2024"):
    """
    Read worker outputs and assemble final report in correct section order.

    Args:
        workspace_dir: Directory containing worker output files
        output_path: Path to write the final report
        company_name: Company name for report title
        period: Period for report title (e.g., "FY2024")
    """
    workspace = Path(workspace_dir)

    # Build final report in correct section order: I, II-III, IV, V, VI, VII, VIII-IX
    section_parts = [
        ('worker_1_sections.md',       'I',        'Worker 1'),
        ('worker_2_sections.md',       'II-III',   'Worker 2'),
        ('worker_3_sections.md',       'IV',       'Worker 3'),
        ('worker_4_sections_v.md',     'V',        'Worker 4 (Part 1)'),
        ('worker_5_sections.md',       'VI',       'Worker 5'),
        ('worker_4_sections_vii.md',   'VII',      'Worker 4 (Part 2)'),
        ('worker_6_sections.md',       'VIII-IX',  'Worker 6'),
    ]

    final_report = []
    final_report.append(f"# Financial Analysis Report: {company_name} - {period}\n\n")
    final_report.append("---\n\n")

    sections_found = []
    sections_missing = []

    for filename, sections, description in section_parts:
        filepath = workspace / filename
        if filepath.exists():
            content = filepath.read_text()
            if content.strip():
                final_report.append(content)
                final_report.append("\n\n---\n\n")
                sections_found.append(sections)
                continue

        sections_missing.append(sections)
        print(f"⚠️  Warning: {filename} not found (Sections {sections})")

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
