"""Tests for financial_calculator CLI tool."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).parent.parent.parent.parent
    / "skills"
    / "financial-analysis-report"
    / "scripts"
    / "financial_calculator.py"
)


def _make_fs_index():
    """Create a minimal fs_index fixture with known values for ratio testing."""
    return {
        "currency": "MYR",
        "fiscal_year_end": "2024-12-31",
        "company_name": "TEST",
        "line_items": {
            "revenue": {"group_current": 1_000_000, "group_prior": 800_000},
            "gross profit": {"group_current": 400_000, "group_prior": 320_000},
            "profit before tax": {"group_current": 200_000, "group_prior": 150_000},
            "profit for the financial year": {"group_current": 160_000, "group_prior": 120_000},
            "profit for the financial year attributable to: owners of the parent": {
                "group_current": 140_000,
                "group_prior": 100_000,
            },
            "equity attributable to owners of the parent": {
                "group_current": 700_000,
                "group_prior": 600_000,
            },
            "current assets": {"group_current": 500_000, "group_prior": 400_000},
            "current liabilities": {"group_current": 300_000, "group_prior": 250_000},
            "inventories": {"group_current": 100_000, "group_prior": 80_000},
            "cash and bank balances": {"group_current": 150_000, "group_prior": 120_000},
            "total assets": {"group_current": 1_500_000, "group_prior": 1_200_000},
            "total liabilities": {"group_current": 700_000, "group_prior": 550_000},
            "trade receivables": {"group_current": 80_000, "group_prior": 60_000},
            "trade payables": {"group_current": 90_000, "group_prior": 70_000},
            "bank borrowings": {"group_current": 200_000, "group_prior": 150_000},
            "net cash from operating activities": {"group_current": 180_000, "group_prior": 130_000},
            "net cash from/(used in) investing activities": {"group_current": -50_000, "group_prior": -40_000},
            "finance costs": {"group_current": 30_000, "group_prior": 25_000},
            "basic and diluted earnings per share (sen)": {"group_current": 28.0, "group_prior": 20.0},
        },
    }


def _make_prior_fs_index():
    """Create a prior year fs_index fixture (2023)."""
    return {
        "currency": "MYR",
        "fiscal_year_end": "2023-12-31",
        "company_name": "TEST",
        "line_items": {
            "revenue": {"group_current": 800_000, "group_prior": 700_000},
            "gross profit": {"group_current": 320_000, "group_prior": 280_000},
            "profit before tax": {"group_current": 150_000, "group_prior": 130_000},
            "profit for the financial year": {"group_current": 120_000, "group_prior": 100_000},
            "profit for the financial year attributable to: owners of the parent": {
                "group_current": 100_000,
                "group_prior": 80_000,
            },
            "equity attributable to owners of the parent": {
                "group_current": 600_000,
                "group_prior": 520_000,
            },
            "current assets": {"group_current": 400_000, "group_prior": 350_000},
            "current liabilities": {"group_current": 250_000, "group_prior": 220_000},
            "inventories": {"group_current": 80_000, "group_prior": 70_000},
            "cash and bank balances": {"group_current": 120_000, "group_prior": 100_000},
            "total assets": {"group_current": 1_200_000, "group_prior": 1_000_000},
            "total liabilities": {"group_current": 550_000, "group_prior": 450_000},
            "trade receivables": {"group_current": 60_000, "group_prior": 50_000},
            "trade payables": {"group_current": 70_000, "group_prior": 60_000},
            "bank borrowings": {"group_current": 150_000, "group_prior": 130_000},
            "net cash from operating activities": {"group_current": 130_000, "group_prior": 110_000},
            "net cash from/(used in) investing activities": {"group_current": -40_000, "group_prior": -30_000},
            "finance costs": {"group_current": 25_000, "group_prior": 22_000},
        },
    }


def _run(args, fs_index=None, prior_index=None, extra_files=None):
    """Helper: write temp files and run the CLI, returning parsed JSON from stdout."""
    fs_index = fs_index or _make_fs_index()
    with tempfile.TemporaryDirectory() as tmpdir:
        fs_path = os.path.join(tmpdir, "fs_index.json")
        with open(fs_path, "w") as f:
            json.dump(fs_index, f)

        cmd = [sys.executable, str(SCRIPT), fs_path] + args

        if prior_index is not None:
            prior_path = os.path.join(tmpdir, "prior.json")
            with open(prior_path, "w") as f:
                json.dump(prior_index, f)
            cmd += ["--prior", prior_path]

        if extra_files:
            for i, ef in enumerate(extra_files):
                ep = os.path.join(tmpdir, f"extra_{i}.json")
                with open(ep, "w") as f:
                    json.dump(ef, f)
                # Replace placeholder in --trend args with actual path
                cmd = [c.replace(f"extra_{i}.json", ep) for c in cmd]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            raise RuntimeError(
                f"CLI failed (rc={result.returncode})\n"
                f"  stdout: {result.stdout[:500]}\n"
                f"  stderr: {result.stderr[:500]}"
            )
        return json.loads(result.stdout)


def _run_fail(args, fs_index=None):
    """Helper: run CLI expecting failure. Returns (returncode, stdout, stderr)."""
    fs_index = fs_index or _make_fs_index()
    with tempfile.TemporaryDirectory() as tmpdir:
        fs_path = os.path.join(tmpdir, "fs_index.json")
        with open(fs_path, "w") as f:
            json.dump(fs_index, f)

        cmd = [sys.executable, str(SCRIPT), fs_path] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.returncode, result.stdout, result.stderr


# ── Default (all ratios) ─────────────────────────────────────────────────────

class TestAllRatios:
    def test_returns_all_categories(self):
        out = _run([])
        assert "profitability" in out
        assert "liquidity" in out
        assert "solvency" in out
        assert "efficiency" in out
        assert "cashflow" in out

    def test_no_yoy_growth_without_prior(self):
        out = _run([])
        assert "yoy_growth" not in out
        assert "ratio_changes" not in out
        assert "trends" not in out

    def test_output_is_valid_json(self):
        out = _run([])
        assert isinstance(out, dict)


# ── Profitability ─────────────────────────────────────────────────────────────

class TestProfitability:
    def test_gross_margin(self):
        out = _run(["--category", "profitability"])
        # gross_profit / revenue * 100 = 400000 / 1000000 * 100 = 40.0
        assert out["gross_margin"] == pytest.approx(40.0)

    def test_pbt_margin(self):
        out = _run(["--category", "profitability"])
        # 200000 / 1000000 * 100 = 20.0
        assert out["pbt_margin"] == pytest.approx(20.0)

    def test_pat_margin(self):
        out = _run(["--category", "profitability"])
        # 160000 / 1000000 * 100 = 16.0
        assert out["pat_margin"] == pytest.approx(16.0)

    def test_attributable_margin(self):
        out = _run(["--category", "profitability"])
        # 140000 / 1000000 * 100 = 14.0
        assert out["attributable_margin"] == pytest.approx(14.0)

    def test_roe(self):
        out = _run(["--category", "profitability"])
        # 140000 / 700000 * 100 = 20.0
        assert out["roe"] == pytest.approx(20.0)

    def test_roa(self):
        out = _run(["--category", "profitability"])
        # 140000 / 1500000 * 100 = 9.333...
        assert out["roa"] == pytest.approx(140_000 / 1_500_000 * 100)

    def test_category_output_is_flat_dict(self):
        """--category profitability returns flat dict, not nested."""
        out = _run(["--category", "profitability"])
        assert isinstance(out, dict)
        # No nested category keys
        assert "profitability" not in out
        assert "liquidity" not in out


# ── Liquidity ─────────────────────────────────────────────────────────────────

class TestLiquidity:
    def test_current_ratio(self):
        out = _run(["--category", "liquidity"])
        # 500000 / 300000 = 1.666...
        assert out["current_ratio"] == pytest.approx(500_000 / 300_000)

    def test_quick_ratio(self):
        out = _run(["--category", "liquidity"])
        # (500000 - 100000) / 300000 = 1.333...
        assert out["quick_ratio"] == pytest.approx(400_000 / 300_000)

    def test_working_capital(self):
        out = _run(["--category", "liquidity"])
        assert out["working_capital"] == pytest.approx(200_000)

    def test_cash_to_current_assets(self):
        out = _run(["--category", "liquidity"])
        # 150000 / 500000 * 100 = 30.0
        assert out["cash_to_current_assets"] == pytest.approx(30.0)


# ── Solvency ──────────────────────────────────────────────────────────────────

class TestSolvency:
    def test_liabilities_to_assets(self):
        out = _run(["--category", "solvency"])
        # 700000 / 1500000 * 100 = 46.666...
        assert out["liabilities_to_assets"] == pytest.approx(700_000 / 1_500_000 * 100)

    def test_borrowings_to_assets(self):
        out = _run(["--category", "solvency"])
        # 200000 / 1500000 * 100 = 13.333...
        assert out["borrowings_to_assets"] == pytest.approx(200_000 / 1_500_000 * 100)

    def test_net_debt_to_equity(self):
        out = _run(["--category", "solvency"])
        # (200000 - 150000) / 700000 = 0.0714...
        assert out["net_debt_to_equity"] == pytest.approx(50_000 / 700_000)

    def test_equity_to_assets(self):
        out = _run(["--category", "solvency"])
        # 700000 / 1500000 * 100 = 46.666...
        assert out["equity_to_assets"] == pytest.approx(700_000 / 1_500_000 * 100)


# ── Efficiency ────────────────────────────────────────────────────────────────

class TestEfficiency:
    def test_receivables_days(self):
        out = _run(["--category", "efficiency"])
        # 80000 * 365 / 1000000 = 29.2
        assert out["receivables_days"] == pytest.approx(29.2)

    def test_payables_days(self):
        out = _run(["--category", "efficiency"])
        # payables_days = payables * 365 / operating_expenses
        # operating_expenses = cost_of_sales + distribution + admin + other
        # Fixture has no "cost of sales" item, so get_operating_expenses falls back
        # to "operating expenses" which also doesn't exist -> 0.0 -> safe_divide returns 0.0
        assert out["payables_days"] == 0.0

    def test_asset_turnover(self):
        out = _run(["--category", "efficiency"])
        # 1000000 / 1500000 = 0.666...
        assert out["asset_turnover"] == pytest.approx(1_000_000 / 1_500_000)


# ── Cashflow ──────────────────────────────────────────────────────────────────

class TestCashflow:
    def test_ocf_to_revenue(self):
        out = _run(["--category", "cashflow"])
        # 180000 / 1000000 * 100 = 18.0
        assert out["ocf_to_revenue"] == pytest.approx(18.0)

    def test_free_cash_flow(self):
        out = _run(["--category", "cashflow"])
        # ocf - capex = 180000 - 50000 = 130000
        assert out["free_cash_flow"] == pytest.approx(130_000)

    def test_ocf_interest_coverage(self):
        out = _run(["--category", "cashflow"])
        # 180000 / 30000 = 6.0
        assert out["ocf_interest_coverage"] == pytest.approx(6.0)

    def test_ocf_to_debt(self):
        out = _run(["--category", "cashflow"])
        # 180000 / 200000 * 100 = 90.0
        assert out["ocf_to_debt"] == pytest.approx(90.0)


# ── --prior (YoY growth) ─────────────────────────────────────────────────────

class TestPriorYoY:
    def test_yoy_growth_present(self):
        out = _run([], prior_index=_make_prior_fs_index())
        assert "yoy_growth" in out
        assert "ratio_changes" in out

    def test_yoy_growth_revenue(self):
        out = _run([], prior_index=_make_prior_fs_index())
        growth = out["yoy_growth"]
        # Current=1000000, Prior=800000 -> growth = (1000000-800000)/800000*100 = 25.0
        assert growth["Revenue"]["growth_rate"] == pytest.approx(25.0)
        assert growth["Revenue"]["absolute_change"] == pytest.approx(200_000)
        assert growth["Revenue"]["current"] == pytest.approx(1_000_000)
        assert growth["Revenue"]["prior"] == pytest.approx(800_000)

    def test_yoy_growth_pbt(self):
        out = _run([], prior_index=_make_prior_fs_index())
        growth = out["yoy_growth"]
        # (200000-150000)/150000*100 = 33.333...
        assert growth["PBT"]["growth_rate"] == pytest.approx(200_000 / 150_000 * 100 - 100)

    def test_yoy_growth_is_significant(self):
        out = _run([], prior_index=_make_prior_fs_index())
        growth = out["yoy_growth"]
        # Revenue grew 25% > 15% threshold -> significant
        assert growth["Revenue"]["is_significant"] is True

    def test_ratio_changes_present(self):
        out = _run([], prior_index=_make_prior_fs_index())
        changes = out["ratio_changes"]
        assert "profitability" in changes
        assert "liquidity" in changes
        assert "solvency" in changes
        assert "efficiency" in changes
        assert "cashflow" in changes

    def test_ratio_changes_profitability(self):
        out = _run([], prior_index=_make_prior_fs_index())
        changes = out["ratio_changes"]["profitability"]
        assert "gross_margin" in changes
        margin_data = changes["gross_margin"]
        assert "current" in margin_data
        assert "prior" in margin_data
        assert "absolute_change" in margin_data

    def test_all_ratios_still_present_with_prior(self):
        """With --prior, all ratio categories should still be in output."""
        out = _run([], prior_index=_make_prior_fs_index())
        assert "profitability" in out
        assert "liquidity" in out
        assert "solvency" in out
        assert "efficiency" in out
        assert "cashflow" in out


# ── --trend (multi-year) ─────────────────────────────────────────────────────

class TestTrend:
    def test_trends_present(self):
        prior = _make_prior_fs_index()
        extra = {
            "currency": "MYR",
            "fiscal_year_end": "2022-12-31",
            "company_name": "TEST",
            "line_items": {
                "revenue": {"group_current": 700_000, "group_prior": 600_000},
                "gross profit": {"group_current": 280_000, "group_prior": 240_000},
                "profit before tax": {"group_current": 130_000, "group_prior": 110_000},
                "profit for the financial year": {"group_current": 100_000, "group_prior": 85_000},
                "profit for the financial year attributable to: owners of the parent": {
                    "group_current": 80_000,
                    "group_prior": 70_000,
                },
                "equity attributable to owners of the parent": {
                    "group_current": 520_000,
                    "group_prior": 450_000,
                },
                "total assets": {"group_current": 1_000_000, "group_prior": 850_000},
            },
        }
        out = _run(["--trend", "2022:extra_0.json", "2023:extra_1.json"], extra_files=[extra, prior])
        assert "trends" in out

    def test_trend_cagr(self):
        prior = _make_prior_fs_index()
        extra = {
            "currency": "MYR",
            "fiscal_year_end": "2022-12-31",
            "company_name": "TEST",
            "line_items": {
                "revenue": {"group_current": 700_000},
                "total assets": {"group_current": 1_000_000},
            },
        }
        out = _run(["--trend", "2022:extra_0.json", "2023:extra_1.json"], extra_files=[extra, prior])
        trends = out["trends"]
        # Trend datasets: 2022 (revenue=700000) -> 2023 (revenue=800000)
        # CAGR = (800000/700000)^(1/1) - 1 = 14.2857...%
        expected_cagr = ((800_000 / 700_000) - 1) * 100
        assert trends["revenue"]["cagr"] == pytest.approx(expected_cagr, rel=1e-3)

    def test_trend_direction(self):
        prior = _make_prior_fs_index()
        extra = {
            "currency": "MYR",
            "fiscal_year_end": "2022-12-31",
            "company_name": "TEST",
            "line_items": {"revenue": {"group_current": 700_000}},
        }
        out = _run(["--trend", "2022:extra_0.json", "2023:extra_1.json"], extra_files=[extra, prior])
        trends = out["trends"]
        # Revenue CAGR should be > 10% -> "Strong Growth"
        assert trends["revenue"]["direction"] == "Strong Growth"


# ── --category combined with --prior ─────────────────────────────────────────

class TestCategoryWithPrior:
    def test_category_with_prior_returns_flat_dict_plus_growth(self):
        out = _run(
            ["--category", "profitability"],
            prior_index=_make_prior_fs_index(),
        )
        # Category output is flat dict
        assert "gross_margin" in out
        assert "roe" in out
        # Growth info is also present
        assert "yoy_growth" in out

    def test_category_with_prior_growth_has_metrics(self):
        out = _run(
            ["--category", "profitability"],
            prior_index=_make_prior_fs_index(),
        )
        assert "Revenue" in out["yoy_growth"]
        assert "PBT" in out["yoy_growth"]
        assert "PAT" in out["yoy_growth"]


# ── Error handling ────────────────────────────────────────────────────────────

class TestErrors:
    def test_no_args_returns_usage(self):
        """No arguments at all should fail with usage message."""
        cmd = [sys.executable, str(SCRIPT)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        assert result.returncode != 0
        assert "usage" in result.stderr.lower() or "usage" in result.stdout.lower()

    def test_nonexistent_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake = os.path.join(tmpdir, "nonexistent.json")
            cmd = [sys.executable, str(SCRIPT), fake]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            assert result.returncode != 0

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad = os.path.join(tmpdir, "bad.json")
            with open(bad, "w") as f:
                f.write("not json{{{")
            cmd = [sys.executable, str(SCRIPT), bad]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            assert result.returncode != 0

    def test_invalid_category(self):
        rc, stdout, stderr = _run_fail(["--category", "nonexistent_category"])
        assert rc != 0


# ── Missing data (safe defaults) ─────────────────────────────────────────────

class TestMissingData:
    def test_missing_line_items_returns_zeroes(self):
        fs = {"currency": "MYR", "fiscal_year_end": "2024-12-31", "company_name": "EMPTY", "line_items": {}}
        out = _run([], fs_index=fs)
        assert "profitability" in out
        assert out["profitability"]["gross_margin"] == 0.0

    def test_zero_revenue_safe_divide(self):
        fs = _make_fs_index()
        fs["line_items"]["revenue"] = {"group_current": 0, "group_prior": 0}
        out = _run(["--category", "profitability"], fs_index=fs)
        assert out["gross_margin"] == 0.0
