#!/usr/bin/env python3
"""
End-to-end Financial Analysis Report Generation

Orchestrates the complete workflow:
1. Parse PDFs with finanalysis CLI
2. Calculate metrics
3. Generate data bundles for workers
4. Spawn parallel workers
5. Assemble final report

Usage:
    python generate_report.py \
        --pdf-2024 <path/to/2024.pdf> \
        --pdf-2023 <path/to/2023.pdf> \
        --company CHINHIN \
        --output-dir output/CHINHIN \
        [--workspace workspace/]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def find_finanalysis_cli() -> List[str]:
    """
    Try multiple ways to find the finanalysis CLI.

    Returns:
        Command as list of strings to run finanalysis

    Raises:
        RuntimeError: If CLI cannot be found
    """
    # 1. Check if in PATH
    if shutil.which('finanalysis'):
        return ['finanalysis']

    # 2. Check common virtual environment locations
    common_paths = [
        '../finanalysis/.venv/bin/python -m finanalysis.cli',
        os.path.expanduser('~/.local/bin/finanalysis'),
        './venv/bin/finanalysis',
        'venv/bin/finanalysis'
    ]

    for path in common_paths:
        parts = path.split()
        if os.path.exists(parts[0]):
            return parts

    # 3. Check if finanalysis module is importable
    try:
        import importlib
        importlib.import_module('finanalysis')
        # Found as module, try running via python -m
        return [sys.executable, '-m', 'finanalysis.cli']
    except ImportError:
        pass

    raise RuntimeError(
        "Could not find finanalysis CLI. Please either:\n"
        "1. Install it: pip install git+https://github.com/GuoxinShan/finanalysis.git\n"
        "2. Activate the venv: source ../finanalysis/.venv/bin/activate\n"
        "3. Add to PATH\n"
        "Alternatively, provide the path to the finanalysis CLI via environment variable."
    )


def run_cli(command: List[str], description: str = "Run a CLI command and handle errors"):
    print(f"Running: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        if result.returncode != 0:
            print(f"❌ Error running {description}")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            sys.exit(1)

        print(f"✓ {description} completed")
        return result

    except FileNotFoundError:
        print(f"❌ Command not found: {' '.join(command)}")
        raise


def parse_pdf(pdf_path: str, company_name: str, output_dir: str) -> str:
    """Parse a PDF and generate fs_index.json"""
    cli = find_finanalysis_cli()

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Run parse command
    cmd = cli + ['parse', pdf_path, '--company', company_name, '-o', output_dir]

    run_cli(cmd, f"Parsing {pdf_path}")

    # Return path to fs_index.json
    return os.path.join(output_dir, 'fs_index.json')


def calculate_metrics(fs_index_path: str, prior_fs_index_path: Optional[str], output_path: str) -> str:
    """Calculate derived metrics from fs_index.json"""
    cli = find_finanalysis_cli()

    cmd = cli + ['calculate', fs_index_path]
    if prior_fs_index_path:
        cmd.extend(['--prior', prior_fs_index_path])
    cmd.extend(['--output', output_path])

    run_cli(cmd, f"Calculating metrics for {fs_index_path}")

    return output_path


def generate_data_bundles(fs_index_path: str, company_name: str, prior_fs_index_path: Optional[str], output_path: str) -> str:
    """Generate data bundles for workers"""
    # Get path to data_extractor.py
    script_dir = Path(__file__).parent
    extractor_path = script_dir / 'data_extractor.py'

    if not extractor_path.exists():
        raise FileNotFoundError(f"Could not find data_extractor.py at {extractor_path}")

    cmd = [sys.executable, str(extractor_path),
           fs_index_path,
           '--company', company_name]

    if prior_fs_index_path:
        cmd.extend(['--prior', prior_fs_index_path])
    cmd.extend(['--output', output_path])

    run_cli(cmd, f"Generating data bundles")

    return output_path


def spawn_workers(data_bundles_path: str, workspace_dir: str) -> None:
    """
    Spawn parallel worker agents (placeholder for now)

    This function is a placeholder - in the actual skill workflow,
    this would be done by the coordinator agent spawning 6 subagents.
    Here we just prepare the workspace.

    Args:
        data_bundles_path: Path to data_bundles.json
        workspace_dir: Directory for worker outputs
    """
    os.makedirs(workspace_dir, exist_ok=True)

    # Copy data bundles to workspace (if not already there)
    dest_path = os.path.join(workspace_dir, 'data_bundles.json')
    if os.path.abspath(data_bundles_path) != os.path.abspath(dest_path):
        shutil.copy(data_bundles_path, dest_path)

    print(f"✓ Worker workspace prepared at {workspace_dir}")
    print(f"  Data bundles: {dest_path}")
    print(f"  Worker outputs will be written to: {workspace_dir}/worker_N_sections.md")

    # Note: Actual worker spawning would be done by the skill coordinator
    # using the Agent tool to spawn 6 parallel subagents
    print("\n⏳ Worker spawning is handled by the skill coordinator")
    print("   The coordinator will:")
    print("   1. Read data_bundles.json")
    print("   2. Read worker instructions from references/")
    print("   3. Spawn 6 workers with Agent tool")
    print("   4. Collect worker outputs")
    print("   5. Run assemble_report.py to combine outputs")


def assemble_final_report(workspace_dir: str, output_path: str, company_name: str, period: str) -> None:
    """Assemble final report from worker outputs"""
    # Get path to assemble_report.py
    script_dir = Path(__file__).parent
    assembler_path = script_dir / 'assemble_report.py'

    if not assembler_path.exists():
        raise FileNotFoundError(f"Could not find assemble_report.py at {assembler_path}")

    # Check for worker output files
    worker_files = []
    for i in range(1, 7):
        if i == 6:
            # Worker 6 has two parts
            for part in ['part1', 'part2']:
                path = os.path.join(workspace_dir, f'worker_{i}_sections_{part}.md')
                if os.path.exists(path):
                    worker_files.append(path)
        else:
            path = os.path.join(workspace_dir, f'worker_{i}_sections.md')
            if os.path.exists(path):
                worker_files.append(path)

    if not worker_files:
        print(f"⚠️  No worker output files found in {workspace_dir}")
        print("   Skipping report assembly")
        return

    # Run assembly script
    cmd = [sys.executable, str(assembler_path),
           '--workspace', workspace_dir,
           '--output', output_path,
           '--company', company_name,
           '--period', period]

    result = run_cli(cmd, f"Assembling final Report")

    print(f"✓ Final report: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate complete financial analysis report end-to-end"
    )

    parser.add_argument(
        "--pdf-2024",
        required=True,
        help="Path to 2024 annual report PDF"
    )

    parser.add_argument(
        "--pdf-2023",
        help="Path to 2023 annual report PDF (for YoY comparison)"
    )

    parser.add_argument(
        "--company",
        required=True,
        help="Company name (e.g., CHINHIN)"
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for all generated files"
    )

    parser.add_argument(
        "--workspace",
        default="workspace",
        help="Workspace directory for intermediate files"
    )

    parser.add_argument(
        "--skip-pdf-parsing",
        action="store_true",
        help="Skip PDF parsing (use if fs_index.json already exists)"
    )

    parser.add_argument(
        "--skip-metrics",
        action="store_true",
        help="Skip metrics calculation (use if metrics.json already exists)"
    )

    parser.add_argument(
        "--skip-bundles",
        action="store_true",
        help="Skip data bundle generation (use if data_bundles.json already exists)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Financial Analysis Report Generator")
    print("=" * 80)
    print(f"Company: {args.company}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Workspace: {args.workspace}")
    print("=" * 80)

    # Create directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.workspace, exist_ok=True)

    # Determine period from PDF filename or use default
    period = "FY2024"
    if "2024" in args.pdf_2024:
        period = "FY2024"
    elif "2023" in args.pdf_2024:
        period = "FY2023"

    # Step 1: Parse PDFs
    if not args.skip_pdf_parsing:
        print("\n[Step 1/5] Parsing PDFs...")
        print("-" * 80)

        fs_index_2024 = parse_pdf(args.pdf_2024, args.company, args.output_dir)

        fs_index_2023 = None
        if args.pdf_2023:
            fs_index_2023 = parse_pdf(args.pdf_2023, args.company, args.output_dir)
    else:
        fs_index_2024 = os.path.join(args.output_dir, 'fs_index.json')
        fs_index_2023 = os.path.join(args.output_dir, 'fs_index.json') if args.pdf_2023 else None
        print("✓ Using existing fs_index.json files")

    # Step 2: Calculate metrics
    if not args.skip_metrics:
        print("\n[Step 2/5] Calculating derived metrics...")
        print("-" * 80)

        metrics_path = os.path.join(args.output_dir, 'metrics.json')
        calculate_metrics(fs_index_2024, fs_index_2023, metrics_path)
    else:
        print("\n[Step 2/5] Skipping metrics calculation (using existing)")
        print("-" * 80)

    # Step 3: Generate data bundles
    if not args.skip_bundles:
        print("\n[Step 3/5] Generating data bundles for workers...")
        print("-" * 80)

        data_bundles_path = os.path.join(args.workspace, 'data_bundles.json')
        generate_data_bundles(fs_index_2024, args.company, fs_index_2023, data_bundles_path)
    else:
        print("\n[Step 3/5] Skipping data bundle generation (using existing)")
        print("-" * 80)
        data_bundles_path = os.path.join(args.workspace, 'data_bundles.json')

    # Step 4: Prepare worker workspace
    print("\n[Step 4/4] Preparing worker workspace...")
    print("-" * 80)

    # Prepare workspace (create dir, copy data bundles if needed)
    os.makedirs(args.workspace, exist_ok=True)
    dest_path = os.path.join(args.workspace, 'data_bundles.json')
    if os.path.abspath(data_bundles_path) != os.path.abspath(dest_path):
        shutil.copy(data_bundles_path, dest_path)

    print(f"✓ Worker workspace prepared at {args.workspace}")
    print(f"  Data bundles: {dest_path}")
    print(f"  Worker outputs will be written to: {args.workspace}/worker_N_sections.md")

    # Print final summary
    output_path = f"{args.company}-{period}-revised.md"

    print("\n" + "=" * 80)
    print("✅ PHASE 1 COMPLETE - WORKSPACE PREPARED")
    print("=" * 80)
    print(f"\n📄 Ready to generate: {output_path}")
    print(f"📊 Data Bundles: {data_bundles_path}")
    print(f"🔍 Workspace: {args.workspace}")

    print("\n💡 NEXT STEPS:")
    print("   1. Spawn 6 parallel workers (see instructions below)")
    print("   2. After workers complete, run:")
    print(f"      python scripts/assemble_report.py \\")
    print(f"        --workspace {args.workspace} \\")
    print(f"        --output {output_path} \\")
    print(f"        --company {args.company} \\")
    print(f"        --period {period}")

    print("\n" + "=" * 80)
    print("WORKER SPAWN INSTRUCTIONS")
    print("=" * 80)
    print("\nSpawn 6 parallel workers using the Agent tool:")
    print("\nfor i in {1,2,3,4,5,6}; do")
    print("  Agent(")
    print("    subagent_type='general-purpose',")
    print("    description=f'Worker {i}: Financial analysis sections',")
    print("    prompt=f\"\"\"")
    print(f"Read references/worker_{{i}}_*.md for instructions.")
    print(f"Read {args.workspace}/data_bundles.json and extract worker_{{i}} data.")
    print(f"Write markdown sections to {args.workspace}/worker_{{i}}_sections.md")
    print('    """')
    print("  )")
    print("done")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
