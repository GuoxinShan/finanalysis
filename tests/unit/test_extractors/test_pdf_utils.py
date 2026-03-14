# tests/unit/test_extractors/test_pdf_utils.py
from src.finanalysis.extractors.pdf_utils import open_pdf, get_page_count, get_page_dimensions, classify_page

def test_open_pdf():
    # Use one of the real PDFs
    with open_pdf("testdata/CHINHIN_Annual_Report_2024.pdf") as pdf:
        assert pdf is not None
        assert len(pdf.pages) > 0

def test_get_page_count():
    count = get_page_count("testdata/CHINHIN_Annual_Report_2024.pdf")
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
    # Create a mock page with tabular text (many lines with aligned numbers)
    table_text = "\n".join([
        "Revenue                    3,252,347    2,057,210",
        "Cost of sales             (2,727,214)  (1,868,788)",
        "Gross profit                 525,133      188,422",
        "Other income                  45,678       32,100",
        "Admin expenses              (120,456)     (98,765)",
        "Finance costs                (85,432)     (65,321)",
        "Profit before tax            275,845      189,318",
        "Tax expense                  (68,961)     (47,329)",
        "Profit for the year          206,884      141,989",
        "Some text line without numbers here",
    ])

    class MockPage:
        def extract_text(self):
            return table_text

    page = MockPage()
    page_type = classify_page(page)
    assert page_type == "table"
