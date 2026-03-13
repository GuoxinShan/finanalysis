# tests/unit/test_extractors/test_pdf_utils.py
from src.finanalysis.extractors.pdf_utils import open_pdf, get_page_count, get_page_dimensions, classify_page

def test_open_pdf():
    # Use one of the real PDFs
    with open_pdf("testdata/CHINHIN-2023-12-31.pdf") as pdf:
        assert pdf is not None
        assert len(pdf.pages) > 0

def test_get_page_count():
    count = get_page_count("testdata/CHINHIN-2023-12-31.pdf")
    assert count > 0

def test_classify_page_native_text():
    # Create a mock page with text
    class MockPage:
        def extract_text(self):
            return "This is a paragraph of text. " * 10

        def find_tables(self):
            return []

    page = MockPage()
    page_type = classify_page(page)
    assert page_type == "native_text"

def test_classify_page_table():
    # Create a mock page with table
    class MockTable:
        @property
        def bbox_area(self):
            return 400000  # Large area

    class MockPage:
        def extract_text(self):
            return ""

        def find_tables(self):
            return [MockTable()]

        @property
        def width(self):
            return 612

        @property
        def height(self):
            return 792

    page = MockPage()
    page_type = classify_page(page)
    assert page_type == "table"
