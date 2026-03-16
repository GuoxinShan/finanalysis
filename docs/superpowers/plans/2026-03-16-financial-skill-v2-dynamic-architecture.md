# Financial Analysis Report Skill v2 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fixed 6+1 worker architecture with a dynamic tool-only skill where the model decides report structure, analysis depth, and agent workflow.

**Architecture:** Two CLI tools (data_extractor.py for querying structured metrics + text, financial_calculator.py for computing ratios) and a validation script (validate_report.py for post-generation audit). The SKILL.md is minimal (~70 lines) pointing to tools and references. Two reference files provide data catalog and writing guidelines.

**Tech Stack:** Python 3.11+, argparse, json, re. No external dependencies.

**Spec:** `docs/superpowers/specs/2026-03-16-financial-skill-v2-dynamic-architecture-design.md`

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Rewrite | `skills/financial-analysis-report/scripts/data_extractor.py` | CLI: query fs_index metrics + search text_blocks |
| Rewrite | `skills/financial-analysis-report/scripts/financial_calculator.py` | CLI: compute financial ratios from fs_index |
| Rewrite | `skills/financial-analysis-report/scripts/validate_report.py` | CLI: audit report numbers against fs_index |
| Create | `skills/financial-analysis-report/references/data_catalog.md` | Available fields, calculable ratios, unit system |
| Create | `skills/financial-analysis-report/references/writing_guidelines.md` | Merged tone + precision + units (light) |
| Rewrite | `skills/financial-analysis-report/SKILL.md` | Minimal skill definition (~70 lines) |
| Delete | `skills/financial-analysis-report/references/worker_*.md` (7 files) | Worker instructions no longer needed |
| Delete | `skills/financial-analysis-report/references/canonical_data_registry.md` | No fixed data ownership |
| Delete | `skills/financial-analysis-report/references/output_format_specification.md` | No fixed format |
| Delete | `skills/financial-analysis-report/references/manual_workflow.md` | No fixed workflow |
| Delete | `skills/financial-analysis-report/references/troubleshooting.md` | No fixed workflow to troubleshoot |
| Delete | `skills/financial-analysis-report/references/quick_start_examples.md` | No fixed workflow |
| Delete | `skills/financial-analysis-report/references/data_format.md` | Replaced by data_catalog.md |
| Delete | `skills/financial-analysis-report/scripts/generate_report.py` | No fixed orchestration |
| Delete | `skills/financial-analysis-report/scripts/assemble_report.py` | No fixed assembly |
| Delete | `skills/financial-analysis-report/scripts/extract_worker_bundle.py` | No worker bundles |
| Delete | `skills/financial-analysis-report/scripts/prepare_workspace.py` | No fixed workspace |
| Delete | `skills/financial-analysis-report/scripts/generate_summary.py` | No fixed summary |
| Delete | `skills/financial-analysis-report/scripts/example_worker_extraction.py` | Example for old architecture |
| Delete | `skills/financial-analysis-report/scripts/dashboard_generator.py` | Not needed |
| Rewrite | `tests/skills/financial-analysis-report/test_data_extractor.py` | Tests for new CLI tool |
| Create | `tests/skills/financial-analysis-report/test_financial_calculator.py` | Tests for ratio calculator |
| Rewrite | `tests/skills/financial-analysis-report/test_validate_report.py` | Tests for enhanced validator |

---

## Chunk 1: data_extractor.py

### Task 1: Write tests for data_extractor CLI

**Files:**
- Create: `tests/skills/financial-analysis-report/test_data_extractor.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for data_extractor CLI tool."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent.parent.parent / "skills" / "financial-analysis-report" / "scripts" / "data_extractor.py"
FIXTURES = Path(__file__).parent / "fixtures"

def _run(args):
    """Run data_extractor.py with given args, return parsed JSON output."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    return json.loads(result.stdout)


def _make_fs_index(**overrides):
    """Create a minimal fs_index dict."""
    base = {
        "currency": "MYR",
        "fiscal_year_end": "2024-12-31",
        "company_name": "TEST",
        "line_items": {
            "revenue": {
                "label": "Revenue",
                "statement": "income_statement",
                "section": "revenue",
                "page": 10,
                "group_current": 3252347,
                "group_prior": 2057210,
                "company_current": 3252347,
                "company_prior": 2057210,
            },
            "cost of sales": {
                "label": "Cost of Sales",
                "statement": "income_statement",
                "section": "cost_of_sales",
                "page": 10,
                "group_current": 2727213,
                "group_prior": 1868320,
                "company_current": 2727213,
                "company_prior": 1868320,
            },
            "gross profit": {
                "label": "Gross Profit",
                "statement": "income_statement",
                "section": "gross_profit",
                "page": 10,
                "group_current": 525134,
                "group_prior": 188890,
                "company_current": 525134,
                "company_prior": 188890,
            },
            "cash and bank balances": {
                "label": "Cash and Bank Balances",
                "statement": "balance_sheet",
                "section": "current_assets",
                "page": 15,
                "group_current": 85000,
                "group_prior": 62000,
                "company_current": 85000,
                "company_prior": 62000,
            },
        }
    }
    base["line_items"].update(overrides)
    return base


class TestMetricExtraction:
    def test_single_metric(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--metric", "revenue"])
        assert result["label"] == "revenue"
        assert result["group_current"] == 3252347
        assert result["group_prior"] == 2057210
        assert result["unit"] == "RM'000"
        assert "source" in result

    def test_multiple_metrics(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--metric", "revenue", "gross profit"])
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["label"] == "revenue"
        assert result[1]["label"] == "gross profit"

    def test_metric_not_found(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--metric", "nonexistent"])
        assert result["value"] is None
        assert "not found" in result["message"].lower()


class TestCategoryExtraction:
    def test_category_income_statement(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--category", "income_statement"])
        assert isinstance(result, list)
        labels = [r["label"] for r in result]
        assert "Revenue" in labels
        assert "Gross Profit" in labels
        # Balance sheet items should NOT be here
        assert "Cash and Bank Balances" not in labels


class TestSearch:
    def test_search_finds_match(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--search", "cash"])
        assert isinstance(result, list)
        assert len(result) >= 1
        assert any("cash" in r["label"].lower() for r in result)

    def test_search_no_match(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--search", "xyznotfound"])
        assert isinstance(result, list)
        assert len(result) == 0


class TestList:
    def test_list_all_fields(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--list"])
        assert isinstance(result, dict)
        assert "income_statement" in result
        assert "balance_sheet" in result
        assert "cash_flow" in result
        assert len(result["income_statement"]) >= 1


class TestTextSearch:
    def test_text_search(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        # Create text_blocks.jsonl in same directory
        blocks_path = fs.parent / "text_blocks.jsonl"
        blocks_path.write_text(json.dumps({
            "page_number": 45, "text": "Management Discussion and Analysis"
        }) + "\n" + json.dumps({
            "page_number": 46, "text": "The company faced challenges in the construction sector"
        }) + "\n")
        result = _run([str(fs), "--text-search", "management"])
        assert isinstance(result, list)
        assert len(result) >= 1
        assert result[0]["page_number"] == 45

    def test_text_page_range(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        blocks_path = fs.parent / "text_blocks.jsonl"
        blocks_path.write_text(json.dumps({"page_number": 10, "text": "Page 10 content"}) + "\n")
        result = _run([str(fs), "--text-page", "1-20"])
        assert isinstance(result, list)
        assert len(result) >= 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/skills/financial-analysis-report/test_data_extractor.py -v`
Expected: FAIL (script doesn't exist yet or doesn't have CLI interface)

### Task 2: Implement data_extractor.py

**Files:**
- Rewrite: `skills/financial-analysis-report/scripts/data_extractor.py`

- [ ] **Step 1: Write the implementation**

The new script is a clean CLI tool. Key design:

```python
#!/usr/bin/env python3
"""
Financial Data Extractor — Query structured metrics and search text from parsed annual reports.

Usage:
    python data_extractor.py <fs_index.json> --metric revenue
    python data_extractor.py <fs_index.json> --category income_statement
    python data_extractor.py <fs_index.json> --search "borrowing"
    python data_extractor.py <fs_index.json> --list
    python data_extractor.py <fs_index.json> --text-search "management"
    python data_extractor.py <fs_index.json> --text-page 45-60
"""
import json
import sys
import os
import re
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List


def load_fs_index(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return json.load(f)


def load_text_blocks(fs_index_path: str) -> List[Dict]:
    """Load text_blocks.jsonl from the same directory as fs_index.json."""
    blocks_path = Path(fs_index_path).parent / "text_blocks.jsonl"
    if not blocks_path.exists():
        return []
    blocks = []
    with open(blocks_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                blocks.append(json.loads(line))
    return blocks


def find_line_item(fs_index: Dict, key_pattern: str) -> Optional[Dict]:
    """Find a line item by key pattern (case-insensitive, exact then substring)."""
    items = fs_index.get('line_items', {})
    # Exact match
    for key, item in items.items():
        if key_pattern.lower() == key.lower():
            return item
    # Substring match
    for key, item in items.items():
        if key_pattern.lower() in key.lower():
            return item
    return None


def format_metric(key: str, item: Dict) -> Dict:
    """Format a single metric with source traceability."""
    return {
        "label": item.get("label", key),
        "statement": item.get("statement"),
        "group_current": item.get("group_current"),
        "group_prior": item.get("group_prior"),
        "company_current": item.get("company_current"),
        "company_prior": item.get("company_prior"),
        "unit": "RM'000",
        "source": f"fs_index.line_items['{key}']",
    }


def cmd_metric(fs_index: Dict, metrics: List[str]) -> Any:
    """Extract one or more metrics by name."""
    if len(metrics) == 1:
        item = find_line_item(fs_index, metrics[0])
        if item is None:
            return {
                "label": metrics[0],
                "value": None,
                "message": f"'{metrics[0]}' not found in fs_index. Use --list to see available fields, or --text-search for qualitative data."
            }
        # Find the actual key
        for key, val in fs_index["line_items"].items():
            if val is item:
                return format_metric(key, val)
        return format_metric(metrics[0], item)
    else:
        results = []
        for m in metrics:
            item = find_line_item(fs_index, m)
            if item is None:
                results.append({"label": m, "value": None, "message": f"'{m}' not found"})
            else:
                for key, val in fs_index["line_items"].items():
                    if val is item:
                        results.append(format_metric(key, val))
                        break
        return results


def cmd_category(fs_index: Dict, category: str) -> List[Dict]:
    """Extract all metrics from a statement category."""
    items = fs_index.get('line_items', {})
    results = []
    for key, item in items.items():
        if item.get("statement", "").lower() == category.lower():
            results.append(format_metric(key, item))
    return results


def cmd_search(fs_index: Dict, keyword: str) -> List[Dict]:
    """Search line items by keyword."""
    items = fs_index.get('line_items', {})
    results = []
    for key, item in items.items():
        if keyword.lower() in key.lower() or keyword.lower() in item.get("label", "").lower():
            results.append(format_metric(key, item))
    return results


def cmd_list(fs_index: Dict) -> Dict[str, List[str]]:
    """List all available fields grouped by statement."""
    items = fs_index.get('line_items', {})
    by_statement = {}
    for key, item in items.items():
        stmt = item.get("statement", "unknown")
        if stmt not in by_statement:
            by_statement[stmt] = []
        by_statement[stmt].append(item.get("label", key))
    # Deduplicate while preserving order
    for stmt in by_statement:
        seen = set()
        deduped = []
        for label in by_statement[stmt]:
            if label not in seen:
                seen.add(label)
                deduped.append(label)
        by_statement[stmt] = deduped
    return by_statement


def cmd_text_search(fs_index_path: str, query: str, top: int = 20) -> List[Dict]:
    """Search text_blocks.jsonl for a keyword."""
    blocks = load_text_blocks(fs_index_path)
    query_lower = query.lower()
    results = []
    for block in blocks:
        text = block.get("text", "")
        if query_lower in text.lower():
            results.append({
                "page_number": block.get("page_number"),
                "text": text[:500],  # Truncate for readability
                "match": query,
            })
    return results[:top]


def cmd_text_page(fs_index_path: str, page_range: str) -> List[Dict]:
    """Extract text blocks from a page range (e.g., '45-60')."""
    match = re.match(r'(\d+)\s*-\s*(\d+)', page_range)
    if not match:
        print(f"Error: Invalid page range '{page_range}'. Use format: 45-60", file=sys.stderr)
        sys.exit(1)
    start, end = int(match.group(1)), int(match.group(2))
    blocks = load_text_blocks(fs_index_path)
    results = []
    for block in blocks:
        page = block.get("page_number")
        if page and start <= page <= end:
            results.append({
                "page_number": page,
                "text": block.get("text", ""),
            })
    return results


def main():
    parser = argparse.ArgumentParser(description="Extract financial data from fs_index.json")
    parser.add_argument("fs_index", help="Path to fs_index.json")
    parser.add_argument("--metric", nargs="+", help="Extract specific metric(s)")
    parser.add_argument("--category", help="Extract all metrics from a statement (income_statement, balance_sheet, cash_flow)")
    parser.add_argument("--search", help="Search line items by keyword")
    parser.add_argument("--list", action="store_true", help="List all available fields")
    parser.add_argument("--text-search", help="Search annual report text for a keyword")
    parser.add_argument("--text-page", help="Extract text from page range (e.g., 45-60)")
    parser.add_argument("--top", type=int, default=20, help="Max results for text search (default: 20)")

    args = parser.parse_args()

    if not Path(args.fs_index).exists():
        print(f"Error: {args.fs_index} not found", file=sys.stderr)
        sys.exit(1)

    fs_index = load_fs_index(args.fs_index)

    # Determine which command to run
    if args.metric:
        result = cmd_metric(fs_index, args.metric)
    elif args.category:
        result = cmd_category(fs_index, args.category)
    elif args.search:
        result = cmd_search(fs_index, args.search)
    elif args.list:
        result = cmd_list(fs_index)
    elif args.text_search:
        result = cmd_text_search(args.fs_index, args.text_search, args.top)
    elif args.text_page:
        result = cmd_text_page(args.fs_index, args.text_page)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/skills/financial-analysis-report/test_data_extractor.py -v`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add skills/financial-analysis-report/scripts/data_extractor.py tests/skills/financial-analysis-report/test_data_extractor.py
git commit -m "refactor(skill): rewrite data_extractor.py as clean CLI tool"
```

---

## Chunk 2: financial_calculator.py

### Task 3: Write tests for financial_calculator CLI

**Files:**
- Create: `tests/skills/financial-analysis-report/test_financial_calculator.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for financial_calculator CLI tool."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent.parent.parent / "skills" / "financial-analysis-report" / "scripts" / "financial_calculator.py"


def _run(args):
    result = subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    return json.loads(result.stdout)


def _make_fs_index():
    return {
        "currency": "MYR",
        "fiscal_year_end": "2024-12-31",
        "company_name": "TEST",
        "line_items": {
            "revenue": {"group_current": 1000000, "group_prior": 800000},
            "gross profit": {"group_current": 400000, "group_prior": 320000},
            "profit before tax": {"group_current": 200000, "group_prior": 150000},
            "profit for the financial year": {"group_current": 160000, "group_prior": 120000},
            "profit for the financial year attributable to: owners of the parent": {
                "group_current": 140000, "group_prior": 100000
            },
            "equity attributable to owners of the parent": {
                "group_current": 700000, "group_prior": 600000
            },
            "current assets": {"group_current": 500000, "group_prior": 400000},
            "current liabilities": {"group_current": 300000, "group_prior": 250000},
            "inventories": {"group_current": 100000, "group_prior": 80000},
            "cash and bank balances": {"group_current": 150000, "group_prior": 120000},
            "total assets": {"group_current": 1500000, "group_prior": 1200000},
            "total liabilities": {"group_current": 700000, "group_prior": 550000},
            "trade receivables": {"group_current": 80000, "group_prior": 60000},
            "trade payables": {"group_current": 90000, "group_prior": 70000},
            "bank borrowings": {"group_current": 200000, "group_prior": 150000},
            "net cash from operating activities": {"group_current": 180000, "group_prior": 130000},
            "net cash from/(used in) investing activities": {"group_current": -50000, "group_prior": -40000},
            "finance costs": {"group_current": 30000, "group_prior": 25000},
            "basic and diluted earnings per share (sen)": {"group_current": 28.0, "group_prior": 20.0},
        }
    }


class TestAllRatios:
    def test_returns_all_categories(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs)])
        assert "profitability" in result
        assert "liquidity" in result
        assert "solvency" in result
        assert "efficiency" in result
        assert "cashflow" in result

    def test_profitability_ratios(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--category", "profitability"])
        assert "gross_margin" in result
        assert abs(result["gross_margin"] - 40.0) < 0.1  # 400k/1000k

    def test_liquidity_ratios(self, tmp_path):
        fs = tmp_path / "fs_index.json"
        fs.write_text(json.dumps(_make_fs_index()))
        result = _run([str(fs), "--category", "liquidity"])
        assert "current_ratio" in result
        assert abs(result["current_ratio"] - 1.667) < 0.01  # 500k/300k


class TestYoYGrowth:
    def test_yoy_growth(self, tmp_path):
        fs_current = tmp_path / "fs_index.json"
        fs_current.write_text(json.dumps(_make_fs_index()))
        fs_prior = tmp_path / "fs_prior.json"
        prior = _make_fs_index()
        # Swap current/prior values
        for item in prior["line_items"].values():
            item["group_current"] = item.get("group_prior", 0)
        fs_prior.write_text(json.dumps(prior))

        result = _run([str(fs_current), "--prior", str(fs_prior)])
        assert "yoy_growth" in result
        assert "revenue" in result["yoy_growth"]
        # Revenue grew from 800k to 1000k = 25%
        assert abs(result["yoy_growth"]["revenue"]["growth_rate"] - 25.0) < 0.1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/skills/financial-analysis-report/test_financial_calculator.py -v`
Expected: FAIL

### Task 4: Rewrite financial_calculator.py

**Files:**
- Rewrite: `skills/financial-analysis-report/scripts/financial_calculator.py`

- [ ] **Step 1: Rewrite the script**

Keep the existing calculation functions (they're well-written) but replace the CLI interface. The existing `main()` function uses argparse — keep that pattern but clean up. Key changes:
- Remove `format_ratio_table()` and markdown output mode (model doesn't need formatted tables, it needs JSON)
- Keep all `calculate_*` functions as-is
- Simplify CLI to: `[fs_index] [--category CAT] [--prior FILE] [--trend YEAR:FILE...]`
- Output is always JSON

- [ ] **Step 2: Run tests**

Run: `pytest tests/skills/financial-analysis-report/test_financial_calculator.py -v`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add skills/financial-analysis-report/scripts/financial_calculator.py tests/skills/financial-analysis-report/test_financial_calculator.py
git commit -m "refactor(skill): rewrite financial_calculator.py as clean CLI tool"
```

---

## Chunk 3: validate_report.py

### Task 5: Write tests for enhanced validator

**Files:**
- Rewrite: `tests/skills/financial-analysis-report/test_validate_report.py`

- [ ] **Step 1: Write failing tests**

Keep existing tests (they're good) and add new tests for UNVERIFIABLE detection:

```python
def test_unverifiable_numbers_flagged(self):
    """Numbers that can't be traced to any data source should be flagged."""
    # This requires the validator to also check text (not just tables)
    # for specific number patterns that look like financial data claims
    pass  # Will be fleshed out during implementation
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py -v`
Expected: FAIL (new tests fail)

### Task 6: Rewrite validate_report.py

**Files:**
- Rewrite: `skills/financial-analysis-report/scripts/validate_report.py`

- [ ] **Step 1: Enhance the validator**

Keep existing `validate_data_accuracy` and `validate_calculations` functions. Add:
- `detect_unverifiable_claims()` — scan report text for specific numeric claims (e.g., "customer concentration at 35%") that don't match any fs_index data and aren't text-search results
- Improve number extraction to handle both tables AND inline text (e.g., "Revenue grew 58% to RM3.25b")
- Output format: JSON with `verified`, `mismatch`, `unverifiable` arrays

- [ ] **Step 2: Run tests**

Run: `pytest tests/skills/financial-analysis-report/test_validate_report.py -v`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add skills/financial-analysis-report/scripts/validate_report.py tests/skills/financial-analysis-report/test_validate_report.py
git commit -m "refactor(skill): enhance validate_report.py with unverifiable detection"
```

---

## Chunk 4: References and SKILL.md

### Task 7: Create data_catalog.md

**Files:**
- Create: `skills/financial-analysis-report/references/data_catalog.md`

- [ ] **Step 1: Generate catalog from actual fs_index data**

Run this script to generate the catalog from the real data:

```bash
python3 -c "
import json
from pathlib import Path

fs = json.loads(Path('output/CHINHIN/2024/fs_index.json').read_text())
items = fs['line_items']

# Group by statement
by_stmt = {}
for key, val in items.items():
    stmt = val.get('statement', 'unknown')
    label = val.get('label', key)
    if stmt not in by_stmt:
        by_stmt[stmt] = []
    if label not in [x[0] for x in by_stmt[stmt]]:
        by_stmt[stmt].append((label, key))

for stmt in sorted(by_stmt.keys()):
    print(f'### {stmt.replace(\"_\", \" \").title()} ({len(by_stmt[stmt])} items)')
    print()
    print('| Label | fs_index key |')
    print('|---|---|')
    for label, key in sorted(by_stmt[stmt]):
        print(f'| {label} | `{key}` |')
    print()
"
```

Use the output to build the catalog file. Add the unit system section and calculable ratios section manually.

- [ ] **Step 2: Commit**

```bash
git add skills/financial-analysis-report/references/data_catalog.md
git commit -m "docs(skill): add data catalog reference"
```

### Task 8: Create writing_guidelines.md

**Files:**
- Create: `skills/financial-analysis-report/references/writing_guidelines.md`

- [ ] **Step 1: Merge and trim existing guidelines**

Merge from existing `tone_guidelines.md` + `writing_standards.md` + `precision_quick_reference.md`. Trim to ~150 lines. Keep:
- Precision rules (calculate from raw, round only for display)
- Unit conventions (RM'000 → RM xxx million, sen → RM, pp, bps)
- Tone principles (professional, specific, explain WHY)
- Anti-patterns (over-hedging, emotional language, generic statements)
- Word replacement table

Remove:
- Section-specific tone guidance (no fixed sections)
- Data bundle format section (no bundles)
- Worker checklist section (no workers)

- [ ] **Step 2: Commit**

```bash
git add skills/financial-analysis-report/references/writing_guidelines.md
git commit -m "docs(skill): add merged writing guidelines reference"
```

### Task 9: Rewrite SKILL.md

**Files:**
- Rewrite: `skills/financial-analysis-report/SKILL.md`

- [ ] **Step 1: Write minimal SKILL.md**

~70 lines. Structure:
1. Frontmatter (name + description — keep triggering description similar to current)
2. One-paragraph intro
3. Tools section (data_extractor + financial_calculator + validate_report with all flags)
4. Anti-fabrication rule
5. Workflow (5 steps, no fixed structure)
6. References (data_catalog.md + writing_guidelines.md)

- [ ] **Step 2: Commit**

```bash
git add skills/financial-analysis-report/SKILL.md
git commit -m "refactor(skill): rewrite SKILL.md for dynamic architecture"
```

---

## Chunk 5: Cleanup

### Task 10: Delete obsolete files

- [ ] **Step 1: Delete all worker instruction files and old scripts**

```bash
cd skills/financial-analysis-report

# Delete worker instructions
rm references/worker_1_context_setup.md
rm references/worker_2_core_performance.md
rm references/worker_3_business_analysis.md
rm references/worker_4_profitability_health.md
rm references/worker_5_risk.md
rm references/worker_6_cashflow_outlook.md
rm references/worker_7_summary.md

# Delete obsolete references
rm references/canonical_data_registry.md
rm references/output_format_specification.md
rm references/manual_workflow.md
rm references/troubleshooting.md
rm references/quick_start_examples.md
rm references/data_format.md

# Delete obsolete scripts
rm scripts/generate_report.py
rm scripts/assemble_report.py
rm scripts/extract_worker_bundle.py
rm scripts/prepare_workspace.py
rm scripts/generate_summary.py
rm scripts/example_worker_extraction.py
rm scripts/dashboard_generator.py
```

- [ ] **Step 2: Verify skill structure**

```bash
find skills/financial-analysis-report -type f | sort
```

Expected:
```
SKILL.md
references/data_catalog.md
references/writing_guidelines.md
scripts/data_extractor.py
scripts/financial_calculator.py
scripts/validate_report.py
```

- [ ] **Step 3: Run all tests**

Run: `pytest tests/skills/financial-analysis-report/ -v`
Expected: ALL PASS

- [ ] **Step 4: Commit cleanup**

```bash
git add -A skills/financial-analysis-report/
git commit -m "refactor(skill): remove obsolete worker files and fixed workflow scripts"
```

---

## Chunk 6: Integration Test

### Task 11: Smoke test the new skill end-to-end

- [ ] **Step 1: Test data_extractor against real data**

```bash
python skills/financial-analysis-report/scripts/data_extractor.py output/CHINHIN/2024/fs_index.json --metric revenue
python skills/financial-analysis-report/scripts/data_extractor.py output/CHINHIN/2024/fs_index.json --category income_statement
python skills/financial-analysis-report/scripts/data_extractor.py output/CHINHIN/2024/fs_index.json --list
python skills/financial-analysis-report/scripts/data_extractor.py output/CHINHIN/2024/fs_index.json --search "borrowing"
python skills/financial-analysis-report/scripts/data_extractor.py output/CHINHIN/2024/fs_index.json --text-search "management"
```

Verify each returns valid JSON with source traceability.

- [ ] **Step 2: Test financial_calculator against real data**

```bash
python skills/financial-analysis-report/scripts/financial_calculator.py output/CHINHIN/2024/fs_index.json
python skills/financial-analysis-report/scripts/financial_calculator.py output/CHINHIN/2024/fs_index.json --category profitability
python skills/financial-analysis-report/scripts/financial_calculator.py output/CHINHIN/2024/fs_index.json --prior output/CHINHIN/2023/fs_index.json
```

Verify ratios are reasonable.

- [ ] **Step 3: Run full test suite**

Run: `pytest tests/skills/financial-analysis-report/ -v`
Expected: ALL PASS

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "refactor(skill): complete v2 dynamic architecture migration"
```
