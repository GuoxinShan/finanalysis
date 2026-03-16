#!/usr/bin/env python3
"""
End-to-end Financial Analysis Report Generation - Multi-Year Support

Orchestrates the complete workflow:
1. Parse PDFs with finanalysis CLI
2. Calculate metrics
3. Generate data bundles for workers
4. Spawn parallel workers
5. Assemble final report

Usage (Flexible Multi-Year):
    # 3 years of data (recommended for trend analysis)
    python generate_report.py \
        --company CHINHIN \
        --pdfs 2024:path/to/2024.pdf 2023:path/to/2023.pdf 2022:path/to/2022.pdf \
        --output-dir output/CHINHIN \
        --workspace workspace/

    # 2 years of data (minimum for YoY comparison)
    python generate_report.py \
        --company CHINHIN \
        --pdfs 2024:path/to/2024.pdf 2023:path/to/2023.pdf \
        --output-dir output/CHINHIN

    # Single year (no trend analysis)
    python generate_report.py \
        --company CHINHIN \
        --pdfs 2024:path/to/2024.pdf \
        --output-dir output/CHINHIN
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple


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
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        raise


def extract_year_from_fs_index(fs_index_path: str) -> str:
    """Extract fiscal year from fs_index.json"""
    import json
    with open(fs_index_path, 'r') as f:
        fs_index = json.load(f)

    fiscal_year_end = fs_index.get('fiscal_year_end') or ''
    if fiscal_year_end and fiscal_year_end[:4].isdigit():
        return fiscal_year_end[:4]  # Extract year from "YYYY-MM-DD"
    raise ValueError(f"Cannot determine fiscal year from {fs_index_path} — fiscal_year_end is missing or null")


def validate_periods(fs_index_paths: Dict[str, str]) -> None:
    """
    Validate that all periods are different and in correct chronological order.

    Args:
        fs_index_paths: Dict mapping year string to fs_index.json path
                       e.g., {"2024": "output/2024/fs_index.json", "2023": "output/2023/fs_index.json"}
    """
    if len(fs_index_paths) < 2:
        return

    # Extract years and sort them
    years = sorted(fs_index_paths.keys(), reverse=True)

    # Verify each year is different
    if len(years) != len(set(years)):
        raise ValueError(
            f"❌ ERROR: Duplicate years detected in input. "
            f"Each PDF must be from a different fiscal year.\n"
            f"Years provided: {years}"
        )

    # Verify chronological order (newest first)
    for i in range(len(years) - 1):
        if int(years[i]) <= int(years[i + 1]):
            raise ValueError(
                f"❌ ERROR: Years must be in descending order (newest first).\n"
                f"Found: {years[i]} followed by {years[i + 1]}\n"
                f"Expected order: {years}"
            )

    print(f"✓ Period validation passed: {', '.join([f'FY{y}' for y in years])}")


def parse_pdf(pdf_path: str, company_name: str, output_dir: str) -> str:
    """Parse a PDF and generate fs_index.json in a year-based subdirectory"""
    cli = find_finanalysis_cli()

    # Validate PDF exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    print(f"Parsing PDF: {pdf_path}")

    # Parse to temporary directory first to get fiscal year
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_output = os.path.join(temp_dir, 'fs_index.json')

        # Run parse command to temporary location
        cmd = cli + ['parse', pdf_path, '--company', company_name, '-o', temp_dir]

        try:
            run_cli(cmd, f"Parsing {pdf_path}")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to parse PDF: {pdf_path}")
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Exit code: {e.returncode}")
            if e.stdout:
                print(f"   stdout: {e.stdout}")
            if e.stderr:
                print(f"   stderr: {e.stderr}")
            raise

        # Check if fs_index.json was created
        if not os.path.exists(temp_output):
            raise FileNotFoundError(
                f"fs_index.json not created at {temp_output}. "
                f"The finanalysis parse command may have failed silently."
            )

        # Extract year from fs_index
        year = extract_year_from_fs_index(temp_output)

        # Create year-based subdirectory
        year_dir = os.path.join(output_dir, year)
        os.makedirs(year_dir, exist_ok=True)

        # Copy ALL output files to final location (not just fs_index.json)
        # This includes: text_blocks.jsonl, table_rows.jsonl, page_manifests.jsonl, etc.
        for filename in os.listdir(temp_dir):
            temp_file = os.path.join(temp_dir, filename)
            if os.path.isfile(temp_file):
                final_file = os.path.join(year_dir, filename)
                shutil.copy(temp_file, final_file)
                print(f"✓ Copied: {filename}")

        final_output = os.path.join(year_dir, 'fs_index.json')

        return final_output


def calculate_metrics(fs_index_path: str, prior_fs_index_paths: Optional[List[str]], output_path: str) -> str:
    """
    Calculate derived metrics from fs_index.json

    Args:
        fs_index_path: Path to current year fs_index.json
        prior_fs_index_paths: List of paths to prior year fs_index.json files (in chronological order, newest first)
        output_path: Where to save metrics.json
    """
    cli = find_finanalysis_cli()

    cmd = cli + ['calculate', fs_index_path]

    # Add prior years if available (newest first)
    if prior_fs_index_paths:
        # For now, only use the most recent prior year for metrics calculation
        # The finanalysis CLI currently only supports one --prior argument
        # Future enhancement: support multi-year metrics calculation
        cmd.extend(['--prior', prior_fs_index_paths[0]])

    cmd.extend(['--output', output_path])

    run_cli(cmd, f"Calculating metrics for {fs_index_path}")

    return output_path


def generate_data_bundles(
    fs_index_path: str,
    company_name: str,
    prior_fs_index_paths: Optional[List[str]],
    output_path: str
) -> str:
    """
    Generate data bundles for workers with multi-year support

    Args:
        fs_index_path: Path to current year fs_index.json
        company_name: Company name
        prior_fs_index_paths: List of paths to prior year fs_index.json files (newest first)
        output_path: Where to save data_bundles.json
    """
    # Get path to data_extractor.py
    script_dir = Path(__file__).parent
    extractor_path = script_dir / 'data_extractor.py'

    if not extractor_path.exists():
        raise FileNotFoundError(f"Could not find data_extractor.py at {extractor_path}")

    # Get path to text_blocks.jsonl for current year
    fs_index_dir = Path(fs_index_path).parent
    text_blocks_path = fs_index_dir / 'text_blocks.jsonl'

    cmd = [sys.executable, str(extractor_path),
           fs_index_path,
           '--company', company_name]

    # Add multiple prior years if available
    if prior_fs_index_paths:
        for prior_path in prior_fs_index_paths:
            cmd.extend(['--prior', prior_path])

    # Add text_blocks if it exists
    if text_blocks_path.exists():
        cmd.extend(['--text-blocks', str(text_blocks_path)])
        print(f"✓ Found text_blocks: {text_blocks_path}")
    else:
        print(f"⚠️  Warning: text_blocks.jsonl not found at {text_blocks_path}")
        print(f"   Workers will have limited qualitative data access")

    cmd.extend(['--output', output_path])

    run_cli(cmd, f"Generating data bundles with {len(prior_fs_index_paths) if prior_fs_index_paths else 0} prior years")

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


def parse_pdfs_arg(pdfs_list: List[str]) -> Dict[str, str]:
    """
    Parse --pdfs arguments into a dict mapping year to path.

    Args:
        pdfs_list: List of strings in format "YEAR:PATH"

    Returns:
        Dict mapping year string to PDF path

    Example:
        Input: ["2024:path/to/2024.pdf", "2023:path/to/2023.pdf"]
        Output: {"2024": "path/to/2024.pdf", "2023": "path/to/2023.pdf"}
    """
    pdfs = {}
    for item in pdfs_list:
        if ':' not in item:
            raise ValueError(
                f"❌ Invalid --pdfs format: '{item}'\n"
                f"Expected format: YEAR:PATH (e.g., '2024:path/to/2024.pdf')"
            )

        parts = item.split(':', 1)  # Split on first colon only
        if len(parts) != 2:
            raise ValueError(
                f"❌ Invalid --pdfs format: '{item}'\n"
                f"Expected format: YEAR:PATH (e.g., '2024:path/to/2024.pdf')"
            )

        year, path = parts
        year = year.strip()
        path = path.strip()

        # Validate year
        if not year.isdigit() or len(year) != 4:
            raise ValueError(
                f"❌ Invalid year: '{year}'\n"
                f"Year must be a 4-digit number (e.g., '2024')"
            )

        pdfs[year] = path

    return pdfs


def main():
    parser = argparse.ArgumentParser(
        description="Generate complete financial analysis report end-to-end with multi-year support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 3 years of data (recommended for trend analysis)
  python generate_report.py \\
    --company CHINHIN \\
    --pdfs 2024:report2024.pdf 2023:report2023.pdf 2022:report2022.pdf \\
    --output-dir output/CHINHIN

  # 2 years of data (minimum for YoY comparison)
  python generate_report.py \\
    --company CHINHIN \\
    --pdfs 2024:report2024.pdf 2023:report2023.pdf \\
    --output-dir output/CHINHIN

  # Single year (no trend analysis)
  python generate_report.py \\
    --company CHINHIN \\
    --pdfs 2024:report2024.pdf \\
    --output-dir output/CHINHIN
        """
    )

    parser.add_argument(
        "--pdfs",
        nargs='+',
        required=True,
        help="PDF files in format YEAR:PATH (e.g., 2024:report2024.pdf 2023:report2023.pdf)"
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
    print("Financial Analysis Report Generator - Multi-Year Edition")
    print("=" * 80)

    # Parse PDF arguments
    try:
        pdfs = parse_pdfs_arg(args.pdfs)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    # Sort years (newest first)
    years = sorted(pdfs.keys(), reverse=True)

    print(f"Company: {args.company}")
    print(f"Years: {', '.join([f'FY{y}' for y in years])} ({len(years)} years)")
    print(f"Output Directory: {args.output_dir}")
    print(f"Workspace: {args.workspace}")
    print("=" * 80)

    # Create directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.workspace, exist_ok=True)

    # Step 1: Parse PDFs
    fs_index_paths = {}  # Maps year to fs_index.json path

    if not args.skip_pdf_parsing:
        print("\n[Step 1/5] Parsing PDFs...")
        print("-" * 80)

        for year in years:
            pdf_path = pdfs[year]
            fs_index_path = parse_pdf(pdf_path, args.company, args.output_dir)
            fs_index_paths[year] = fs_index_path

        # Validate periods are different and in correct order
        try:
            validate_periods(fs_index_paths)
        except ValueError as e:
            print(str(e))
            sys.exit(1)
    else:
        # When skipping parsing, find fs_index.json in year-based subdirectories
        print("\n[Step 1/5] Using existing fs_index.json files...")
        print("-" * 80)

        for year in years:
            fs_index_path = os.path.join(args.output_dir, year, 'fs_index.json')

            if not os.path.exists(fs_index_path):
                print(f"❌ ERROR: fs_index.json not found at {fs_index_path}")
                print(f"   Run without --skip-pdf-parsing to parse PDFs first")
                sys.exit(1)

            fs_index_paths[year] = fs_index_path

        print(f"✓ Using existing fs_index.json files:")
        for year in years:
            print(f"  FY{year}: {fs_index_paths[year]}")

        # Validate periods
        try:
            validate_periods(fs_index_paths)
        except ValueError as e:
            print(str(e))
            sys.exit(1)

    # Determine period from current (most recent) year
    current_year = years[0]
    prior_years = years[1:] if len(years) > 1 else []

    period = f"FY{current_year}"
    print(f"\n✓ Current Period: {period}")
    if prior_years:
        print(f"✓ Prior Years: {', '.join([f'FY{y}' for y in prior_years])}")

    # Step 2: Calculate metrics
    if not args.skip_metrics:
        print("\n[Step 2/5] Calculating derived metrics...")
        print("-" * 80)

        metrics_path = os.path.join(args.output_dir, current_year, 'metrics.json')

        prior_paths = [fs_index_paths[y] for y in prior_years] if prior_years else None
        calculate_metrics(fs_index_paths[current_year], prior_paths, metrics_path)
    else:
        print("\n[Step 2/5] Skipping metrics calculation (using existing)")
        print("-" * 80)

    # Step 3: Generate data bundles
    if not args.skip_bundles:
        print("\n[Step 3/5] Generating data bundles for workers...")
        print("-" * 80)

        data_bundles_path = os.path.join(args.workspace, 'data_bundles.json')

        prior_paths = [fs_index_paths[y] for y in prior_years] if prior_years else None
        generate_data_bundles(fs_index_paths[current_year], args.company, prior_paths, data_bundles_path)

        print(f"\n✓ Multi-year data bundles created:")
        print(f"  Current: FY{current_year}")
        if prior_years:
            for y in prior_years:
                print(f"  Prior: FY{y}")
    else:
        print("\n[Step 3/5] Skipping data bundle generation (using existing)")
        print("-" * 80)
        data_bundles_path = os.path.join(args.workspace, 'data_bundles.json')

    # Step 4: Prepare worker workspace
    print("\n[Step 4/5] Preparing worker workspace...")
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
    print(f"📅 Years: {', '.join([f'FY{y}' for y in years])} ({len(years)}-year analysis)")

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
