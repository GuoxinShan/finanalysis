# src/finanalysis/stages/stage2_text.py
import json
import logging
from pathlib import Path
from typing import List, Tuple

from ..models import DocumentManifest, PageManifest, TextBlock
from ..extractors.pdf_utils import open_pdf
from ..extractors.text_extractor import extract_text_blocks
from ..cache import CacheManager
from ..config import Settings

logger = logging.getLogger(__name__)


class Stage2TextExtractor:
    """Stage 2: Text extraction from PDF pages"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.cache_mgr = CacheManager(Path(settings.cache_dir))

    def process(
        self,
        pdf_path: str,
        doc_manifest: DocumentManifest,
        page_manifests: List[PageManifest],
        output_dir: Path,
    ) -> Tuple[List[TextBlock], List[PageManifest]]:
        """Extract text from pages

        Args:
            pdf_path: Path to PDF file
            doc_manifest: Document manifest from Stage 1
            page_manifests: Page manifests from Stage 1
            output_dir: Output directory for results

        Returns:
            Tuple of (text_blocks, updated_page_manifests)
        """
        logger.info(f"Stage 2: Extracting text from {pdf_path}")
        pdf_hash = doc_manifest.pdf_hash

        # Check cache
        if self.settings.cache_enabled and self.cache_mgr.is_cached(pdf_hash, stage=2):
            logger.info(f"Loading Stage 2 results from cache for {pdf_hash}")
            cached = self.cache_mgr.load_cache(pdf_hash, stage=2)
            text_blocks = [TextBlock(**b) for b in cached["text_blocks"]]
            updated_manifests = [PageManifest(**p) for p in cached["page_manifests"]]
            return text_blocks, updated_manifests

        all_text_blocks = []

        with open_pdf(pdf_path) as pdf:
            for page_manifest in page_manifests:
                page_num = page_manifest.page_number

                # Skip pages that are table-dominant
                if page_manifest.page_type == "table":
                    continue

                try:
                    # Extract text from page
                    page = pdf.pages[page_num - 1]  # 0-indexed
                    text_blocks = extract_text_blocks(page, page_number=page_num)

                    # Update page manifest
                    page_manifest.text_extracted = True
                    page_manifest.text_block_ids = [b.id for b in text_blocks]

                    all_text_blocks.extend(text_blocks)

                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}, skipping")
                    continue

        # Update manifest count
        doc_manifest.text_block_count = len(all_text_blocks)

        # Save to cache
        if self.settings.cache_enabled:
            self.cache_mgr.save_cache(
                pdf_hash,
                stage=2,
                data={
                    "text_blocks": [b.model_dump(mode="json") for b in all_text_blocks],
                    "page_manifests": [p.model_dump(mode="json") for p in page_manifests],
                },
            )

        # Save output files
        output_dir.mkdir(exist_ok=True, parents=True)

        with open(output_dir / "text_blocks.jsonl", "w") as f:
            for block in all_text_blocks:
                f.write(json.dumps(block.model_dump(mode="json")) + "\n")

        with open(output_dir / "page_manifests.jsonl", "w") as f:
            for pm in page_manifests:
                f.write(json.dumps(pm.model_dump(mode="json")) + "\n")

        logger.info(f"Stage 2 complete: extracted {len(all_text_blocks)} text blocks")
        return all_text_blocks, page_manifests

