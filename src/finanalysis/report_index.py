# src/finanalysis/report_index.py
"""Multi-company, multi-year report registry.

Wraps multiple FSIndex objects so you can query across companies and years.

Usage:
    registry = ReportIndex()
    registry.add("output/CHINHIN/2023")
    registry.add("output/CHINHIN/2024")

    registry.query("revenue", company="CHINHIN", year=2024)
    registry.query_series("revenue", company="CHINHIN")
    registry.companies()
    registry.years("CHINHIN")

Persistent registry (saved to disk):
    registry.save("output/registry.json")
    registry = ReportIndex.load("output/registry.json")
"""
import json
import logging
from pathlib import Path
from typing import Optional

from .fs_index import FSIndex

logger = logging.getLogger(__name__)

_DEFAULT_REGISTRY = Path("output/registry.json")


class ReportIndex:
    """Registry of FSIndex objects keyed by (company, year)."""

    def __init__(self):
        # {company_key: {year: FSIndex}}
        self._indexes: dict[str, dict[int, FSIndex]] = {}
        # Track output dirs for persistence
        self._dirs: list[str] = []

    def add(self, output_dir: str | Path) -> Optional[FSIndex]:
        """Load an FSIndex from a pipeline output directory and register it."""
        out = Path(output_dir)
        fs_path = out / "fs_index.json"
        if not fs_path.exists():
            logger.warning(f"No fs_index.json in {out}")
            return None

        idx = FSIndex.load(fs_path)
        if not idx.line_items:
            logger.warning(f"Empty fs_index in {out}")
            return None

        company = idx.company_name
        if not company:
            logger.warning(f"No company_name in {fs_path} — run pipeline with --company flag")
            return None

        year = None
        if idx.fiscal_year_end:
            try:
                year = int(idx.fiscal_year_end[:4])
            except ValueError:
                pass
        if not year:
            logger.warning(f"No fiscal_year_end in {fs_path}")
            return None

        company_key = company.upper().strip()
        if company_key not in self._indexes:
            self._indexes[company_key] = {}
        self._indexes[company_key][year] = idx

        dir_str = str(out.resolve())
        if dir_str not in self._dirs:
            self._dirs.append(dir_str)

        logger.info(f"Registered {company_key} FY{year} ({len(idx.line_items)} items)")
        return idx

    def add_many(self, output_dirs: list[str | Path]) -> "ReportIndex":
        for d in output_dirs:
            self.add(d)
        return self

    def save(self, path: str | Path = _DEFAULT_REGISTRY):
        """Persist the registry (list of output dirs) to disk."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            json.dump({"dirs": self._dirs}, f, indent=2)
        logger.info(f"Registry saved to {p} ({len(self._dirs)} dirs)")

    @classmethod
    def load(cls, path: str | Path = _DEFAULT_REGISTRY) -> "ReportIndex":
        """Load a previously saved registry from disk."""
        p = Path(path)
        if not p.exists():
            return cls()
        with open(p) as f:
            data = json.load(f)
        registry = cls()
        for d in data.get("dirs", []):
            registry.add(d)
        return registry

    def companies(self) -> list[str]:
        return sorted(self._indexes.keys())

    def years(self, company: str) -> list[int]:
        key = company.upper().strip()
        return sorted(self._indexes.get(key, {}).keys())

    def get_index(self, company: str, year: int) -> Optional[FSIndex]:
        key = company.upper().strip()
        return self._indexes.get(key, {}).get(year)

    def query(self, label: str, company: str, year: int) -> Optional[dict]:
        """Look up a metric by label, company, and year.

        Returns dict with group/company values, or None if not found.
        """
        idx = self.get_index(company, year)
        if idx is None:
            return None

        group_val = idx.lookup(label, entity="group", period="current")
        company_val = idx.lookup(label, entity="company", period="current")

        if group_val is None and company_val is None:
            return None

        return {
            "label": label,
            "group": group_val,
            "company": company_val,
            "currency": idx.currency,
            "fiscal_year_end": idx.fiscal_year_end,
        }

    def query_series(self, label: str, company: str, entity: str = "group") -> list[dict]:
        """Query a metric across all available years for a company."""
        key = company.upper().strip()
        results = []
        for year, idx in sorted(self._indexes.get(key, {}).items()):
            val = idx.lookup(label, entity=entity, period="current")
            results.append({
                "year": year,
                "value": val,
                "currency": idx.currency,
                "fiscal_year_end": idx.fiscal_year_end,
            })
        return results

