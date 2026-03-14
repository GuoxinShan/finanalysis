# tests/integration/test_pipeline_stage4.py
"""Integration test for Stage 4 (FSIndex structured extraction, no LLM)."""
import pytest
from pathlib import Path

from src.finanalysis.fs_index import FSIndex
from src.finanalysis.config import Settings


@pytest.fixture
def settings():
    """Test settings with cache disabled"""
    return Settings(
        openai_api_key="test-key",
        llm_model="qwen3.5-flash",
        cache_enabled=False,
        output_dir="./test_output"
    )


@pytest.fixture
def test_pdf_path():
    """Path to test PDF"""
    return "testdata/CHINHIN_Annual_Report_2024.pdf"


def test_fsindex_extracts_line_items(test_pdf_path):
    """Test FSIndex extracts line items from real PDF"""
    pdf_path = Path(test_pdf_path)
    if not pdf_path.exists():
        pytest.skip("Test PDF not available")

    idx = FSIndex.from_pdf(pdf_path)

    assert len(idx.line_items) > 50
    assert idx.currency == "MYR"

    # Verify key metrics are present
    assert "revenue" in idx.line_items
    assert "gross profit" in idx.line_items
    assert "profit before tax" in idx.line_items

    # Verify values are populated
    revenue = idx.line_items["revenue"]
    assert revenue["group_current"] is not None
    assert revenue["group_prior"] is not None


def test_fsindex_save_load_roundtrip(test_pdf_path, tmp_path):
    """Test FSIndex save/load preserves data"""
    pdf_path = Path(test_pdf_path)
    if not pdf_path.exists():
        pytest.skip("Test PDF not available")

    idx = FSIndex.from_pdf(pdf_path)
    save_path = tmp_path / "fs_index.json"
    idx.save(save_path)

    loaded = FSIndex.load(save_path)
    assert loaded.currency == idx.currency
    assert len(loaded.line_items) == len(idx.line_items)
    assert loaded.line_items["revenue"]["group_current"] == idx.line_items["revenue"]["group_current"]


def test_fsindex_lookup(test_pdf_path):
    """Test FSIndex lookup returns correct values"""
    pdf_path = Path(test_pdf_path)
    if not pdf_path.exists():
        pytest.skip("Test PDF not available")

    idx = FSIndex.from_pdf(pdf_path)

    revenue = idx.lookup("revenue", "group", "current")
    assert revenue is not None
    assert revenue > 0

    # Lookup with fuzzy match
    ppe = idx.lookup("property, plant and equipment", "group", "current")
    assert ppe is not None
