#!/usr/bin/env python3
"""
Prepare workspace for parallel worker report generation.

This script:
1. Parses PDFs (if not already parsed)
2. Calculates metrics
3. Generates data bundles
4. Prepares workspace directory
5. EXITS with instructions (does NOT spawn workers or assemble)

After this script exits, the coordinator should:
1. Spawn 6 parallel workers
2. Run assemble_report.py to"""

import argparse
import json
import os
import shutil
from pathlib import Path

# Import helper functions from generate_report.py
from generate_report import (
    find_finanalysis_cli,
    parse_pdf,
    calculate_metrics,
    generate_data_bundles
)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare workspace for parallel worker report generation"
    )
    parser.add_argument('--pdf-2024', required=True, help='Path to 2024 PDF report')
    parser.add_argument('--pdf-2023', help='Path to 2023 PDF report (for YoY comparison)')
    parser.add_argument('--company', required=True, help='Company name')
    parser.add_argument('--output-dir', required=True, help='Output directory for fs_index.json and metrics.json')
    parser.add_argument('--workspace', required=True, help='Workspace directory for worker outputs')
    parser.add_argument('--skip-pdf-parsing', action='store_true', help='Skip PDF parsing (use existing fs_index.json)')
    parser.add_argument('--skip-metrics', action='store_true', help='Skip metrics calculation')
    parser.add_argument('--skip-bundles', action='store_true', help='Skip data bundle generation')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Determine period
    period = "FY2024"
    if "2024" in args.pdf_2024:
        period = "FY2024"
    elif "2023" in args.pdf_2024:
        period = "FY2023"

    print("\n" + "=" * 80)
    print("PARALLEL WORKER REPORT GENERATION - PHASE 1: PREPARATION")
    print("=" * 80)
    print(f"Company: {args.company}")
    print(f"Period: {period}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Workspace: {args.workspace}")

    # Step 1: Parse PDFs
    if not args.skip_pdf_parsing:
        print("\n[Step 1/3] Parsing PDFs...")
        print("-" * 80)

        fs_index_2024 = parse_pdf(args.pdf_2024, args.company, args.output_dir)

        fs_index_2023 = None
        if args.pdf_2023:
            fs_index_2023 = parse_pdf(args.pdf_2023, args.company, args.output_dir)
    else:
        fs_index_2023 = None

        print(f"✓ PDFs parsed successfully")
        print(f"  2024: {fs_index_2024}")
        if fs_index_2023:
            print(f"  2023: {fs_index_2023}")
    else:
        fs_index_2024 = os.path.join(args.output_dir, 'fs_index.json')
        fs_index_2023 = os.path.join(args.output_dir, '2023', 'fs_index.json') if args.pdf_2023 else None
        print("✓ Using existing fs_index.json files")

    # Step 2: Calculate metrics
    if not args.skip_metrics:
        print("\n[Step 2/3] Calculating derived metrics...")
        print("-" * 80)

        metrics_path = os.path.join(args.output_dir, 'metrics.json')
        calculate_metrics(fs_index_2024, fs_index_2023, metrics_path)

        print(f"✓ Metrics calculated: {metrics_path}")
    else:
        print("\n[Step 2/3] Skipping metrics calculation")
        print("-" * 80)

    # Step 3: Generate data bundles
    print("\n[Step 3/3] Generating data bundles for workers...")
    print("-" * 80)

    os.makedirs(args.workspace, exist_ok=True)
    data_bundles_path = os.path.join(args.workspace, 'data_bundles.json')

    if not args.skip_bundles:
        generate_data_bundles(fs_index_2024, args.company, fs_index_2023, data_bundles_path)
        print(f"✓ Data bundles generated: {data_bundles_path}")
    else:
        print(f"✓ Using existing data bundles: {data_bundles_path}")

    # Extract individual worker bundles
    bundles_dir = os.path.join(args.workspace, 'bundles')
    os.makedirs(bundles_dir, exist_ok=True)

    from extract_worker_bundle import extract_all_bundles
    with open(data_bundles_path) as f:
        data = json.load(f)
    all_bundles = extract_all_bundles(data, include_trends=True)
    for worker_key, bundle in all_bundles.items():
        bundle_path = os.path.join(bundles_dir, f"{worker_key}_bundle.json")
        with open(bundle_path, 'w') as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)
    print(f"✓ Individual bundles extracted to {bundles_dir}/ ({len(all_bundles)} workers)")

    # Print next steps
    print("\n" + "=" * 80)
    print("✅ PHASE 1 COMPLETE - WORKSPACE PREPARED")
    print("=" * 80)
    print(f"\n📁 Workspace: {args.workspace}")
    print(f"📊 Data Bundles: {data_bundles_path}")
    print(f"📋 Metrics: {args.output_dir}/metrics.json")

    print("\n" + "=" * 80)
    print("NEXT: PHASE 2 - SPAWN 6 PARALLEL WORKERS FOR REPORT SECTIONS")
    print("=" * 80)
    print("\nThe workspace is ready. Now spawn 7 parallel worker agents for report sections:")
    print("\n┌─────────────────────────────────────────────────────────────────┐")
    print("│ WORKER SPAWN TEMPLATE (for coordinator)                          │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print("\nfor i in {1,2,3,4,5,6,6b}; do")
    print("  bundle = Read(f'{args.workspace}/bundles/worker_${{i}}_bundle.json')")
    print("  instructions = Read(f'references/worker_${{i}}_*.md')")
    print("  Agent(")
    print("    subagent_type='general-purpose',")
    print("    description=f'Worker ${{i}}: Financial analysis sections',")
    print("    prompt=f\"\"\"")
    print("      {instructions}")
    print("      **Your Pre-Loaded Data Bundle**:")
    print("      ```json")
    print("      {bundle}")
    print("      ```")
    print("      Write your sections using the data above.")
    print("      Output: {args.workspace}/worker_${{i}}_sections.md")
    print('    """')
    print("  )")
    print("done")

    print("\n" + "=" * 80)
    print("NEXT: PHASE 3 - ASSEMBLE FINAL REPORT")
    print("=" * 80)
    print("\nAfter all 6 workers complete, run:")
    print(f"\n  python scripts/assemble_report.py \\")
    print(f"    --workspace {args.workspace} \\")
    print(f"    --output {args.company}-{period}-revised.md \\")
    print(f"    --company {args.company} \\")
    print(f"    --period {period}")

    print("\n" + "=" * 80)
    print("NEXT: PHASE 4 - GENERATE EXECUTIVE SUMMARY (WORKER 7)")
    print("=" * 80)
    print("\nSpawn Worker 7 to generate the executive summary from the full report:")
    print("\n  Agent(")
    print("    subagent_type='general-purpose',")
    print("    description='Executive summary generation',")
    print("    prompt=f\"\"\"")
    print("Read references/worker_7_summary.md for instructions.")
    print(f"Read {args.company}-{period}-revised.md (the full report).")
    print(f"Generate a 4-section executive summary following the worker_7 instructions.")
    print(f"Write the summary to {args.company}-{period}-summary.md")
    print('    """')
    print("  )")

    print("\n" + "=" * 80)
    print("SUMMARY: 4-PHASE WORKFLOW")
    print("=" * 80)
    print("\n1. Preparation (this script) → 2. Workers 1-6 (report sections)")
    print("   → 3. Assembly → 4. Worker 7 (executive summary)")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
