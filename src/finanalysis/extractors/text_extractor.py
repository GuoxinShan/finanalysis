# src/finanalysis/extractors/text_extractor.py
import hashlib
from typing import List
from pdfplumber.pdf import Page

from ..models import TextBlock


def extract_text_blocks(page: Page, page_number: int) -> List[TextBlock]:
    """Extract text blocks from a PDF page

    Args:
        page: pdfplumber Page object
        page_number: Page number (1-indexed)

    Returns:
        List of TextBlock objects
    """
    text_blocks = []

    # Extract words with metadata
    words = page.extract_words(
        keep_blank_chars=True,
        x_tolerance=3,
        y_tolerance=3,
    )

    if not words:
        return text_blocks

    # Group words into lines based on vertical position
    lines = _group_words_into_lines(words)

    # Group lines into blocks based on vertical spacing
    blocks = _group_lines_into_blocks(lines, page.height)

    # Create TextBlock objects
    for block_idx, block_lines in enumerate(blocks):
        if not block_lines:
            continue

        # Combine all text in block - extract 'text' field from each word dict
        text = " ".join(" ".join(word["text"] for word in line) for line in block_lines)

        # Skip very short blocks
        if len(text) < 20:
            continue

        # Compute bounding box
        block_words = [w for line in block_lines for w in line]
        x0 = min(w["x0"] for w in block_words)
        y0 = min(w["top"] for w in block_words)
        x1 = max(w["x1"] for w in block_words)
        y1 = max(w["bottom"] for w in block_words)

        # Generate unique ID
        block_id = hashlib.md5(
            f"{page_number}-{block_idx}-{text}".encode()
        ).hexdigest()[:12]

        text_block = TextBlock(
            id=f"text-{block_id}",
            page_number=page_number,
            text=text,
            bbox=(x0, y0, x1, y1),
        )
        text_blocks.append(text_block)

    return text_blocks


def _group_words_into_lines(words: List[dict]) -> List[List[dict]]:
    """Group words into lines based on vertical position"""
    if not words:
        return []

    # Sort by vertical position (top), then horizontal (x0)
    sorted_words = sorted(words, key=lambda w: (w["top"], w["x0"]))

    lines = []
    current_line = [sorted_words[0]]
    current_top = sorted_words[0]["top"]

    for word in sorted_words[1:]:
        # Check if word is on same line (within tolerance)
        if abs(word["top"] - current_top) < 5:
            current_line.append(word)
        else:
            # Start new line
            lines.append(current_line)
            current_line = [word]
            current_top = word["top"]

    # Don't forget last line
    if current_line:
        lines.append(current_line)

    return lines


def _group_lines_into_blocks(lines: List[List[dict]], page_height: float) -> List[List[List[dict]]]:
    """Group lines into blocks based on vertical spacing"""
    if not lines:
        return []

    # Calculate typical line height
    if len(lines) < 2:
        return [lines]

    line_heights = []
    for i in range(len(lines) - 1):
        current_bottom = max(w["bottom"] for w in lines[i])
        next_top = min(w["top"] for w in lines[i + 1])
        line_heights.append(next_top - current_bottom)

    # Use median spacing as threshold
    import statistics

    median_spacing = statistics.median(line_heights) if line_heights else 10
    block_threshold = median_spacing * 2.0  # 2x median spacing indicates new block

    blocks = []
    current_block = [lines[0]]

    for i in range(1, len(lines)):
        current_bottom = max(w["bottom"] for w in lines[i - 1])
        next_top = min(w["top"] for w in lines[i])
        spacing = next_top - current_bottom

        if spacing > block_threshold:
            # Start new block
            blocks.append(current_block)
            current_block = [lines[i]]
        else:
            current_block.append(lines[i])

    # Don't forget last block
    if current_block:
        blocks.append(current_block)

    return blocks
