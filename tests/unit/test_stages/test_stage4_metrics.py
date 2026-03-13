# tests/unit/test_stages/test_stage4_metrics.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.finanalysis.stages.stage4_metrics import Stage4MetricExtractor
from src.finanalysis.models import DocumentManifest, PageManifest, TableRow, MetricCandidate, MetricType
from src.finanalysis.config import Settings


@pytest.fixture
def settings():
    """Test settings"""
    return Settings(
        openai_api_key="test-key",
        llm_model="qwen3.5-flash",
        cache_enabled=False
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
        text_block_count=0,
        table_row_count=3,
        metric_candidate_count=0,
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
        ),
        TableRow(
            id="row-3",
            page_number=2,
            table_index=0,
            row_index=0,
            cells=["Gross Profit", "$750,000", "2023"],
            bbox=(50, 100, 550, 120),
            extraction_method="pdfplumber",
            confidence=1.0
        )
    ]


def test_stage4_initialization(settings):
    """Test Stage4MetricExtractor initialization"""
    extractor = Stage4MetricExtractor(settings=settings)
    assert extractor.settings == settings
    assert extractor.llm_client is not None


@patch('src.finanalysis.stages.stage4_metrics.LLMClient')
def test_stage4_process(mock_llm_client_class, settings, doc_manifest, page_manifests, table_rows, tmp_path):
    """Test Stage 4 processing with mocked LLM"""
    # Mock LLM client
    mock_llm_client = MagicMock()
    mock_llm_client.extract_json.return_value = {
        "metrics": [
            {
                "metric_type": "revenue",
                "value": 1000000.0,
                "currency": "USD",
                "period": "2023",
                "confidence": 0.95,
                "reasoning": "Revenue row clearly labeled"
            },
            {
                "metric_type": "net_income",
                "value": 500000.0,
                "currency": "USD",
                "period": "2023",
                "confidence": 0.92,
                "reasoning": "Net Income row clearly labeled"
            }
        ]
    }
    mock_llm_client_class.return_value = mock_llm_client

    # Create extractor
    extractor = Stage4MetricExtractor(settings=settings)

    # Save table rows to input file
    import json
    stage3_output = tmp_path / "stage3_tables.json"
    with open(stage3_output, 'w') as f:
        json.dump([row.model_dump() for row in table_rows], f)

    # Process
    metrics = extractor.process(
        pdf_path="test.pdf",
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        table_rows=table_rows,
        output_dir=tmp_path
    )

    # Verify metrics extracted
    assert len(metrics) == 2
    assert all(isinstance(m, MetricCandidate) for m in metrics)

    # Check first metric
    metric1 = metrics[0]
    assert metric1.metric_type == MetricType.REVENUE
    assert metric1.value == 1000000.0
    assert metric1.currency == "USD"
    assert metric1.confidence == 0.95

    # Check second metric
    metric2 = metrics[1]
    assert metric2.metric_type == MetricType.NET_INCOME
    assert metric2.value == 500000.0
    assert metric2.confidence == 0.92

    # Verify manifest updated
    assert doc_manifest.metric_candidate_count == 2

    # Verify output files created
    assert (tmp_path / "stage4_metrics.json").exists()
    assert (tmp_path / "stage4_metrics.jsonl").exists()


@patch('src.finanalysis.stages.stage4_metrics.LLMClient')
def test_stage4_handles_empty_tables(mock_llm_client_class, settings, doc_manifest, page_manifests, tmp_path):
    """Test Stage 4 handles empty table rows"""
    extractor = Stage4MetricExtractor(settings=settings)

    # Process with empty table rows
    metrics = extractor.process(
        pdf_path="test.pdf",
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        table_rows=[],
        output_dir=tmp_path
    )

    # Should return empty list
    assert metrics == []
    assert doc_manifest.metric_candidate_count == 0


@patch('src.finanalysis.stages.stage4_metrics.LLMClient')
def test_stage4_handles_llm_error(mock_llm_client_class, settings, doc_manifest, page_manifests, table_rows, tmp_path):
    """Test Stage 4 handles LLM errors gracefully"""
    # Mock LLM client to raise error
    mock_llm_client = MagicMock()
    mock_llm_client.extract_json.side_effect = Exception("LLM API error")
    mock_llm_client_class.return_value = mock_llm_client

    extractor = Stage4MetricExtractor(settings=settings)

    # Should handle error and return empty list
    metrics = extractor.process(
        pdf_path="test.pdf",
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        table_rows=table_rows,
        output_dir=tmp_path
    )

    assert metrics == []
