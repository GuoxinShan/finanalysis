#!/usr/bin/env python3
"""
Benchmark script for finanalysis CLI tool against the test set.
Uses FSIndex for direct structured lookups — no LLM at query time.

Usage: uv run python scripts/benchmark.py [--csv PATH] [--pdf-dir DIR]
"""
import argparse
import csv
import re
import json
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
    for noise in ["RM'000", "RM\u2019000", "USD'000", "thousand"]:
        text = text.replace(noise, "")

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

    # Detect entity: company vs group
    entity = "company" if "company" in q and "group" not in q else "group"

    # Detect year
    year = None
    for y in ["2025", "2024", "2023", "2022"]:
        if y in q:
            year = y
            break

    # Extract the metric label from the question
    # Strategy: extract everything between "the" and the entity/date marker
    label = ""
    # Try "as at" pattern (balance sheet)
    m = re.search(r'what was the (.+?)\s+(?:as\s+at\s+|at the end of)', q)
    if not m:
        # Try "for <entity> in <year>" pattern
        m = re.search(r'what was the (.+?)\s+for\s+(?:chin\s+hin|the)\s+(?:group|company)\b', q)
    if not m:
        m = re.search(r'what was the (.+?)(?:\s+in\s+\d{4})', q)
    if m:
        label = m.group(1).strip()

    # Strip trailing entity references that leaked into the label
    label = re.sub(r'\s+for\s+chin\s+hin\s+(?:group|company).*$', '', label)
    label = re.sub(r'\s+for\s+the\s+(?:group|company).*$', '', label)
    # Handle "at the end of 2024" -> "at the end of the financial year"
    label = re.sub(r'\s+at the end of \d{4}$', ' at the end of the financial year', label)
    label = re.sub(r'\s+', ' ', label)

    return {"label": label, "entity": entity, "year": year}


def run_benchmark(csv_path: Path, pdf_dir: Path):
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        questions = list(reader)

    print(f"Loaded {len(questions)} test questions\n")

    # Build FSIndex for each PDF
    indexes: dict[str, FSIndex] = {}
    for pdf in sorted(pdf_dir.glob("*.pdf")):
        year_match = re.search(r'(20\d{2})', pdf.name)
        if not year_match:
            continue
        year = year_match.group(1)
        # Prefer annual report
        if year in indexes and "annual" not in pdf.name.lower():
            continue
        print(f"  Indexing {pdf.name}...")
        idx = FSIndex.from_pdf(pdf)
        if idx.line_items:
            indexes[year] = idx
            print(f"    -> {len(idx.line_items)} line items")

    print(f"\nIndexed years: {sorted(indexes.keys())}\n")

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

        # Direct lookup — period is "current" for the report's own year
        idx = indexes[year]
        predicted = idx.lookup(parsed["label"], parsed["entity"], "current")

        # If not found with current, try prior (some questions ask about
        # prior year data shown in the same report)
        if predicted is None:
            # Check if a newer year's report has this as prior
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
    parser = argparse.ArgumentParser(description="Benchmark finanalysis")
    parser.add_argument(
        "--csv", default="testdata/chin_hin_questions_50_基础指标_标准问法.csv",
        help="Path to test questions CSV"
    )
    parser.add_argument(
        "--pdf-dir", default="testdata",
        help="Directory containing source PDFs"
    )
    args = parser.parse_args()
    run_benchmark(csv_path=Path(args.csv), pdf_dir=Path(args.pdf_dir))
