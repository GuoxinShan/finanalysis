# tests/unit/test_models/test_document.py
from datetime import datetime
from src.finanalysis.models.document import DocumentManifest, PageManifest

def test_document_manifest_creation():
    manifest = DocumentManifest(
        pdf_path="/path/to/test.pdf",
        pdf_hash="abc123",
        total_pages=10,
        file_size_bytes=1024,
        processed_at=datetime(2023, 1, 1, 12, 0),
        page_types={"native_text": 5, "table": 5},
        text_block_count=20,
        table_row_count=50,
        metric_candidate_count=6,
        config_snapshot={"model": "qwen3.5-flash"}
    )

    assert manifest.pdf_path == "/path/to/test.pdf"
    assert manifest.total_pages == 10
    assert manifest.page_types["native_text"] == 5

def test_page_manifest_creation():
    manifest = PageManifest(
        page_number=1,
        page_type="native_text",
        width=612.0,
        height=792.0,
        content_hash="def456"
    )

    assert manifest.page_number == 1
    assert manifest.page_type == "native_text"
    assert manifest.text_extracted == False
    assert manifest.table_extracted == False
    assert manifest.ocr_applied == False
    assert manifest.text_block_ids == []
    assert manifest.table_row_ids == []
