# tests/unit/test_cache.py
import tempfile
from pathlib import Path
from src.finanalysis.cache import CacheManager

def test_compute_pdf_hash():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test PDF file
        test_file = Path(tmpdir) / "test.pdf"
        test_file.write_text("test content")

        cache_mgr = CacheManager(Path(tmpdir) / "cache")
        hash1 = cache_mgr.compute_pdf_hash(str(test_file))

        # Same content should produce same hash
        hash2 = cache_mgr.compute_pdf_hash(str(test_file))
        assert hash1 == hash2

        # Different content should produce different hash
        test_file.write_text("different content")
        hash3 = cache_mgr.compute_pdf_hash(str(test_file))
        assert hash1 != hash3

def test_cache_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "cache"
        cache_mgr = CacheManager(cache_dir)

        pdf_hash = "test-hash-123"
        stage = 1
        test_data = {"key": "value", "number": 42}

        # Test save and load
        cache_mgr.save_cache(pdf_hash, stage, test_data)

        assert cache_mgr.is_cached(pdf_hash, stage)

        loaded_data = cache_mgr.load_cache(pdf_hash, stage)
        assert loaded_data == test_data

        # Test invalidate
        cache_mgr.invalidate(pdf_hash, stage)
        assert not cache_mgr.is_cached(pdf_hash, stage)
