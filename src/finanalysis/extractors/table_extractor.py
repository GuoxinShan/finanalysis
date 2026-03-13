# src/finanalysis/extractors/table_extractor.py
import hashlib
import logging
from typing import List, Optional
from pdfplumber.pdf import Page

from ..models import TableRow

logger = logging.getLogger(__name__)


class TableExtractionError(Exception):
    """Raised when table extraction fails"""
    pass


def extract_tables(
    page: Page,
    page_number: int,
    table_index: int = 0,
    min_row_length: int = 2,
    extraction_method: str = "pdfplumber"
) -> List[TableRow]:
    """Extract tables from a PDF page

    Args:
        page: pdfplumber Page object
        page_number: Page number (1-indexed)
        table_index: Which table on the page to extract (0-indexed)
        min_row_length: Minimum number of cells to consider a valid row
        extraction_method: Method used for extraction ("pdfplumber", "camelot", "fallback")

    Returns:
        List of TableRow objects

    Raises:
        TableExtractionError: If extraction fails
    """
    try:
        tables = page.find_tables()

        if not tables:
            logger.debug(f"No tables found on page {page_number}")
            return []

        if table_index >= len(tables):
            logger.warning(
                f"Table index {table_index} out of range (page {page_number} has {len(tables)} tables)"
            )
            return []

        table = tables[table_index]
        return _extract_table_rows(
            table=table,
            page_number=page_number,
            table_index=table_index,
            min_row_length=min_row_length,
            extraction_method=extraction_method,
            page=page
        )

    except Exception as e:
        logger.error(f"Table extraction failed on page {page_number}: {e}")
        raise TableExtractionError(f"Failed to extract tables from page {page_number}: {e}") from e


def _extract_table_rows(
    table,
    page_number: int,
    table_index: int,
    min_row_length: int,
    extraction_method: str,
    page: Page
) -> List[TableRow]:
    """Extract rows from a single table"""
    rows = []

    # Extract table data
    try:
        table_data = table.extract()
    except Exception as e:
        logger.warning(f"Failed to extract table data: {e}")
        return []

    if not table_data:
        return []

    # Get table bbox for metadata
    bbox = table.bbox if hasattr(table, 'bbox') and table.bbox else (0, 0, page.width, page.height)

    # Process each row
    for row_idx, row_data in enumerate(table_data):
        if not row_data or len(row_data) < min_row_length:
            continue

        # Clean cells (convert None to empty string)
        cells = [str(cell) if cell is not None else "" for cell in row_data]

        # Skip empty rows
        if not any(cells):
            continue

        # Generate unique ID
        row_id = _generate_row_id(page_number, table_index, row_idx, cells)

        # Compute row bbox (approximate from table bbox and row index)
        x0, y0, x1, y1 = bbox
        row_height = (y1 - y0) / len(table_data) if len(table_data) > 0 else 20
        row_y0 = y0 + (row_idx * row_height)
        row_y1 = row_y0 + row_height
        row_bbox = (x0, row_y0, x1, row_y1)

        table_row = TableRow(
            id=row_id,
            page_number=page_number,
            table_index=table_index,
            row_index=row_idx,
            cells=cells,
            bbox=row_bbox,
            extraction_method=extraction_method,
            confidence=1.0 if extraction_method == "pdfplumber" else 0.8
        )
        rows.append(table_row)

    logger.info(f"Extracted {len(rows)} rows from table {table_index} on page {page_number}")
    return rows


def _generate_row_id(page_number: int, table_index: int, row_index: int, cells: List[str]) -> str:
    """Generate unique ID for a table row"""
    content = f"{page_number}-{table_index}-{row_index}-{'-'.join(cells[:3])}"  # Use first 3 cells
    hash_val = hashlib.md5(content.encode()).hexdigest()[:12]
    return f"row-{hash_val}"


def extract_tables_with_fallback(page: Page, page_number: int) -> List[TableRow]:
    """Extract tables with fallback to alternative methods if primary fails

    Args:
        page: pdfplumber Page object
        page_number: Page number (1-indexed)

    Returns:
        List of TableRow objects
    """
    all_rows = []

    # Find all tables
    try:
        tables = page.find_tables()
        if not tables:
            return all_rows

        # Extract from each table
        for table_idx in range(len(tables)):
            try:
                rows = extract_tables(
                    page=page,
                    page_number=page_number,
                    table_index=table_idx,
                    extraction_method="pdfplumber"
                )
                all_rows.extend(rows)
            except TableExtractionError:
                logger.warning(f"Failed to extract table {table_idx} from page {page_number}, skipping")
                continue

        return all_rows

    except Exception as e:
        logger.error(f"All table extraction methods failed for page {page_number}: {e}")
        return []
