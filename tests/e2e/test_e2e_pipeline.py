# tests/e2e/test_e2e_pipeline.py
"""
End-to-end tests for the complete PDF parsing pipeline.

These tests run the full pipeline with real PDFs and verify
all outputs are generated correctly. No LLM mocking needed —
Stage 4 uses FSIndex (structured extraction, no LLM).
"""
import pytest
import json
from pathlib import Path

from src.finanalysis.pipeline import Pipeline
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
def test_pdf():
    """Path to test PDF"""
    return "testdata/CHINHIN_Annual_Report_2024.pdf"


def test_e2e_full_pipeline_with_real_pdf(settings, test_pdf, tmp_path):
    """
    E2E Test: Run complete pipeline on real PDF

    This test verifies:
    - All 5 stages complete without errors
    - All output files are created
    - Output files have valid structure
    - FSIndex metrics are extracted correctly
    - Summary is generated with correct statistics
    """
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

    # 2. Verify statistics
    stats = result["statistics"]
    assert stats["total_pages"] > 0
    assert stats["text_blocks"] > 0
    assert stats["table_rows"] >= 0
    assert stats["metrics"] > 0  # FSIndex should find metrics

    # 3. Verify all output files created
    assert (tmp_path / "document_manifest.json").exists()
    assert (tmp_path / "page_manifests.jsonl").exists()
    assert (tmp_path / "text_blocks.jsonl").exists()
    assert (tmp_path / "table_rows.jsonl").exists()
    assert (tmp_path / "metric_candidates.jsonl").exists()
    assert (tmp_path / "summary.json").exists()
    assert (tmp_path / "fs_index.json").exists()

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

    # 7. Verify metric candidates (JSONL) — all from FSIndex
    metrics = []
    with open(tmp_path / "metric_candidates.jsonl", 'r') as f:
        for line in f:
            if line.strip():
                metrics.append(json.loads(line))
    assert len(metrics) > 0
    assert all(m["id"].startswith("fs-") for m in metrics)
    assert all(m["confidence"] == 1.0 for m in metrics)

    # 8. Verify summary
    with open(tmp_path / "summary.json", 'r') as f:
        summary = json.load(f)
        assert summary["status"] == "success"
        assert "statistics" in summary

    print(f"\n✓ E2E Test Complete:")
    print(f"  PDF: {test_pdf}")
    print(f"  Pages: {stats['total_pages']}")
    print(f"  Text blocks: {stats['text_blocks']}")
    print(f"  Table rows: {stats['table_rows']}")
    print(f"  FSIndex metrics: {stats['metrics']}")
    print(f"  Output dir: {tmp_path}")


def test_e2e_pipeline_with_force_flag(settings, test_pdf, tmp_path):
    """E2E Test: Verify force flag works (bypasses cache)"""
    settings.cache_enabled = True
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


def test_e2e_pipeline_handles_empty_results(settings, tmp_path):
    """E2E Test: Verify pipeline handles PDF gracefully (uses stop_at_stage to avoid full re-run)"""
    test_pdf = "testdata/CHINHIN_Annual_Report_2024.pdf"

    if not Path(test_pdf).exists():
        pytest.skip("Test PDF not available")

    pipeline = Pipeline(settings=settings)
    result = pipeline.run(
        pdf_path=test_pdf,
        output_dir=str(tmp_path),
        stop_at_stage=1
    )

    assert result["status"] == "stopped"
    assert result["stage"] == 1
