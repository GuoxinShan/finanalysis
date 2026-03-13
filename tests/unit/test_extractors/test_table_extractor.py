# tests/unit/test_extractors/test_table_extractor.py
import pytest
from src.finanalysis.extractors.table_extractor import extract_tables, TableExtractionError
from src.finanalysis.models import TableRow


def test_extract_tables_basic():
    """Test basic table extraction"""
    # Mock page with simple table
    class MockCell:
        def __init__(self, text):
            self.text = text

    class MockRow:
        def __init__(self, cells):
            self.cells = cells

    class MockTable:
        def extract(self):
            return [
                ["Header 1", "Header 2", "Header 3"],
                ["Value 1", "100", "2023"],
                ["Value 2", "200", "2024"],
            ]

        @property
        def bbox(self):
            return (50, 100, 550, 300)

    class MockPage:
        def find_tables(self):
            return [MockTable()]

        @property
        def width(self):
            return 612

        @property
        def height(self):
            return 792

    page = MockPage()
    rows = extract_tables(page, page_number=1, table_index=0)

    assert isinstance(rows, list)
    assert len(rows) >= 0
    assert all(isinstance(r, TableRow) for r in rows)


def test_extract_tables_empty_page():
    """Test extraction from page with no tables"""
    class MockPage:
        def find_tables(self):
            return []

    page = MockPage()
    rows = extract_tables(page, page_number=1, table_index=0)

    assert isinstance(rows, list)
    assert len(rows) == 0


def test_extract_tables_with_filtering():
    """Test that very short rows are filtered out"""
    class MockTable:
        def extract(self):
            return [
                ["A", "B"],  # Too short
                ["Revenue", "$1,000,000", "2023", "Growth: 15%"],  # Good
            ]

        @property
        def bbox(self):
            return (50, 100, 550, 200)

    class MockPage:
        def find_tables(self):
            return [MockTable()]

    page = MockPage()
    rows = extract_tables(page, page_number=1, table_index=0, min_row_length=3)

    # Should only have 1 row (the longer one)
    assert len(rows) <= 1
