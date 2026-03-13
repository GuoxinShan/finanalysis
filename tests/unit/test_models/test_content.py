# tests/unit/test_models/test_content.py
from src.finanalysis.models.content import TextBlock, TableRow

def test_text_block_creation():
    block = TextBlock(
        id="test-id-123",
        page_number=1,
        text="This is sample text",
        bbox=(100.0, 200.0, 300.0, 250.0)
    )

    assert block.id == "test-id-123"
    assert block.page_number == 1
    assert block.text == "This is sample text"
    assert block.bbox == (100.0, 200.0, 300.0, 250.0)
    assert block.embedding is None

def test_table_row_creation():
    row = TableRow(
        id="row-id-456",
        page_number=2,
        table_index=0,
        row_index=5,
        cells=["Revenue", "$1,234,567", "2023"],
        bbox=(50.0, 100.0, 550.0, 120.0),
        extraction_method="pdfplumber",
        confidence=0.95
    )

    assert row.id == "row-id-456"
    assert row.table_index == 0
    assert row.cells == ["Revenue", "$1,234,567", "2023"]
    assert row.extraction_method == "pdfplumber"
    assert row.confidence == 0.95
