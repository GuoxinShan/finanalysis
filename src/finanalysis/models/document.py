# src/finanalysis/models/document.py
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, List

class DocumentManifest(BaseModel):
    """Document-level metadata"""
    pdf_path: str
    pdf_hash: str
    total_pages: int
    file_size_bytes: int
    processed_at: datetime

    # Statistics
    page_types: Dict[str, int]
    text_block_count: int
    table_row_count: int
    metric_candidate_count: int

    # Configuration snapshot
    config_snapshot: Dict[str, Any]

class PageManifest(BaseModel):
    """Page-level metadata"""
    page_number: int
    page_type: str  # native_text / table / mixed / ocr_only
    width: float
    height: float

    # Processing status
    text_extracted: bool = False
    table_extracted: bool = False
    ocr_applied: bool = False

    # References
    text_block_ids: List[str] = []
    table_row_ids: List[str] = []

    # Caching
    content_hash: str
