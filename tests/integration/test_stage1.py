# tests/integration/test_stage1.py
from pathlib import Path
from src.finanalysis.stages.stage1_preprocess import Stage1Preprocessor
from src.finanalysis.config import Settings
import tempfile

def test_stage1_process():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        settings = Settings(
            openai_api_key="test-key",
            cache_enabled=False
        )

        stage1 = Stage1Preprocessor(settings=settings)

        # Use real test PDF
        doc_manifest, page_manifests = stage1.process(
            pdf_path="testdata/CHINHIN_Annual_Report_2024.pdf",
            output_dir=output_dir
        )

        # Verify document manifest
        assert doc_manifest.pdf_path == "testdata/CHINHIN_Annual_Report_2024.pdf"
        assert doc_manifest.total_pages > 0
        assert len(doc_manifest.pdf_hash) == 64  # SHA256 hex length

        # Verify page manifests
        assert len(page_manifests) == doc_manifest.total_pages
        assert all(p.page_number > 0 for p in page_manifests)
        assert all(p.page_type in ["native_text", "table", "mixed", "ocr_only"] for p in page_manifests)

        # Verify output files exist
        assert (output_dir / "document_manifest.json").exists()
        assert (output_dir / "page_manifests.jsonl").exists()
