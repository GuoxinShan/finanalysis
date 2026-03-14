# tests/unit/test_report_index.py
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.finanalysis.report_index import ReportIndex
from src.finanalysis.fs_index import FSIndex


def _make_fs_index(company: str, fiscal_year_end: str, items: dict) -> FSIndex:
    idx = FSIndex()
    idx.company_name = company
    idx.fiscal_year_end = fiscal_year_end
    idx.currency = "MYR"
    idx.line_items = items
    return idx


def _write_fs_index(tmp_path: Path, company: str, fiscal_year_end: str, items: dict) -> Path:
    out_dir = tmp_path / f"{company}_{fiscal_year_end[:4]}"
    out_dir.mkdir()
    idx = _make_fs_index(company, fiscal_year_end, items)
    idx.save(out_dir / "fs_index.json")
    return out_dir


@pytest.fixture
def sample_dirs(tmp_path):
    items_2023 = {
        "revenue": {"label": "Revenue", "section": "", "statement": "income_statement",
                    "page": 10, "group_current": 2057210.0, "group_prior": 1800000.0,
                    "company_current": 15000.0, "company_prior": 12000.0},
        "gross profit": {"label": "Gross Profit", "section": "", "statement": "income_statement",
                         "page": 10, "group_current": 188422.0, "group_prior": 150000.0,
                         "company_current": None, "company_prior": None},
    }
    items_2024 = {
        "revenue": {"label": "Revenue", "section": "", "statement": "income_statement",
                    "page": 10, "group_current": 3252347.0, "group_prior": 2057210.0,
                    "company_current": 18353.0, "company_prior": 15000.0},
        "gross profit": {"label": "Gross Profit", "section": "", "statement": "income_statement",
                         "page": 10, "group_current": 525133.0, "group_prior": 188422.0,
                         "company_current": None, "company_prior": None},
    }
    dir_2023 = _write_fs_index(tmp_path, "CHINHIN", "2023-12-31", items_2023)
    dir_2024 = _write_fs_index(tmp_path, "CHINHIN", "2024-12-31", items_2024)
    return dir_2023, dir_2024


def test_add_registers_company_and_year(sample_dirs):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex()
    reg.add(dir_2023)
    reg.add(dir_2024)

    assert reg.companies() == ["CHINHIN"]
    assert reg.years("CHINHIN") == [2023, 2024]


def test_add_missing_dir_returns_none(tmp_path):
    reg = ReportIndex()
    result = reg.add(tmp_path / "nonexistent")
    assert result is None


def test_add_missing_company_name_returns_none(tmp_path):
    out_dir = tmp_path / "no_company"
    out_dir.mkdir()
    idx = FSIndex()
    idx.fiscal_year_end = "2024-12-31"
    idx.line_items = {"revenue": {"group_current": 100.0}}
    idx.save(out_dir / "fs_index.json")

    reg = ReportIndex()
    result = reg.add(out_dir)
    assert result is None


def test_query_returns_correct_values(sample_dirs):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex().add_many([dir_2023, dir_2024])

    result = reg.query("revenue", company="CHINHIN", year=2024)
    assert result is not None
    assert result["group"] == 3252347.0
    assert result["company"] == 18353.0
    assert result["currency"] == "MYR"
    assert result["fiscal_year_end"] == "2024-12-31"


def test_query_case_insensitive(sample_dirs):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex().add_many([dir_2023, dir_2024])

    assert reg.query("revenue", company="chinhin", year=2024) is not None
    assert reg.query("revenue", company="Chinhin", year=2024) is not None


def test_query_unknown_company_returns_none(sample_dirs):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex().add_many([dir_2023, dir_2024])
    assert reg.query("revenue", company="PBBANK", year=2024) is None


def test_query_unknown_year_returns_none(sample_dirs):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex().add_many([dir_2023, dir_2024])
    assert reg.query("revenue", company="CHINHIN", year=2022) is None


def test_query_unknown_label_returns_none(sample_dirs):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex().add_many([dir_2023, dir_2024])
    assert reg.query("nonexistent_metric_xyz", company="CHINHIN", year=2024) is None


def test_query_series_returns_all_years(sample_dirs):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex().add_many([dir_2023, dir_2024])

    series = reg.query_series("revenue", company="CHINHIN")
    assert len(series) == 2
    assert series[0]["year"] == 2023
    assert series[0]["value"] == 2057210.0
    assert series[1]["year"] == 2024
    assert series[1]["value"] == 3252347.0


def test_save_and_load_roundtrip(sample_dirs, tmp_path):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex().add_many([dir_2023, dir_2024])

    registry_path = tmp_path / "registry.json"
    reg.save(registry_path)

    loaded = ReportIndex.load(registry_path)
    assert loaded.companies() == ["CHINHIN"]
    assert loaded.years("CHINHIN") == [2023, 2024]

    result = loaded.query("revenue", company="CHINHIN", year=2024)
    assert result is not None
    assert result["group"] == 3252347.0


def test_load_nonexistent_returns_empty(tmp_path):
    reg = ReportIndex.load(tmp_path / "missing.json")
    assert reg.companies() == []


def test_add_many_chaining(sample_dirs):
    dir_2023, dir_2024 = sample_dirs
    reg = ReportIndex().add_many([dir_2023, dir_2024])
    assert len(reg.years("CHINHIN")) == 2
