# tests/unit/test_retrieval.py
import pytest
import json
from pathlib import Path

from src.finanalysis.retrieval import ChunkRetriever


@pytest.fixture
def output_dir(tmp_path):
    """Create sample output files for testing"""
    # Write text blocks
    text_blocks = [
        {"id": "text-1", "page_number": 1, "text": "Revenue for the year was RM 1,500,000", "bbox": [0, 0, 100, 20], "embedding": None},
        {"id": "text-2", "page_number": 2, "text": "Net income increased by 15% to RM 300,000", "bbox": [0, 0, 100, 20], "embedding": None},
        {"id": "text-3", "page_number": 3, "text": "The company declared a dividend of RM 0.05 per share", "bbox": [0, 0, 100, 20], "embedding": None},
        {"id": "text-4", "page_number": 4, "text": "Operating expenses were well controlled", "bbox": [0, 0, 100, 20], "embedding": None},
    ]
    with open(tmp_path / "text_blocks.jsonl", "w") as f:
        for block in text_blocks:
            f.write(json.dumps(block) + "\n")

    # Write table rows
    table_rows = [
        {"id": "row-1", "page_number": 5, "table_index": 0, "row_index": 0, "cells": ["Revenue", "1,500,000", "1,200,000"], "bbox": [0, 0, 100, 20], "extraction_method": "pdfplumber", "confidence": 1.0},
        {"id": "row-2", "page_number": 5, "table_index": 0, "row_index": 1, "cells": ["Net Income", "300,000", "250,000"], "bbox": [0, 0, 100, 20], "extraction_method": "pdfplumber", "confidence": 1.0},
        {"id": "row-3", "page_number": 5, "table_index": 0, "row_index": 2, "cells": ["Gross Profit", "750,000", "600,000"], "bbox": [0, 0, 100, 20], "extraction_method": "pdfplumber", "confidence": 1.0},
    ]
    with open(tmp_path / "table_rows.jsonl", "w") as f:
        for row in table_rows:
            f.write(json.dumps(row) + "\n")

    return tmp_path


def test_retriever_loads_chunks(output_dir):
    """Test ChunkRetriever loads text blocks and table rows"""
    retriever = ChunkRetriever(output_dir=output_dir)
    assert len(retriever.text_blocks) == 4
    assert len(retriever.table_rows) == 3


def test_retriever_keyword_search_text(output_dir):
    """Test keyword search across text blocks"""
    retriever = ChunkRetriever(output_dir=output_dir)
    results = retriever.search("revenue")

    assert len(results) > 0
    assert any("revenue" in r["text"].lower() for r in results)


def test_retriever_keyword_search_tables(output_dir):
    """Test keyword search across table rows"""
    retriever = ChunkRetriever(output_dir=output_dir)
    results = retriever.search("net income")

    assert len(results) > 0
    assert any("Net Income" in r["text"] for r in results)


def test_retriever_search_returns_metadata(output_dir):
    """Test search results include metadata"""
    retriever = ChunkRetriever(output_dir=output_dir)
    results = retriever.search("revenue")

    for r in results:
        assert "id" in r
        assert "text" in r
        assert "page_number" in r
        assert "source" in r  # "text" or "table"
        assert "score" in r


def test_retriever_search_top_k(output_dir):
    """Test search respects top_k limit"""
    retriever = ChunkRetriever(output_dir=output_dir)
    results = retriever.search("the", top_k=2)

    assert len(results) <= 2


def test_retriever_search_no_results(output_dir):
    """Test search returns empty list for no matches"""
    retriever = ChunkRetriever(output_dir=output_dir)
    results = retriever.search("xyznonexistentterm123")

    assert results == []


def test_retriever_search_case_insensitive(output_dir):
    """Test search is case insensitive"""
    retriever = ChunkRetriever(output_dir=output_dir)
    results_lower = retriever.search("revenue")
    results_upper = retriever.search("REVENUE")

    assert len(results_lower) == len(results_upper)
