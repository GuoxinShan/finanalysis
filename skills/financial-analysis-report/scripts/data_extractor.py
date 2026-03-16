#!/usr/bin/env python3
"""
Data Extractor CLI — query fs_index.json and text_blocks.jsonl.

Usage:
    python data_extractor.py <fs_index.json> --metric <name> [--metric <name> ...]
    python data_extractor.py <fs_index.json> --category <statement>
    python data_extractor.py <fs_index.json> --search <keyword>
    python data_extractor.py <fs_index.json> --list
    python data_extractor.py <fs_index.json> --text-search <query>
    python data_extractor.py <fs_index.json> --text-page <range>

All output is JSON on stdout. Errors go to stderr.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_fs_index(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text_blocks(directory: str) -> List[Dict]:
    """Load text_blocks.jsonl co-located with the fs_index file."""
    tb_path = os.path.join(directory, "text_blocks.jsonl")
    if not os.path.exists(tb_path):
        return None  # signal that file was missing
    blocks: List[Dict] = []
    with open(tb_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                blocks.append(json.loads(line))
    return blocks


def find_metric(fs_index: Dict, name: str) -> Optional[Dict]:
    """Find a line item by exact match first, then substring match."""
    items = fs_index.get("line_items", {})

    # Exact match (case-insensitive)
    for key, val in items.items():
        if key.lower() == name.lower():
            return {"key": key, **val, "source": key}

    # Substring match (case-insensitive)
    for key, val in items.items():
        if name.lower() in key.lower():
            return {"key": key, **val, "source": key}

    return None


def cmd_metric(fs_index: Dict, names: List[str]) -> Dict:
    """Extract one or more metrics."""
    if len(names) == 1:
        result = find_metric(fs_index, names[0])
        if result is None:
            return {
                "source": names[0],
                "value": None,
                "guidance": f"Metric '{names[0]}' not found. Use --search to find similar keys or --list to see all available fields.",
            }
        return result

    # Multiple metrics
    out = {}
    for name in names:
        result = find_metric(fs_index, name)
        if result is not None:
            out[result["key"]] = result
        else:
            out[name] = {
                "source": name,
                "value": None,
                "guidance": f"Metric '{name}' not found.",
            }
    return out


def cmd_category(fs_index: Dict, category: str) -> Dict:
    """Extract all metrics from a statement category."""
    items = fs_index.get("line_items", {})
    out = {}
    for key, val in items.items():
        if val.get("statement") == category:
            out[key] = {"key": key, **val, "source": key}
    out["_metadata"] = {
        "currency": fs_index.get("currency"),
        "fiscal_year_end": fs_index.get("fiscal_year_end"),
        "company_name": fs_index.get("company_name"),
        "category": category,
        "count": len(out) - 1,  # exclude _metadata
    }
    return out


def cmd_search(fs_index: Dict, keyword: str) -> Dict:
    """Fuzzy search line items by keyword."""
    items = fs_index.get("line_items", {})
    kw = keyword.lower()
    results = []
    for key, val in items.items():
        if kw in key.lower() or kw in val.get("label", "").lower():
            results.append({
                "key": key,
                "label": val.get("label", key),
                "statement": val.get("statement"),
                "section": val.get("section"),
            })
    return {"query": keyword, "count": len(results), "results": results}


def cmd_list(fs_index: Dict) -> Dict:
    """List all available fields grouped by statement."""
    items = fs_index.get("line_items", {})
    grouped: Dict[str, Dict[str, Dict]] = {}
    for key, val in items.items():
        stmt = val.get("statement", "unknown")
        label = val.get("label", key)
        # Deduplicate by label — keep the first key seen for each label
        if stmt not in grouped:
            grouped[stmt] = {}
        if label not in grouped[stmt]:
            grouped[stmt][label] = {"key": key, "label": label}
    # Convert to lists
    out = {}
    for stmt, entries in grouped.items():
        out[stmt] = list(entries.values())
    return out


def cmd_text_search(directory: str, query: str, top: int = 20) -> Dict:
    """Search text_blocks.jsonl for keyword."""
    blocks = load_text_blocks(directory)
    if blocks is None:
        return {
            "query": query,
            "count": 0,
            "results": [],
            "warning": "text_blocks.jsonl not found in the same directory as fs_index.json",
        }
    q = query.lower()
    results = [
        {"page_number": b["page_number"], "text": b.get("text", "")}
        for b in blocks
        if q in b.get("text", "").lower()
    ]
    return {"query": query, "count": len(results[:top]), "results": results[:top]}


def _parse_page_range(range_str: str):
    """Parse a page range like '45-60' or '10' into (start, end) tuple."""
    if "-" in range_str:
        parts = range_str.split("-", 1)
        return int(parts[0]), int(parts[1])
    else:
        n = int(range_str)
        return n, n


def cmd_text_page(directory: str, page_range: str) -> Dict:
    """Extract text from a page range."""
    blocks = load_text_blocks(directory)
    start, end = _parse_page_range(page_range)
    if blocks is None:
        return {
            "pages": f"{start}-{end}",
            "count": 0,
            "results": [],
            "warning": "text_blocks.jsonl not found in the same directory as fs_index.json",
        }
    results = [
        {"page_number": b["page_number"], "text": b.get("text", "")}
        for b in blocks
        if start <= b.get("page_number", 0) <= end
    ]
    return {"pages": f"{start}-{end}", "count": len(results), "results": results}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query fs_index.json and text_blocks.jsonl for financial data."
    )
    parser.add_argument("fs_index", help="Path to fs_index.json file")
    parser.add_argument("--metric", nargs="+", dest="metrics", help="Extract one or more metrics by name")
    parser.add_argument("--category", choices=["income_statement", "balance_sheet", "cash_flow"],
                        help="Extract all metrics from a statement")
    parser.add_argument("--search", help="Fuzzy search line items by keyword")
    parser.add_argument("--list", action="store_true", help="List all available fields grouped by statement")
    parser.add_argument("--text-search", help="Search text_blocks.jsonl for keywords")
    parser.add_argument("--top", type=int, default=20, help="Max results for --text-search (default: 20)")
    parser.add_argument("--text-page", help="Extract text from page range (e.g., 45-60)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Validate: at least one action required
    if not (args.metrics or args.category or args.search or args.list or args.text_search or args.text_page):
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    # Load fs_index
    try:
        fs_index = load_fs_index(args.fs_index)
    except FileNotFoundError:
        print(f"Error: file not found: {args.fs_index}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.fs_index}: {e}", file=sys.stderr)
        sys.exit(1)

    fs_dir = str(Path(args.fs_index).parent)

    # Dispatch
    if args.metrics:
        result = cmd_metric(fs_index, args.metrics)
    elif args.category:
        result = cmd_category(fs_index, args.category)
    elif args.search:
        result = cmd_search(fs_index, args.search)
    elif args.list:
        result = cmd_list(fs_index)
    elif args.text_search:
        result = cmd_text_search(fs_dir, args.text_search, args.top)
    elif args.text_page:
        result = cmd_text_page(fs_dir, args.text_page)
    else:
        # Should not reach here due to validation above
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline


if __name__ == "__main__":
    main()
