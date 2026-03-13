# src/finanalysis/models/content.py
from pydantic import BaseModel
from typing import List, Tuple, Optional

class TextBlock(BaseModel):
    """Text block extracted from PDF"""
    id: str
    page_number: int
    text: str
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)

    # Extension point for vector embeddings
    embedding: Optional[List[float]] = None

class TableRow(BaseModel):
    """Table row extracted from PDF"""
    id: str
    page_number: int
    table_index: int  # Which table on the page
    row_index: int    # Which row in the table
    cells: List[str]

    # Metadata
    bbox: Tuple[float, float, float, float]
    extraction_method: str  # "pdfplumber" / "camelot" / "fallback"
    confidence: Optional[float] = None
