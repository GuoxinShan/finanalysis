# src/finanalysis/retrieval.py
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ChunkRetriever:
    """Keyword-based retrieval over pipeline output chunks"""

    def __init__(self, output_dir: Path):
        """Initialize retriever from pipeline output directory

        Args:
            output_dir: Directory containing pipeline output files
        """
        self.output_dir = Path(output_dir)
        self.text_blocks = self._load_text_blocks()
        self.table_rows = self._load_table_rows()

        logger.info(
            f"Loaded {len(self.text_blocks)} text blocks and "
            f"{len(self.table_rows)} table rows from {output_dir}"
        )

    def _load_text_blocks(self) -> List[Dict]:
        """Load text blocks from JSONL file"""
        path = self.output_dir / "text_blocks.jsonl"
        if not path.exists():
            return []
        blocks = []
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    blocks.append(json.loads(line))
        return blocks

    def _load_table_rows(self) -> List[Dict]:
        """Load table rows from JSONL file"""
        path = self.output_dir / "table_rows.jsonl"
        if not path.exists():
            return []
        rows = []
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
        return rows

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Keyword search across text blocks and table rows

        Args:
            query: Search query string
            top_k: Maximum number of results to return

        Returns:
            List of result dicts with id, text, page_number, source, score
        """
        query_lower = query.lower()
        results = []

        # Search text blocks
        for block in self.text_blocks:
            text = block.get("text", "")
            score = self._score(query_lower, text)
            if score > 0:
                results.append({
                    "id": block["id"],
                    "text": text,
                    "page_number": block["page_number"],
                    "source": "text",
                    "score": score,
                    "bbox": block.get("bbox"),
                })

        # Search table rows (join cells as text)
        for row in self.table_rows:
            cells = row.get("cells", [])
            text = " | ".join(str(c) for c in cells if c)
            score = self._score(query_lower, text)
            if score > 0:
                results.append({
                    "id": row["id"],
                    "text": text,
                    "page_number": row["page_number"],
                    "source": "table",
                    "score": score,
                    "bbox": row.get("bbox"),
                    "table_index": row.get("table_index"),
                    "row_index": row.get("row_index"),
                })

        # Sort by score descending, return top_k
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    def _score(self, query_lower: str, text: str) -> float:
        """Score a text against a query using keyword matching

        Args:
            query_lower: Lowercase query string
            text: Text to score

        Returns:
            Score between 0.0 and 1.0
        """
        if not text:
            return 0.0

        text_lower = text.lower()
        terms = query_lower.split()

        if not terms:
            return 0.0

        # Count how many query terms appear in text
        matches = sum(1 for term in terms if term in text_lower)
        return matches / len(terms)
