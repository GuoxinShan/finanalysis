# tests/unit/test_compare.py
import pytest
import json
from pathlib import Path

from src.finanalysis.compare import MetricComparer


@pytest.fixture
def output_dirs(tmp_path):
    """Create sample output dirs for 3 years"""
    years = {
        "2023": [
            {"id": "m0", "metric_type": "revenue", "value": 2057202.0, "currency": "MYR", "period": "2023", "source_table_row_id": "r1", "source_text": "Revenue", "confidence": 0.98},
            {"id": "m1", "metric_type": "net_income", "value": 150107.0, "currency": "MYR", "period": "2023", "source_table_row_id": "r2", "source_text": "Net Income", "confidence": 0.96},
            {"id": "m2", "metric_type": "gross_profit", "value": 188200.0, "currency": "MYR", "period": "2023", "source_table_row_id": "r3", "source_text": "Gross Profit", "confidence": 0.97},
        ],
        "2024": [
            {"id": "m0", "metric_type": "revenue", "value": 3252347.0, "currency": "MYR", "period": "2024", "source_table_row_id": "r1", "source_text": "Revenue", "confidence": 0.95},
            {"id": "m1", "metric_type": "net_income", "value": 208041.0, "currency": "MYR", "period": "2024", "source_table_row_id": "r2", "source_text": "Net Income", "confidence": 0.85},
        ],
        "2025": [
            {"id": "m0", "metric_type": "revenue", "value": 4072171.0, "currency": "MYR", "period": "2025", "source_table_row_id": "r1", "source_text": "Revenue", "confidence": 0.98},
            {"id": "m1", "metric_type": "net_income", "value": 103625.0, "currency": "MYR", "period": "2025", "source_table_row_id": "r2", "source_text": "Net Income", "confidence": 0.97},
            {"id": "m2", "metric_type": "gross_profit", "value": 773401.0, "currency": "MYR", "period": "2025", "source_table_row_id": "r3", "source_text": "Gross Profit", "confidence": 0.98},
        ],
    }

    dirs = {}
    for year, metrics in years.items():
        d = tmp_path / year
        d.mkdir()
        with open(d / "metric_candidates.jsonl", "w") as f:
            for m in metrics:
                f.write(json.dumps(m) + "\n")
        dirs[year] = d

    return dirs


def test_comparer_loads_metrics(output_dirs):
    """Test MetricComparer loads metrics from multiple dirs"""
    comparer = MetricComparer(output_dirs=output_dirs)
    assert "2023" in comparer.metrics
    assert "2024" in comparer.metrics
    assert "2025" in comparer.metrics
    assert len(comparer.metrics["2023"]) == 3


def test_comparer_compare_returns_table(output_dirs):
    """Test compare returns structured table"""
    comparer = MetricComparer(output_dirs=output_dirs)
    table = comparer.compare(metric_type="revenue")

    assert isinstance(table, list)
    assert len(table) > 0
    for row in table:
        assert "label" in row
        assert "value" in row
        assert "currency" in row
        assert "confidence" in row


def test_comparer_compare_all_returns_dict(output_dirs):
    """Test compare_all returns dict keyed by metric type"""
    comparer = MetricComparer(output_dirs=output_dirs)
    result = comparer.compare_all()

    assert isinstance(result, dict)
    assert "revenue" in result
    assert "net_income" in result


def test_comparer_yoy_growth(output_dirs):
    """Test year-over-year growth calculation"""
    comparer = MetricComparer(output_dirs=output_dirs)
    table = comparer.compare(metric_type="revenue")

    # Should have growth % for years after first
    rows_with_growth = [r for r in table if r.get("yoy_growth") is not None]
    assert len(rows_with_growth) > 0


def test_comparer_missing_metric(output_dirs):
    """Test compare handles missing metric gracefully"""
    comparer = MetricComparer(output_dirs=output_dirs)
    table = comparer.compare(metric_type="eps")

    # eps not in any year - should return empty or partial
    assert isinstance(table, list)
