"""Tests for data_extractor CLI tool."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent.parent.parent / "skills" / "financial-analysis-report" / "scripts" / "data_extractor.py"

SAMPLE_FS_INDEX = {
    "currency": "MYR",
    "fiscal_year_end": "2024-12-31",
    "company_name": "CHINHIN",
    "line_items": {
        "revenue": {
            "label": "Revenue",
            "statement": "income_statement",
            "section": "revenue",
            "page": 148,
            "group_current": 3252347,
            "group_prior": 2057210,
            "company_current": 3252347,
            "company_prior": 2057210,
        },
        "gross profit": {
            "label": "Gross Profit",
            "statement": "income_statement",
            "section": "gross_profit",
            "page": 148,
            "group_current": 502100,
            "group_prior": 380200,
            "company_current": 502100,
            "company_prior": 380200,
        },
        "profit before tax": {
            "label": "Profit Before Tax",
            "statement": "income_statement",
            "section": "profit_before_tax",
            "page": 148,
            "group_current": 276500,
            "group_prior": 189300,
            "company_current": 276500,
            "company_prior": 189300,
        },
        "total assets": {
            "label": "Total Assets",
            "statement": "balance_sheet",
            "section": "assets",
            "page": 146,
            "group_current": 5500000,
            "group_prior": 4800000,
            "company_current": 5500000,
            "company_prior": 4800000,
        },
        "total liabilities": {
            "label": "Total Liabilities",
            "statement": "balance_sheet",
            "section": "liabilities",
            "page": 146,
            "group_current": 3200000,
            "group_prior": 2800000,
            "company_current": 3200000,
            "company_prior": 2800000,
        },
        "total equity": {
            "label": "Total Equity",
            "statement": "balance_sheet",
            "section": "equity",
            "page": 146,
            "group_current": 2300000,
            "group_prior": 2000000,
            "company_current": 2300000,
            "company_prior": 2000000,
        },
        "cash and bank balances": {
            "label": "Cash and Bank Balances",
            "statement": "balance_sheet",
            "section": "current_assets",
            "page": 147,
            "group_current": 410000,
            "group_prior": 350000,
            "company_current": 410000,
            "company_prior": 350000,
        },
        "net cash from operating activities": {
            "label": "Net Cash from Operating Activities",
            "statement": "cash_flow",
            "section": "operating",
            "page": 155,
            "group_current": 200000,
            "group_prior": 150000,
            "company_current": 200000,
            "company_prior": 150000,
        },
        "net cash from investing activities": {
            "label": "Net Cash from Investing Activities",
            "statement": "cash_flow",
            "section": "investing",
            "page": 155,
            "group_current": -180000,
            "group_prior": -120000,
            "company_current": -180000,
            "company_prior": -120000,
        },
        "net cash from financing activities": {
            "label": "Net Cash from Financing Activities",
            "statement": "cash_flow",
            "section": "financing",
            "page": 155,
            "group_current": -30000,
            "group_prior": -20000,
            "company_current": -30000,
            "company_prior": -20000,
        },
        # Item with duplicate label (e.g., parenthetical disambiguation)
        "property, plant and equipment (non-current assets)": {
            "label": "Property, plant and equipment",
            "statement": "balance_sheet",
            "section": "non_current_assets",
            "page": 148,
            "group_current": 604008,
            "group_prior": 575840,
            "company_current": 1332,
            "company_prior": 1064,
        },
        "property, plant and equipment": {
            "label": "Property, plant and equipment",
            "statement": "balance_sheet",
            "section": "non_current_assets",
            "page": 148,
            "group_current": 604008,
            "group_prior": 575840,
            "company_current": 1332,
            "company_prior": 1064,
        },
    },
}

SAMPLE_TEXT_BLOCKS = [
    {"id": "text-001", "page_number": 10, "text": "Revenue increased by 58% driven by strong construction demand."},
    {"id": "text-002", "page_number": 10, "text": "Gross margin improved to 15.4% from 18.5%."},
    {"id": "text-003", "page_number": 45, "text": "Management Discussion and Analysis begins here."},
    {"id": "text-004", "page_number": 50, "text": "The Group focuses on sustainable construction practices."},
    {"id": "text-005", "page_number": 60, "text": "Risk factors include currency fluctuation and regulatory changes."},
    {"id": "text-006", "page_number": 61, "text": "The company has a strong order book of RM 2.1 billion."},
]


def _run(args, fs_index=SAMPLE_FS_INDEX, text_blocks=None):
    """Helper: write temp files and run the CLI, returning parsed JSON from stdout."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fs_path = os.path.join(tmpdir, "fs_index.json")
        with open(fs_path, "w") as f:
            json.dump(fs_index, f)

        if text_blocks is not None:
            tb_path = os.path.join(tmpdir, "text_blocks.jsonl")
            with open(tb_path, "w") as f:
                for block in text_blocks:
                    f.write(json.dumps(block) + "\n")

        cmd = [sys.executable, str(SCRIPT), fs_path] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            raise RuntimeError(
                f"CLI failed (rc={result.returncode})\n"
                f"  stdout: {result.stdout[:500]}\n"
                f"  stderr: {result.stderr[:500]}"
            )
        return json.loads(result.stdout)


def _run_fail(args, fs_index=SAMPLE_FS_INDEX, text_blocks=None):
    """Helper: run CLI expecting failure. Returns (returncode, stdout, stderr)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fs_path = os.path.join(tmpdir, "fs_index.json")
        with open(fs_path, "w") as f:
            json.dump(fs_index, f)

        if text_blocks is not None:
            tb_path = os.path.join(tmpdir, "text_blocks.jsonl")
            with open(tb_path, "w") as f:
                for block in text_blocks:
                    f.write(json.dumps(block) + "\n")

        cmd = [sys.executable, str(SCRIPT), fs_path] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.returncode, result.stdout, result.stderr


# ── --metric ──────────────────────────────────────────────────────────────────

class TestMetric:
    def test_exact_match(self):
        out = _run(["--metric", "revenue"])
        assert out["source"] == "revenue"
        assert out["label"] == "Revenue"
        assert out["group_current"] == 3252347
        assert out["group_prior"] == 2057210
        assert out["statement"] == "income_statement"

    def test_substring_match(self):
        """If no exact match, substring match should work."""
        out = _run(["--metric", "profit before tax"])
        # Exact match for "profit before tax"
        assert out["group_current"] == 276500
        assert "source" in out

    def test_substring_match_partial(self):
        """Substring 'gross profit' should match the gross profit item."""
        out = _run(["--metric", "gross profit"])
        assert out["group_current"] == 502100
        assert out["source"] == "gross profit"

    def test_multiple_metrics(self):
        out = _run(["--metric", "revenue", "--metric", "total assets"])
        assert isinstance(out, dict)
        assert "revenue" in out
        # Key is "total assets" (the fs_index key), not "total_assets"
        assert "total assets" in out
        assert out["revenue"]["group_current"] == 3252347
        assert out["total assets"]["group_current"] == 5500000

    def test_not_found_returns_null(self):
        out = _run(["--metric", "nonexistent_metric_xyz"])
        assert out["value"] is None
        assert "guidance" in out
        assert out["source"] == "nonexistent_metric_xyz"

    def test_metric_includes_page(self):
        out = _run(["--metric", "revenue"])
        assert out["page"] == 148


# ── --category ────────────────────────────────────────────────────────────────

class TestCategory:
    def test_income_statement(self):
        out = _run(["--category", "income_statement"])
        assert isinstance(out, dict)
        assert "_metadata" in out
        # Verify all line items (not _metadata) are income_statement
        for key, val in out.items():
            if key == "_metadata":
                continue
            assert val.get("statement") == "income_statement", f"{key} is not income_statement"

    def test_balance_sheet(self):
        out = _run(["--category", "balance_sheet"])
        assert isinstance(out, dict)
        assert "_metadata" in out
        for key, val in out.items():
            if key == "_metadata":
                continue
            assert val.get("statement") == "balance_sheet", f"{key} is not balance_sheet"

    def test_cash_flow(self):
        out = _run(["--category", "cash_flow"])
        assert isinstance(out, dict)
        for key, val in out.items():
            if key.startswith("_"):
                continue
            assert val.get("statement") == "cash_flow", f"{key} is not cash_flow"

    def test_category_metadata(self):
        out = _run(["--category", "income_statement"])
        meta = out["_metadata"]
        assert meta["currency"] == "MYR"
        assert meta["fiscal_year_end"] == "2024-12-31"
        assert meta["company_name"] == "CHINHIN"
        assert meta["count"] > 0


# ── --search ──────────────────────────────────────────────────────────────────

class TestSearch:
    def test_search_finds_matching_items(self):
        out = _run(["--search", "profit"])
        assert isinstance(out, dict)
        assert out["query"] == "profit"
        assert out["count"] > 0
        assert "results" in out
        labels = [r["label"] for r in out["results"]]
        assert "Profit Before Tax" in labels

    def test_search_no_results(self):
        out = _run(["--search", "zzzzz_nonexistent"])
        assert out["count"] == 0
        assert out["results"] == []

    def test_search_returns_key_and_label(self):
        out = _run(["--search", "cash"])
        for r in out["results"]:
            assert "key" in r
            assert "label" in r
            assert "statement" in r


# ── --list ────────────────────────────────────────────────────────────────────

class TestList:
    def test_list_groups_by_statement(self):
        out = _run(["--list"])
        assert "income_statement" in out
        assert "balance_sheet" in out
        assert "cash_flow" in out

    def test_list_deduplicates_labels(self):
        out = _run(["--list"])
        for statement, items in out.items():
            if isinstance(items, list):
                labels = [i["label"] for i in items]
                assert len(labels) == len(set(labels)), f"Duplicate labels in {statement}"

    def test_list_items_have_key_and_label(self):
        out = _run(["--list"])
        for statement, items in out.items():
            if isinstance(items, list):
                for item in items:
                    assert "key" in item
                    assert "label" in item


# ── --text-search ─────────────────────────────────────────────────────────────

class TestTextSearch:
    def test_text_search_finds_keyword(self):
        out = _run(["--text-search", "Revenue"], text_blocks=SAMPLE_TEXT_BLOCKS)
        assert out["query"] == "Revenue"
        assert out["count"] > 0
        assert any("Revenue" in r["text"] for r in out["results"])

    def test_text_search_case_insensitive(self):
        out = _run(["--text-search", "revenue"], text_blocks=SAMPLE_TEXT_BLOCKS)
        assert out["count"] > 0

    def test_text_search_no_results(self):
        out = _run(["--text-search", "zzzzz_nonexistent"], text_blocks=SAMPLE_TEXT_BLOCKS)
        assert out["count"] == 0

    def test_text_search_includes_page_number(self):
        out = _run(["--text-search", "sustainable"], text_blocks=SAMPLE_TEXT_BLOCKS)
        for r in out["results"]:
            assert "page_number" in r

    def test_text_search_no_text_blocks_file(self):
        """If text_blocks.jsonl doesn't exist, return empty results with warning."""
        # Do not pass text_blocks -> no file created
        out = _run(["--text-search", "revenue"])
        assert out["count"] == 0
        assert "warning" in out


# ── --text-page ───────────────────────────────────────────────────────────────

class TestTextPage:
    def test_page_range(self):
        out = _run(["--text-page", "45-60"], text_blocks=SAMPLE_TEXT_BLOCKS)
        assert isinstance(out, dict)
        assert "pages" in out
        assert out["count"] > 0
        for r in out["results"]:
            assert 45 <= r["page_number"] <= 60

    def test_single_page(self):
        out = _run(["--text-page", "10"], text_blocks=SAMPLE_TEXT_BLOCKS)
        for r in out["results"]:
            assert r["page_number"] == 10

    def test_page_range_no_results(self):
        out = _run(["--text-page", "1-5"], text_blocks=SAMPLE_TEXT_BLOCKS)
        assert out["count"] == 0

    def test_text_page_no_file(self):
        out = _run(["--text-page", "45-60"])
        assert out["count"] == 0
        assert "warning" in out


# ── Error handling ────────────────────────────────────────────────────────────

class TestErrors:
    def test_no_args_returns_usage(self):
        rc, stdout, stderr = _run_fail([])
        assert rc != 0
        # Should show usage info
        assert "usage" in stderr.lower() or "usage" in stdout.lower()

    def test_nonexistent_fs_index(self):
        rc, stdout, stderr = _run_fail(["--metric", "revenue"], fs_index={})
        # We pass empty fs_index but the file is valid JSON, so it should work
        # For truly nonexistent file, test differently
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = [sys.executable, str(SCRIPT), os.path.join(tmpdir, "nonexistent.json"), "--metric", "revenue"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            assert result.returncode != 0

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_path = os.path.join(tmpdir, "bad.json")
            with open(bad_path, "w") as f:
                f.write("not json{{{")
            cmd = [sys.executable, str(SCRIPT), bad_path, "--metric", "revenue"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            assert result.returncode != 0


# ── Output format ─────────────────────────────────────────────────────────────

class TestOutputFormat:
    def test_output_is_valid_json(self):
        out = _run(["--metric", "revenue"])
        assert isinstance(out, dict)

    def test_output_has_source_traceability(self):
        out = _run(["--metric", "revenue"])
        assert "source" in out
        assert out["source"] == "revenue"

    def test_list_output_valid_json(self):
        out = _run(["--list"])
        assert isinstance(out, dict)

    def test_category_output_valid_json(self):
        out = _run(["--category", "income_statement"])
        assert isinstance(out, dict)
