# src/finanalysis/cache.py
import hashlib
from pathlib import Path
from typing import Any, Optional
import json

class CacheManager:
    """File hash-based cache management"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True, parents=True)

    def compute_pdf_hash(self, pdf_path: str) -> str:
        """Compute SHA256 hash of PDF file"""
        sha256 = hashlib.sha256()
        with open(pdf_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def get_cache_key(self, pdf_hash: str, stage: int) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{pdf_hash}_stage{stage}.json"

    def is_cached(self, pdf_hash: str, stage: int) -> bool:
        """Check if cache exists"""
        cache_file = self.get_cache_key(pdf_hash, stage)
        return cache_file.exists()

    def load_cache(self, pdf_hash: str, stage: int) -> Any:
        """Load cache"""
        cache_file = self.get_cache_key(pdf_hash, stage)
        with open(cache_file) as f:
            return json.load(f)

    def save_cache(self, pdf_hash: str, stage: int, data: Any):
        """Save cache"""
        cache_file = self.get_cache_key(pdf_hash, stage)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

    def invalidate(self, pdf_hash: str, stage: Optional[int] = None):
        """Clear cache"""
        if stage is not None:
            cache_file = self.get_cache_key(pdf_hash, stage)
            cache_file.unlink(missing_ok=True)
        else:
            # Clear all stages
            for s in range(1, 6):
                cache_file = self.get_cache_key(pdf_hash, s)
                cache_file.unlink(missing_ok=True)
