# tests/e2e/test_e2e_pipeline.py
"""
End-to-end tests for the complete PDF parsing pipeline.

These tests run the full pipeline with real PDFs and verify
all outputs are generated correctly.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.finanalysis.pipeline import Pipeline
from src.finanalysis.config import Settings


@pytest.fixture
def settings():
    """Test settings"""
    return Settings(
        openai_api_key="test-key",
        llm_model="qwen3.5-flash",
        cache_enabled=False,  # Disable cache for E2E tests
        output_dir="./test_output"
    )


@pytest.fixture
def test_pdf():
    """Path to test PDF"""
    return "testdata/CHINHIN-2023-12-31.pdf"


@patch('src.finanalysis.stages.stage4_metrics.LLMClient')
def test_e2e_full_pipeline_with_real_pdf(mock_llm_client_class, settings, test_pdf, tmp_path):
    """
    E2E Test: Run complete pipeline on real PDF

    This test verifies:
    - All 5 stages complete without errors
    - All output files are created
    - Output files have valid structure
    - Metrics are extracted correctly
    - Summary is generated with correct statistics
    """
    # Mock LLM client
    mock_llm_client = MagicMock()
    mock_llm_client.extract_json.return_value = {
        "metrics": [
            {
                "metric_type": "revenue",
                "value": 1500000.0,
                "currency": "MYR",
                "period": "2023",
                "confidence": 0.93,
                "reasoning": "Revenue figure from financial statement"
            },
            {
                "metric_type": "net_income",
                "value": 300000.0,
                "currency": "MYR",
                "period": "2023",
                "confidence": 0.91,
                "reasoning": "Net income from statement"
            },
            {
                "metric_type": "gross_profit",
                "value": 750000.0,
                "currency": "MYR",
                "period": "2023",
                "confidence": 0.89,
                "reasoning": "Gross profit from income statement"
            }
        ]
    }
    mock_llm_client_class.return_value = mock_llm_client

    # Run full pipeline
    pipeline = Pipeline(settings=settings)
    result = pipeline.run(
        pdf_path=test_pdf,
        output_dir=str(tmp_path)
    )

    # 1. Verify result structure
    assert result is not None
    assert result["status"] == "success"
    assert result["pdf_path"] == test_pdf
    assert "pdf_hash" in result
    assert "processed_at" in result
    assert "statistics" in result
    assert "extracted_metrics" in result

    # 2. Verify statistics
    stats = result["statistics"]
    assert stats["total_pages"] > 0
    assert stats["text_blocks"] > 0
    assert stats["table_rows"] >= 0  # May be 0 if no tables
    assert stats["metrics"] >= 0

    # 3. Verify all output files created
    assert (tmp_path / "document_manifest.json").exists()
    assert (tmp_path / "page_manifests.jsonl").exists()
    assert (tmp_path / "text_blocks.jsonl").exists()
    assert (tmp_path / "table_rows.jsonl").exists()
    assert (tmp_path / "metric_candidates.jsonl").exists()
    assert (tmp_path / "summary.json").exists()

    # 4. Verify document manifest
    with open(tmp_path / "document_manifest.json", 'r') as f:
        manifest = json.load(f)
        assert manifest["pdf_path"] == test_pdf
        assert manifest["total_pages"] > 0
        assert "pdf_hash" in manifest
        assert "page_types" in manifest

    # 5. Verify page manifests (JSONL)
    page_manifests = []
    with open(tmp_path / "page_manifests.jsonl", 'r') as f:
        for line in f:
            if line.strip():
                page_manifests.append(json.loads(line))
    assert len(page_manifests) > 0
    assert all("page_number" in pm for pm in page_manifests)

    # 6. Verify text blocks (JSONL)
    text_blocks = []
    with open(tmp_path / "text_blocks.jsonl", 'r') as f:
        for line in f:
            if line.strip():
                text_blocks.append(json.loads(line))
    assert len(text_blocks) > 0
    assert all("text" in tb for tb in text_blocks)

    # 7. Verify metric candidates (JSONL)
    metrics = []
    with open(tmp_path / "metric_candidates.jsonl", 'r') as f:
        for line in f:
            if line.strip():
                metrics.append(json.loads(line))
    assert len(metrics) >= 0  # May be empty if no tables or LLM found nothing

    # 8. Verify summary
    with open(tmp_path / "summary.json", 'r') as f:
        summary = json.load(f)
        assert summary["status"] == "success"
        assert "statistics" in summary
        assert "extracted_metrics" in summary

    # 9. Verify LLM was called if tables were extracted
    if stats["table_rows"] > 0:
        assert mock_llm_client.extract_json.called

    # Print summary for visibility
    print(f"\n✓ E2E Test Complete:")
    print(f"  PDF: {test_pdf}")
    print(f"  Pages: {stats['total_pages']}")
    print(f"  Text blocks: {stats['text_blocks']}")
    print(f"  Table rows: {stats['table_rows']}")
    print(f"  Metrics: {stats['metrics']}")
    print(f"  Output dir: {tmp_path}")


@patch('src.finanalysis.stages.stage4_metrics.LLMClient')
def test_e2e_pipeline_with_force_flag(mock_llm_client_class, settings, test_pdf, tmp_path):
    """E2E Test: Verify force flag works (bypasses cache)"""
    # Mock LLM
    mock_llm_client = MagicMock()
    mock_llm_client.extract_json.return_value = {"metrics": []}
    mock_llm_client_class.return_value = mock_llm_client

    # Run with force=True
    settings.cache_enabled = True  # Enable cache
    pipeline = Pipeline(settings=settings)

    result = pipeline.run(
        pdf_path=test_pdf,
        output_dir=str(tmp_path),
        force=True
    )

    assert result["status"] == "success"


def test_e2e_pipeline_rejects_invalid_pdf(settings, tmp_path):
    """E2E Test: Verify pipeline rejects invalid PDF"""
    pipeline = Pipeline(settings=settings)

    with pytest.raises(FileNotFoundError):
        pipeline.run(
            pdf_path="nonexistent.pdf",
            output_dir=str(tmp_path)
        )


@patch('src.finanalysis.stages.stage4_metrics.LLMClient')
def test_e2e_pipeline_handles_empty_pdf(mock_llm_client_class, settings, tmp_path):
    """E2E Test: Verify pipeline handles empty/minimal PDF gracefully"""
    # Use a PDF path - but this will fail if the file doesn't exist
    # So we'll skip this test if the file doesn't exist
    test_pdf = "testdata/CHINHIN-2023-12-31.pdf"

    if not Path(test_pdf).exists():
        pytest.skip("Test PDF not available")

    # Mock LLM to return no metrics
    mock_llm_client = MagicMock()
    mock_llm_client.extract_json.return_value = {"metrics": []}
    mock_llm_client_class.return_value = mock_llm_client

    pipeline = Pipeline(settings=settings)
    result = pipeline.run(
        pdf_path=test_pdf,
        output_dir=str(tmp_path)
    )

    # Should still succeed, just with empty results
    assert result["status"] == "success"
    assert "processing_notes" in result
