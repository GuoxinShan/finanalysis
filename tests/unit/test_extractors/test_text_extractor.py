# tests/unit/test_extractors/test_text_extractor.py
from src.finanalysis.extractors.text_extractor import extract_text_blocks
from src.finanalysis.models import TextBlock

def test_extract_text_blocks_basic():
    # Create a mock page with text
    class MockChar:
        def __init__(self, text, x0, y0, x1, y1):
            self.text = text
            self.x0 = x0
            self.y0 = y0
            self.x1 = x1
            self.y1 = y1
            self.top = y0
            self.bottom = y1
            self.left = x0
            self.right = x1

    class MockWord:
        def __init__(self, chars):
            self.chars = chars
            self.text = "".join(c.text for c in chars)
            self.x0 = min(c.x0 for c in chars)
            self.y0 = min(c.y0 for c in chars)
            self.x1 = max(c.x1 for c in chars)
            self.y1 = max(c.y1 for c in chars)
            self.top = self.y0
            self.bottom = self.y1
            self.left = self.x0
            self.right = self.x1

    class MockPage:
        def extract_words(self, **kwargs):
            return []

        @property
        def width(self):
            return 612

        @property
        def height(self):
            return 792

    page = MockPage()
    blocks = extract_text_blocks(page, page_number=1)

    assert isinstance(blocks, list)
    assert all(isinstance(b, TextBlock) for b in blocks)
