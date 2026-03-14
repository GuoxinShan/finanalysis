#!/usr/bin/env python3
"""
Benchmark script for finanalysis pipeline output.
Tests against a CSV of questions with known answers.

Requires pipeline to have been run first — reads from output directories.

Usage: uv run python scripts/benchmark.py --csv PATH --output-dir DIR [DIR ...]
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.finanalysis.fs_index import FSIndex


def extract_ground_truth(answer: str) -> float | None:
    """Extract ground truth number from answer string."""
    # Handle 'X sen/cents' pattern for EPS
    unit_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:sen|cents?)', answer, re.IGNORECASE)
    if unit_match:
        return float(unit_match.group(1))

    text = answer
    # Strip any currency'000 patterns (e.g. RM'000, USD'000, S$'000)
    text = re.sub(r"[A-Z$]{1,4}['\u2019]\s*000", "", text)
    text = text.replace("thousand", "")

    # Prefer comma-formatted numbers
    comma_nums = re.findall(r'-?[\d]{1,3}(?:,\d{3})+', text)
    if comma_nums:
        parsed = [float(n.replace(',', '')) for n in comma_nums]
        return max(parsed, key=abs)

    # Fall back to decimal or large integers
    nums = re.findall(r'-?\d+\.\d+|-?\d{4,}', text)
    if nums:
        parsed = [float(n) for n in nums]
        return max(parsed, key=abs)

    return None


def parse_question(question: str) -> dict:
    """Parse a question into structured lookup parameters."""
    q = question.lower()

    entity = "company" if "company" in q and "group" not in q else "group"

    year = None
    for y in ["2025", "2024", "2023", "2022"]:
        if y in q:
            year = y
            break

    label = ""
    m = re.search(r'what was the (.+?)\s+(?:as\s+at\s+|at the end of)', q)
    if not m:
        m = re.search(r'what was the (.+)\s+for\s+(?:the\s+)?(?:\w+\s+)*?(?:group|company)\b', q)
    if not m:
        m = re.search(r'what was the (.+?)(?:\s+in\s+\d{4})', q)
    if m:
        label = m.group(1).strip()

    label = re.sub(r'\s+for\s+(?:\w+\s+)*(?:group|company).*$', '', label)
    label = re.sub(r'\s+for\s+the\s+(?:group|company).*$', '', label)
    label = re.sub(r'\s+at the end of \d{4}$', ' at the end of the financial year', label)
    label = re.sub(r'\s+', ' ', label)

    return {"label": label, "entity": entity, "year": year}


def load_indexes(output_dirs: list[Path]) -> dict[str, FSIndex]:
    """Load FSIndex from pipeline output directories."""
    indexes: dict[str, FSIndex] = {}
    for out_dir in output_dirs:
        fs_path = out_dir / "fs_index.json"
        if not fs_path.exists():
            print(f"  WARNING: {fs_path} not found, skipping")
            continue

        idx = FSIndex.load(fs_path)
        if not idx.line_items:
            print(f"  WARNING: {fs_path} has no line items, skipping")
            continue

        # Use fiscal_year_end from fs_index, fall back to directory name
        year = None
        if idx.fiscal_year_end:
            year = idx.fiscal_year_end[:4]  # "2024-12-31" -> "2024"
        else:
            year_match = re.search(r'(20\d{2})', out_dir.name) or re.search(r'(20\d{2})', str(out_dir))
            if year_match:
                year = year_match.group(1)

        if year:
            indexes[year] = idx
            print(f"  Loaded {fs_path}: {len(idx.line_items)} items, year={year}, fy_end={idx.fiscal_year_end}, currency={idx.currency}")
        else:
            print(f"  WARNING: cannot detect year from {out_dir}, skipping")

    return indexes


def run_benchmark(csv_path: Path, output_dirs: list[Path]):
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        questions = list(reader)

    print(f"Loaded {len(questions)} test questions\n")

    indexes = load_indexes(output_dirs)
    if not indexes:
        print("ERROR: No valid pipeline outputs found. Run the pipeline first:")
        print("  uv run finanalysis parse <pdf> -o <output-dir>")
        sys.exit(1)

    print(f"\nLoaded years: {sorted(indexes.keys())}\n")

    results = []
    correct = 0
    total = 0
    errors_by_metric = defaultdict(list)

    for i, q in enumerate(questions):
        question = q["英文问题"]
        ground_truth_str = q["英文答案"]
        metric_label = q["涉及指标"].split(":")[0].strip()

        parsed = parse_question(question)
        year = parsed["year"]

        if not year or year not in indexes:
            results.append({
                "question": question, "metric": metric_label,
                "year": year, "ground_truth": None,
                "predicted": None, "correct": False,
                "error": "no_index"
            })
            continue

        gt_num = extract_ground_truth(ground_truth_str)

        idx = indexes[year]
        predicted = idx.lookup(parsed["label"], parsed["entity"], "current")

        # Try prior period from a newer year's report
        if predicted is None:
            for other_year in sorted(indexes.keys(), reverse=True):
                if other_year > year:
                    predicted = indexes[other_year].lookup(
                        parsed["label"], parsed["entity"], "prior"
                    )
                    if predicted is not None:
                        break

        is_correct = False
        if gt_num is not None and predicted is not None:
            tolerance = abs(gt_num) * 0.01
            is_correct = abs(predicted - gt_num) <= max(tolerance, 1.0)

        status = "✓" if is_correct else "✗"
        gt_str = f"{gt_num:,.0f}" if gt_num else "None"
        pred_str = f"{predicted:,.0f}" if predicted else "None"
        print(f"[{i+1}/{len(questions)}] {status} {question[:65]}")
        if not is_correct:
            print(f"         GT={gt_str}  Pred={pred_str}  label='{parsed['label']}' entity={parsed['entity']}")

        if is_correct:
            correct += 1
        else:
            errors_by_metric[metric_label].append({
                "question": question[:60],
                "gt": gt_num, "predicted": predicted,
                "parsed_label": parsed["label"],
            })

        total += 1
        results.append({
            "question": question, "metric": metric_label,
            "year": year, "ground_truth": gt_num,
            "predicted": predicted, "correct": is_correct,
        })

    accuracy = correct / total * 100 if total > 0 else 0
    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"Total questions: {total}")
    print(f"Correct:         {correct}")
    print(f"Accuracy:        {accuracy:.1f}%")
    print()

    if errors_by_metric:
        print(f"FAILURES BY METRIC:")
        print(f"{'-'*60}")
        for metric, failures in sorted(
            errors_by_metric.items(), key=lambda x: -len(x[1])
        ):
            print(f"  {metric} ({len(failures)} failures):")
            for f in failures[:2]:
                print(f"    Q: {f['question']}")
                print(f"    GT: {f['gt']}  Predicted: {f['predicted']}")
                print(f"    Parsed label: '{f['parsed_label']}'")
            print()

    out_path = Path("output/benchmark_results.json")
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "accuracy": accuracy, "correct": correct,
            "total": total, "results": results
        }, f, indent=2)
    print(f"Detailed results saved to {out_path}")

    return accuracy, results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark finanalysis pipeline output")
    parser.add_argument(
        "--csv", required=True,
        help="Path to test questions CSV"
    )
    parser.add_argument(
        "--output-dir", required=True, nargs="+",
        help="Pipeline output directories (one per year)"
    )
    args = parser.parse_args()
    run_benchmark(
        csv_path=Path(args.csv),
        output_dirs=[Path(d) for d in args.output_dir]
    )
