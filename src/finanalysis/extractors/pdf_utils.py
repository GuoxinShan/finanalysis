# src/finanalysis/extractors/pdf_utils.py
import pdfplumber
from contextlib import contextmanager
from typing import Generator, Tuple, Optional
from pathlib import Path

@contextmanager
def open_pdf(pdf_path: str) -> Generator[pdfplumber.PDF, None, None]:
    """Context manager for opening PDF files"""
    pdf = pdfplumber.open(pdf_path)
    try:
        yield pdf
    finally:
        pdf.close()

def get_page_count(pdf_path: str) -> int:
    """Get total page count of PDF"""
    with open_pdf(pdf_path) as pdf:
        return len(pdf.pages)

def get_page_dimensions(page: pdfplumber.pdf.Page) -> Tuple[float, float]:
    """Get page dimensions (width, height)"""
    return (page.width, page.height)

def classify_page(page, text: Optional[str] = None) -> str:
    """Classify page type: native_text / table / mixed / ocr_only

    Args:
        page: pdfplumber page object
        text: Pre-extracted text (avoids redundant extraction)
    """
    if text is None:
        text = page.extract_text() or ""

    text_length = len(text)

    if text_length < 50:
        return "ocr_only"

    # Heuristic: pages with many aligned numbers are likely tables
    import re
    number_lines = len(re.findall(r'[\d,]{3,}.*[\d,]{3,}', text))
    total_lines = max(text.count('\n'), 1)
    number_ratio = number_lines / total_lines

    if number_ratio > 0.4:
        return "table"
    elif number_ratio > 0.15:
        return "mixed"
    return "native_text"
