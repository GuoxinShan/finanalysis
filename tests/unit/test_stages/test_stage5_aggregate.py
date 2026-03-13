# tests/unit/test_stages/test_stage5_aggregate.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from src.finanalysis.stages.stage5_aggregate import Stage5Aggregator
from src.finanalysis.models import DocumentManifest, PageManifest, TextBlock, TableRow, MetricCandidate, MetricType
from src.finanalysis.config import Settings


@pytest.fixture
def settings():
    """Test settings"""
    return Settings(
        openai_api_key="test-key",
        llm_model="qwen3.5-flash",
        cache_enabled=False,
        output_dir="./test_output"
    )


@pytest.fixture
def doc_manifest():
    """Sample document manifest"""
    return DocumentManifest(
        pdf_path="test.pdf",
        pdf_hash="abc123",
        total_pages=2,
        file_size_bytes=1000,
        processed_at=datetime.now(),
        page_types={"table": 1, "mixed": 1},
        text_block_count=5,
        table_row_count=3,
        metric_candidate_count=2,
        config_snapshot={}
    )


@pytest.fixture
def page_manifests():
    """Sample page manifests"""
    return [
        PageManifest(
            page_number=1,
            page_type="table",
            width=612,
            height=792,
            text_extracted=False,
            table_extracted=True,
            ocr_applied=False,
            text_block_ids=[],
            table_row_ids=["row-1", "row-2"],
            content_hash="hash1"
        ),
        PageManifest(
            page_number=2,
            page_type="mixed",
            width=612,
            height=792,
            text_extracted=True,
            table_extracted=True,
            ocr_applied=False,
            text_block_ids=["text-1"],
            table_row_ids=["row-3"],
            content_hash="hash2"
        )
    ]


@pytest.fixture
def text_blocks():
    """Sample text blocks"""
    return [
        TextBlock(
            id="text-1",
            page_number=2,
            text="Sample text block",
            bbox=(50, 100, 550, 120)
        )
    ]


@pytest.fixture
def table_rows():
    """Sample table rows"""
    return [
        TableRow(
            id="row-1",
            page_number=1,
            table_index=0,
            row_index=0,
            cells=["Revenue", "$1,000,000", "2023"],
            bbox=(50, 100, 550, 120),
            extraction_method="pdfplumber",
            confidence=1.0
        ),
        TableRow(
            id="row-2",
            page_number=1,
            table_index=0,
            row_index=1,
            cells=["Net Income", "$500,000", "2023"],
            bbox=(50, 120, 550, 140),
            extraction_method="pdfplumber",
            confidence=1.0
        )
    ]


@pytest.fixture
def metrics():
    """Sample metrics"""
    return [
        MetricCandidate(
            id="metric-0",
            metric_type=MetricType.REVENUE,
            value=1000000.0,
            currency="USD",
            period="2023",
            source_table_row_id="row-1",
            source_text="Revenue, $1,000,000, 2023",
            confidence=0.95,
            reasoning="Revenue row clearly labeled"
        ),
        MetricCandidate(
            id="metric-1",
            metric_type=MetricType.NET_INCOME,
            value=500000.0,
            currency="USD",
            period="2023",
            source_table_row_id="row-2",
            source_text="Net Income, $500,000, 2023",
            confidence=0.92,
            reasoning="Net income row clearly labeled"
        )
    ]


def test_stage5_initialization(settings):
    """Test Stage5Aggregator initialization"""
    aggregator = Stage5Aggregator(settings=settings)
    assert aggregator.settings == settings


def test_stage5_process(settings, doc_manifest, page_manifests, text_blocks, table_rows, metrics, tmp_path):
    """Test Stage 5 processing"""
    aggregator = Stage5Aggregator(settings=settings)

    # Process
    summary = aggregator.process(
        pdf_path="test.pdf",
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        text_blocks=text_blocks,
        table_rows=table_rows,
        metrics=metrics,
        output_dir=tmp_path
    )

    # Verify summary generated
    assert summary is not None
    assert summary["status"] == "success"
    assert summary["pdf_path"] == "test.pdf"
    assert "statistics" in summary
    assert summary["statistics"]["total_pages"] == 2
    assert summary["statistics"]["text_blocks"] == 1  # Actual count from text_blocks list
    assert summary["statistics"]["table_rows"] == 2  # Actual count from table_rows list
    assert summary["statistics"]["metrics"] == 2

    # Verify output files created
    assert (tmp_path / "document_manifest.json").exists()
    assert (tmp_path / "page_manifests.jsonl").exists()
    assert (tmp_path / "text_blocks.jsonl").exists()
    assert (tmp_path / "table_rows.jsonl").exists()
    assert (tmp_path / "metric_candidates.jsonl").exists()
    assert (tmp_path / "summary.json").exists()

    # Verify manifest updated
    with open(tmp_path / "document_manifest.json", 'r') as f:
        manifest_data = json.load(f)
        assert manifest_data["pdf_path"] == "test.pdf"


def test_stage5_handles_empty_data(settings, doc_manifest, page_manifests, tmp_path):
    """Test Stage 5 handles empty data gracefully"""
    aggregator = Stage5Aggregator(settings=settings)

    # Process with empty data
    summary = aggregator.process(
        pdf_path="test.pdf",
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        text_blocks=[],
        table_rows=[],
        metrics=[],
        output_dir=tmp_path
    )

    # Should still succeed
    assert summary["status"] == "success"
    assert summary["statistics"]["text_blocks"] == 0
    assert summary["statistics"]["table_rows"] == 0
    assert summary["statistics"]["metrics"] == 0


def test_stage5_validates_outputs(settings, doc_manifest, page_manifests, text_blocks, table_rows, metrics, tmp_path):
    """Test Stage 5 validates all output files"""
    aggregator = Stage5Aggregator(settings=settings)

    # Process
    aggregator.process(
        pdf_path="test.pdf",
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        text_blocks=text_blocks,
        table_rows=table_rows,
        metrics=metrics,
        output_dir=tmp_path
    )

    # Validate all files have content
    assert (tmp_path / "document_manifest.json").stat().st_size > 0
    assert (tmp_path / "page_manifests.jsonl").stat().st_size > 0
    assert (tmp_path / "text_blocks.jsonl").stat().st_size > 0
    assert (tmp_path / "table_rows.jsonl").stat().st_size > 0
    assert (tmp_path / "metric_candidates.jsonl").stat().st_size > 0
    assert (tmp_path / "summary.json").stat().st_size > 0
