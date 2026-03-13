# tests/integration/test_stage2.py
from pathlib import Path
from src.finanalysis.stages.stage2_text import Stage2TextExtractor
from src.finanalysis.stages.stage1_preprocess import Stage1Preprocessor
from src.finanalysis.config import Settings
import tempfile


def test_stage2_process():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        settings = Settings(
            openai_api_key="test-key",
            cache_enabled=False
        )

        # Run Stage 1 first
        stage1 = Stage1Preprocessor(settings=settings)
        doc_manifest, page_manifests = stage1.process(
            pdf_path="testdata/CHINHIN-2023-12-31.pdf",
            output_dir=output_dir
        )

        # Run Stage 2
        stage2 = Stage2TextExtractor(settings=settings)
        text_blocks, updated_page_manifests = stage2.process(
            pdf_path="testdata/CHINHIN-2023-12-31.pdf",
            doc_manifest=doc_manifest,
            page_manifests=page_manifests,
            output_dir=output_dir
        )

        # Verify text blocks extracted
        assert isinstance(text_blocks, list)
        assert len(text_blocks) > 0
        assert all(hasattr(b, "text") for b in text_blocks)
        assert all(hasattr(b, "page_number") for b in text_blocks)

        # Verify page manifests updated
        assert len(updated_page_manifests) == len(page_manifests)

        # Verify output files exist
        assert (output_dir / "text_blocks.jsonl").exists()
        assert (output_dir / "page_manifests.jsonl").exists()
