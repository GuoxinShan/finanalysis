# src/finanalysis/stages/stage3_tables.py
import json
import logging
from pathlib import Path
from typing import List, Tuple

from ..models import DocumentManifest, PageManifest, TableRow
from ..extractors.pdf_utils import open_pdf
from ..extractors.table_extractor import extract_tables_with_fallback
from ..cache import CacheManager
from ..config import Settings

logger = logging.getLogger(__name__)


class Stage3TableExtractor:
    """Stage 3: Table extraction from PDF pages"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.cache_mgr = CacheManager(Path(settings.cache_dir))

    def process(
        self,
        pdf_path: str,
        doc_manifest: DocumentManifest,
        page_manifests: List[PageManifest],
        output_dir: Path,
    ) -> Tuple[List[TableRow], List[PageManifest]]:
        """Extract tables from pages

        Args:
            pdf_path: Path to PDF file
            doc_manifest: Document manifest from Stage 1
            page_manifests: Page manifests from Stage 2
            output_dir: Output directory for results

        Returns:
            Tuple of (table_rows, updated_page_manifests)
        """
        pdf_hash = doc_manifest.pdf_hash

        # Check cache
        if self.settings.cache_enabled and self.cache_mgr.is_cached(pdf_hash, stage=3):
            logger.info(f"Loading Stage 3 results from cache for {pdf_hash}")
            cached = self.cache_mgr.load_cache(pdf_hash, stage=3)
            table_rows = [TableRow(**r) for r in cached["table_rows"]]
            updated_manifests = [PageManifest(**p) for p in cached["page_manifests"]]
            return table_rows, updated_manifests

        all_table_rows = []

        with open_pdf(pdf_path) as pdf:
            for page_manifest in page_manifests:
                page_num = page_manifest.page_number

                # Skip pages that are not table-dominant or mixed
                if page_manifest.page_type not in ["table", "mixed"]:
                    continue

                # Extract tables from page
                page = pdf.pages[page_num - 1]  # 0-indexed
                table_rows = extract_tables_with_fallback(page=page, page_number=page_num)

                # Update page manifest
                page_manifest.table_extracted = True
                page_manifest.table_row_ids = [r.id for r in table_rows]

                all_table_rows.extend(table_rows)

        # Update document manifest
        doc_manifest.table_row_count = len(all_table_rows)

        # Save to cache
        if self.settings.cache_enabled:
            logger.info(f"Caching Stage 3 results for {pdf_hash}")
            self.cache_mgr.save_cache(
                pdf_hash,
                stage=3,
                data={
                    "table_rows": [r.model_dump(mode="json") for r in all_table_rows],
                    "page_manifests": [p.model_dump(mode="json") for p in page_manifests],
                },
            )

        # Save output files
        output_dir.mkdir(exist_ok=True, parents=True)

        with open(output_dir / "table_rows.jsonl", "w") as f:
            for row in all_table_rows:
                f.write(json.dumps(row.model_dump(mode="json")) + "\n")

        with open(output_dir / "page_manifests.jsonl", "w") as f:
            for pm in page_manifests:
                f.write(json.dumps(pm.model_dump(mode="json")) + "\n")

        logger.info(f"Stage 3 complete: extracted {len(all_table_rows)} table rows")
        return all_table_rows, page_manifests
