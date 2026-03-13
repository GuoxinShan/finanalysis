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

def classify_page(page) -> str:
    """Classify page type: native_text / table / mixed / ocr_only"""

    text = page.extract_text()
    tables = page.find_tables()

    text_length = len(text) if text else 0
    has_tables = len(tables) > 0

    # Check if scanned image
    if text_length < 50 and not has_tables:
        return "ocr_only"

    # Calculate table coverage
    if has_tables:
        table_area = sum(t.bbox_area for t in tables)
        page_area = page.width * page.height
        table_ratio = table_area / page_area

        if table_ratio > 0.5:
            return "table"
        else:
            return "mixed"
    else:
        return "native_text"
