# tests/integration/test_stage3.py
from pathlib import Path
from src.finanalysis.stages.stage3_tables import Stage3TableExtractor
from src.finanalysis.stages.stage1_preprocess import Stage1Preprocessor
from src.finanalysis.stages.stage2_text import Stage2TextExtractor
from src.finanalysis.config import Settings
import tempfile


def test_stage3_process():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        settings = Settings(
            openai_api_key="test-key",
            cache_enabled=False
        )

        # Run Stage 1
        stage1 = Stage1Preprocessor(settings=settings)
        doc_manifest, page_manifests = stage1.process(
            pdf_path="testdata/CHINHIN_Annual_Report_2024.pdf",
            output_dir=output_dir
        )

        # Run Stage 2
        stage2 = Stage2TextExtractor(settings=settings)
        text_blocks, updated_page_manifests = stage2.process(
            pdf_path="testdata/CHINHIN_Annual_Report_2024.pdf",
            doc_manifest=doc_manifest,
            page_manifests=page_manifests,
            output_dir=output_dir
        )

        # Run Stage 3
        stage3 = Stage3TableExtractor(settings=settings)
        table_rows, final_page_manifests = stage3.process(
            pdf_path="testdata/CHINHIN_Annual_Report_2024.pdf",
            doc_manifest=doc_manifest,
            page_manifests=updated_page_manifests,
            output_dir=output_dir
        )

        # Verify table rows extracted
        assert isinstance(table_rows, list)
        assert len(table_rows) > 0
        assert all(hasattr(r, "cells") for r in table_rows)
        assert all(hasattr(r, "page_number") for r in table_rows)

        # Verify page manifests updated
        assert len(final_page_manifests) == len(page_manifests)

        # Verify output files exist
        assert (output_dir / "table_rows.jsonl").exists()
