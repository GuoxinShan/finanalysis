# src/finanalysis/stages/stage1_preprocess.py
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

from ..models import DocumentManifest, PageManifest
from ..extractors.pdf_utils import open_pdf, classify_page, get_page_dimensions
from ..cache import CacheManager
from ..config import Settings


class Stage1Preprocessor:
    """Stage 1: PDF Preprocessing and page classification"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.cache_mgr = CacheManager(Path(settings.cache_dir))

    def process(
        self, pdf_path: str, output_dir: Path
    ) -> Tuple[DocumentManifest, List[PageManifest]]:
        """Process PDF and generate manifests"""

        # Compute hash
        pdf_hash = self.cache_mgr.compute_pdf_hash(pdf_path)

        # Check cache
        if self.settings.cache_enabled and self.cache_mgr.is_cached(pdf_hash, stage=1):
            # Load from cache
            cached = self.cache_mgr.load_cache(pdf_hash, stage=1)
            doc_manifest = DocumentManifest(**cached["document_manifest"])
            page_manifests = [PageManifest(**p) for p in cached["page_manifests"]]
            return doc_manifest, page_manifests

        # Process PDF
        file_size = os.path.getsize(pdf_path)
        page_manifests = []

        with open_pdf(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, start=1):
                # Compute page content hash (simplified)
                text = page.extract_text() or ""
                import hashlib

                content_hash = hashlib.md5(text.encode()).hexdigest()

                # Classify page
                page_type = classify_page(page)

                # Get dimensions
                width, height = get_page_dimensions(page)

                # Create page manifest
                page_manifest = PageManifest(
                    page_number=page_num,
                    page_type=page_type,
                    width=width,
                    height=height,
                    content_hash=content_hash,
                )
                page_manifests.append(page_manifest)

        # Count page types
        page_types = {}
        for pm in page_manifests:
            page_types[pm.page_type] = page_types.get(pm.page_type, 0) + 1

        # Create document manifest
        doc_manifest = DocumentManifest(
            pdf_path=pdf_path,
            pdf_hash=pdf_hash,
            total_pages=total_pages,
            file_size_bytes=file_size,
            processed_at=datetime.now(),
            page_types=page_types,
            text_block_count=0,  # Will be updated in later stages
            table_row_count=0,
            metric_candidate_count=0,
            config_snapshot={
                "cache_enabled": self.settings.cache_enabled,
                "llm_model": self.settings.llm_model,
            },
        )

        # Save to cache
        if self.settings.cache_enabled:
            self.cache_mgr.save_cache(
                pdf_hash,
                stage=1,
                data={
                    "document_manifest": doc_manifest.model_dump(mode="json"),
                    "page_manifests": [p.model_dump(mode="json") for p in page_manifests],
                },
            )

        # Save output files
        output_dir.mkdir(exist_ok=True, parents=True)

        with open(output_dir / "document_manifest.json", "w") as f:
            json.dump(doc_manifest.model_dump(mode="json"), f, indent=2, default=str)

        with open(output_dir / "page_manifests.jsonl", "w") as f:
            for pm in page_manifests:
                f.write(json.dumps(pm.model_dump(mode="json")) + "\n")

        return doc_manifest, page_manifests
