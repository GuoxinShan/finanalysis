# tests/integration/test_pipeline_stage5.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.finanalysis.stages.stage1_preprocess import Stage1Preprocessor
from src.finanalysis.stages.stage2_text import Stage2TextExtractor
from src.finanalysis.stages.stage3_tables import Stage3TableExtractor
from src.finanalysis.stages.stage4_metrics import Stage4MetricExtractor
from src.finanalysis.stages.stage5_aggregate import Stage5Aggregator
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


@patch('src.finanalysis.stages.stage4_metrics.LLMClient')
def test_full_pipeline_through_stage5(mock_llm_client_class, settings, test_pdf_path, tmp_path):
    """Test full pipeline through Stage 5 with mocked LLM"""
    # Mock LLM client
    mock_llm_client = MagicMock()
    mock_llm_client.extract_json.return_value = {
        "metrics": [
            {
                "metric_type": "revenue",
                "value": 1500000.0,
                "currency": "CNY",
                "period": "2023",
                "confidence": 0.93,
                "reasoning": "Revenue figure from financial statement"
            },
            {
                "metric_type": "net_income",
                "value": 300000.0,
                "currency": "CNY",
                "period": "2023",
                "confidence": 0.91,
                "reasoning": "Net income from statement"
            }
        ]
    }
    mock_llm_client_class.return_value = mock_llm_client

    # Stage 1: Preprocess
    stage1 = Stage1Preprocessor(settings=settings)
    doc_manifest, page_manifests = stage1.process(
        pdf_path=test_pdf_path,
        output_dir=tmp_path
    )

    assert doc_manifest is not None
    assert len(page_manifests) > 0

    # Stage 2: Text extraction
    stage2 = Stage2TextExtractor(settings=settings)
    text_blocks, page_manifests = stage2.process(
        pdf_path=test_pdf_path,
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        output_dir=tmp_path
    )

    assert isinstance(text_blocks, list)

    # Stage 3: Table extraction
    stage3 = Stage3TableExtractor(settings=settings)
    table_rows, page_manifests = stage3.process(
        pdf_path=test_pdf_path,
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        output_dir=tmp_path
    )

    assert isinstance(table_rows, list)

    # Stage 4: Metric extraction
    stage4 = Stage4MetricExtractor(settings=settings)
    metrics = stage4.process(
        pdf_path=test_pdf_path,
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        table_rows=table_rows,
        output_dir=tmp_path
    )

    assert isinstance(metrics, list)

    # Stage 5: Aggregation
    stage5 = Stage5Aggregator(settings=settings)
    summary = stage5.process(
        pdf_path=test_pdf_path,
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        text_blocks=text_blocks,
        table_rows=table_rows,
        metrics=metrics,
        output_dir=tmp_path
    )

    # Verify summary
    assert summary is not None
    assert summary["status"] == "success"
    assert summary["pdf_path"] == test_pdf_path
    assert "statistics" in summary
    assert summary["statistics"]["total_pages"] > 0

    # Verify all final output files created
    assert (tmp_path / "document_manifest.json").exists()
    assert (tmp_path / "page_manifests.jsonl").exists()
    assert (tmp_path / "text_blocks.jsonl").exists()
    assert (tmp_path / "table_rows.jsonl").exists()
    assert (tmp_path / "metric_candidates.jsonl").exists()
    assert (tmp_path / "summary.json").exists()

    # Verify LLM was called
    assert mock_llm_client.extract_json.called

    print(f"\n✓ Full pipeline test complete:")
    print(f"  - Pages: {summary['statistics']['total_pages']}")
    print(f"  - Text blocks: {summary['statistics']['text_blocks']}")
    print(f"  - Table rows: {summary['statistics']['table_rows']}")
    print(f"  - Metrics: {summary['statistics']['metrics']}")


def test_stage5_aggregation_with_empty_data(settings, tmp_path):
    """Test Stage 5 aggregation with empty data from all stages"""
    from src.finanalysis.models import DocumentManifest, PageManifest

    doc_manifest = DocumentManifest(
        pdf_path="test.pdf",
        pdf_hash="abc123",
        total_pages=1,
        file_size_bytes=1000,
        processed_at=datetime.now(),
        page_types={"native_text": 1},
        text_block_count=0,
        table_row_count=0,
        metric_candidate_count=0,
        config_snapshot={}
    )

    page_manifests = [
        PageManifest(
            page_number=1,
            page_type="native_text",
            width=612,
            height=792,
            text_extracted=True,
            table_extracted=False,
            ocr_applied=False,
            text_block_ids=[],
            table_row_ids=[],
            content_hash="hash1"
        )
    ]

    stage5 = Stage5Aggregator(settings=settings)
    summary = stage5.process(
        pdf_path="test.pdf",
        doc_manifest=doc_manifest,
        page_manifests=page_manifests,
        text_blocks=[],
        table_rows=[],
        metrics=[],
        output_dir=tmp_path
    )

    assert summary["status"] == "success"
    assert summary["statistics"]["text_blocks"] == 0
    assert summary["statistics"]["table_rows"] == 0
    assert summary["statistics"]["metrics"] == 0
    assert len(summary["processing_notes"]) > 0  # Should have notes about empty data
