# src/finanalysis/report_index.py
"""Multi-company, multi-year report registry.

Wraps multiple FSIndex objects so you can query across companies and years
without knowing which PDF or output directory to look in.

Usage:
    registry = ReportIndex()
    registry.add("output/CHINHIN/2023")
    registry.add("output/CHINHIN/2024")
    registry.add("output/PBBANK/2024")

    # Query by company + year
    registry.query("revenue", company="CHINHIN", year=2024)
    # -> {"group": 3252347.0, "company": 18353.0, "currency": "MYR", "fiscal_year_end": "2024-12-31"}

    registry.companies()   # ["CHINHIN", "PBBANK"]
    registry.years("CHINHIN")  # [2023, 2024]
"""
import logging
from pathlib import Path
from typing import Optional

from .fs_index import FSIndex

logger = logging.getLogger(__name__)


class ReportIndex:
    """Registry of FSIndex objects keyed by (company, year)."""

    def __init__(self):
        # {company_key: {year: FSIndex}}
        self._indexes: dict[str, dict[int, FSIndex]] = {}

    def add(self, output_dir: str | Path) -> Optional[FSIndex]:
        """Load an FSIndex from a pipeline output directory and register it.

        The company key comes from fs_index.company_name (set via --company flag).
        The year comes from fs_index.fiscal_year_end.

        Returns the loaded FSIndex, or None if loading failed.
        """
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
        logger.info(f"Registered {company_key} FY{year} ({len(idx.line_items)} items)")
        return idx

    def add_many(self, output_dirs: list[str | Path]) -> "ReportIndex":
        """Add multiple output directories. Returns self for chaining."""
        for d in output_dirs:
            self.add(d)
        return self

    def companies(self) -> list[str]:
        """List all registered company keys."""
        return sorted(self._indexes.keys())

    def years(self, company: str) -> list[int]:
        """List available years for a company."""
        key = company.upper().strip()
        return sorted(self._indexes.get(key, {}).keys())

    def get_index(self, company: str, year: int) -> Optional[FSIndex]:
        """Get the FSIndex for a specific company and year."""
        key = company.upper().strip()
        return self._indexes.get(key, {}).get(year)

    def query(
        self,
        label: str,
        company: str,
        year: int,
    ) -> Optional[dict]:
        """Look up a metric by label, company, and year.

        Returns a dict with group and company values (whichever are available):
            {
                "group": 3252347.0,
                "company": 18353.0,   # None if not available
                "currency": "MYR",
                "fiscal_year_end": "2024-12-31",
                "label": "revenue",
            }
        Returns None if the company/year is not registered or label not found.
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

    def query_series(
        self,
        label: str,
        company: str,
        entity: str = "group",
    ) -> list[dict]:
        """Query a metric across all available years for a company.

        Returns list of {year, value, currency, fiscal_year_end} sorted by year.
        """
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
