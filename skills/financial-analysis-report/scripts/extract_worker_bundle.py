#!/usr/bin/env python3
"""
Extract individual worker data bundles from the combined data_bundles.json

This utility helps coordinators extract worker-specific data for passing to agents,
avoiding the need for workers to read files.

Usage:
    # Extract single worker bundle
    python extract_worker_bundle.py --worker 2 --input workspace/data_bundles.json

    # Extract all worker bundles to separate files
    python extract_worker_bundle.py --all --input workspace/data_bundles.json --output-dir workspace/bundles

    # Extract with multi-year trends included
    python extract_worker_bundle.py --worker 2 --input workspace/data_bundles.json --include-trends

    # List available workers
    python extract_worker_bundle.py --list --input workspace/data_bundles.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def load_data_bundles(input_path: str) -> Dict[str, Any]:
    """Load the combined data_bundles.json file"""
    with open(input_path, 'r') as f:
        return json.load(f)


def extract_worker_bundle(
    data_bundles: Dict[str, Any],
    worker_id,  # int (1-6)
    include_trends: bool = True,
    include_global: bool = False
) -> Dict[str, Any]:
    """
    Extract a single worker's data bundle.

    Args:
        data_bundles: The combined data bundles dict
        worker_id: Worker ID (1-6)
        include_trends: Whether to include multi-year trends
        include_global: Whether to include global verification metadata

    Returns:
        Dict with worker's data bundle
    """
    worker_key = f"worker_{worker_id}"

    if worker_key not in data_bundles:
        raise KeyError(f"Worker {worker_id} not found in data bundles")

    # Start with worker-specific data
    bundle = {
        worker_key: data_bundles[worker_key]
    }

    # Optionally include multi-year trends
    if include_trends and "_multi_year_trends" in data_bundles:
        bundle["_multi_year_trends"] = data_bundles["_multi_year_trends"]

    # Optionally include global metadata
    if include_global and "_global_verification" in data_bundles:
        bundle["_global_verification"] = data_bundles["_global_verification"]

    return bundle


def extract_all_bundles(
    data_bundles: Dict[str, Any],
    include_trends: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Extract all worker bundles as separate dicts.

    Returns:
        Dict mapping worker_id to worker bundle
    """
    all_bundles = {}

    # Worker IDs: 1-6
    worker_ids = list(range(1, 7))

    for worker_id in worker_ids:
        try:
            all_bundles[f"worker_{worker_id}"] = extract_worker_bundle(
                data_bundles,
                worker_id,
                include_trends=include_trends
            )
        except KeyError:
            print(f"⚠️  Warning: worker_{worker_id} not found, skipping")

    return all_bundles


def list_available_workers(data_bundles: Dict[str, Any]) -> None:
    """List all available worker bundles"""
    print("\nAvailable Workers:")
    print("=" * 60)

    worker_ids = list(range(1, 7))

    for worker_id in worker_ids:
        worker_key = f"worker_{worker_id}"
        if worker_key in data_bundles:
            worker_data = data_bundles[worker_key]

            # Try to determine what sections this worker handles
            sections_info = ""
            if "sections" in worker_data:
                sections_info = f" (Sections: {worker_data['sections']})"

            print(f"  ✓ Worker {worker_id}{sections_info}")
        else:
            print(f"  ✗ Worker {worker_id} - Not available")

    # Check for multi-year trends
    if "_multi_year_trends" in data_bundles:
        trends = data_bundles["_multi_year_trends"]
        print(f"\n✓ Multi-Year Trends Available:")
        print(f"  Years: {trends.get('years', [])}")
        print(f"  CAGRs: {len(trends.get('cagrs', {}))} metrics")

    print("=" * 60)


def format_as_prompt_data(bundle: Dict[str, Any], worker_id: int) -> str:
    """
    Format worker bundle as a string suitable for including in agent prompt.

    This creates a formatted JSON string that can be directly inserted into
    a worker agent's prompt without them needing to read files.
    """
    return json.dumps(bundle, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Extract worker-specific data bundles from combined data_bundles.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract Worker 2 bundle as JSON
  python extract_worker_bundle.py --worker 2 --input workspace/data_bundles.json

  # Extract Worker 2 with trends, formatted for prompt
  python extract_worker_bundle.py --worker 2 --input workspace/data_bundles.json --format prompt

  # Extract all workers to separate files
  python extract_worker_bundle.py --all --input workspace/data_bundles.json --output-dir workspace/bundles

  # List available workers
  python extract_worker_bundle.py --list --input workspace/data_bundles.json
        """
    )

    parser.add_argument(
        "--worker",
        type=str,
        help="Worker ID to extract (1-6)"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Extract all worker bundles to separate files"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available workers and exit"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to data_bundles.json"
    )

    parser.add_argument(
        "--output",
        help="Output file path (for single worker extraction)"
    )

    parser.add_argument(
        "--output-dir",
        help="Output directory (for --all extraction)"
    )

    parser.add_argument(
        "--format",
        choices=["json", "prompt"],
        default="json",
        help="Output format: 'json' for file, 'prompt' for agent prompt inclusion"
    )

    parser.add_argument(
        "--include-trends",
        action="store_true",
        default=True,
        help="Include multi-year trends in bundle (default: True)"
    )

    parser.add_argument(
        "--no-trends",
        action="store_true",
        help="Exclude multi-year trends from bundle"
    )

    args = parser.parse_args()

    # Load data bundles
    try:
        data_bundles = load_data_bundles(args.input)
        print(f"✓ Loaded: {args.input}")
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {args.input}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in {args.input}: {e}")
        sys.exit(1)

    # Handle --list
    if args.list:
        list_available_workers(data_bundles)
        return

    # Handle --all
    if args.all:
        if not args.output_dir:
            print("❌ ERROR: --output-dir required when using --all")
            sys.exit(1)

        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        all_bundles = extract_all_bundles(
            data_bundles,
            include_trends=not args.no_trends
        )

        print(f"\n✓ Extracting {len(all_bundles)} worker bundles to {output_dir}/")
        for worker_key, bundle in all_bundles.items():
            output_file = output_dir / f"{worker_key}_bundle.json"
            with open(output_file, 'w') as f:
                json.dump(bundle, f, indent=2, ensure_ascii=False)
            print(f"  ✓ {output_file}")

        print(f"\nUsage in coordinator:")
        print(f"  worker_bundle = Read('{output_dir}/worker_2_bundle.json')")
        print(f"  # Pass directly to agent in prompt")

        return

    # Handle single worker extraction
    if args.worker:
        # Normalize worker ID
        try:
            worker_id = int(args.worker)
        except ValueError:
            worker_id = args.worker

        include_trends = not args.no_trends if args.no_trends else args.include_trends

        try:
            bundle = extract_worker_bundle(
                data_bundles,
                worker_id,
                include_trends=include_trends
            )
        except KeyError as e:
            print(f"❌ ERROR: {e}")
            sys.exit(1)

        # Format output
        if args.format == "prompt":
            output = format_as_prompt_data(bundle, args.worker)
        else:
            output = json.dumps(bundle, indent=2, ensure_ascii=False)

        # Write to file or stdout
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✓ Written to: {args.output}")
        else:
            print("\n" + output)

        if args.format == "prompt":
            print("\n" + "=" * 80)
            print("💡 USAGE IN COORDINATOR:")
            print("=" * 80)
            print(f"""
# Extract worker bundle (coordinator reads ONCE)
worker_{args.worker}_bundle = extract_worker_bundle(
    data_bundles,
    worker_id={args.worker},
    include_trends={include_trends}
)

# Pass directly to agent (no file reading by worker)
worker_{args.worker} = Agent(
    subagent_type="general-purpose",
    description="Worker {args.worker} analysis",
    prompt=f\"\"\"
{{worker_instructions}}

**Your Pre-Loaded Data** (DO NOT read files):
```json
{{json.dumps(worker_{args.worker}_bundle, indent=2)}}
```

Write your sections using the data above.
\"\"\"
)
""")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
