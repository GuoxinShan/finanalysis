# src/finanalysis/pipeline.py
import logging
from pathlib import Path
from typing import Optional

from .config import Settings
from .stages.stage1_preprocess import Stage1Preprocessor
from .stages.stage2_text import Stage2TextExtractor
from .stages.stage3_tables import Stage3TableExtractor
from .stages.stage4_metrics import Stage4MetricExtractor
from .stages.stage5_aggregate import Stage5Aggregator
from .fs_index import FSIndex

logger = logging.getLogger(__name__)


class Pipeline:
    """PDF parsing pipeline orchestrator"""

    def __init__(self, settings: Settings):
        """Initialize pipeline with settings

        Args:
            settings: Application settings
        """
        self.settings = settings

    def run(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        force: bool = False,
        stop_at_stage: Optional[int] = None
    ) -> dict:
        """Run full PDF parsing pipeline

        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory (default: settings.output_dir)
            force: Force reprocess, ignore cache
            stop_at_stage: Stop after this stage (1-5), for testing

        Returns:
            Summary dict with processing results

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF path is invalid
        """
        # Validate inputs
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if not pdf_path_obj.is_file():
            raise ValueError(f"Not a file: {pdf_path}")

        # Setup output directory
        output = Path(output_dir) if output_dir else Path(self.settings.output_dir)
        output.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting pipeline for {pdf_path}")
        logger.info(f"Output directory: {output}")

        # Override cache if force is set
        if force:
            original_cache = self.settings.cache_enabled
            self.settings.cache_enabled = False
            logger.info("Cache disabled (force=True)")

        try:
            # Stage 1: Preprocessing
            logger.info("Stage 1: Preprocessing")
            stage1 = Stage1Preprocessor(settings=self.settings)
            doc_manifest, page_manifests = stage1.process(
                pdf_path=pdf_path,
                output_dir=output
            )

            if stop_at_stage == 1:
                logger.info("Stopping at Stage 1 (testing mode)")
                return {"status": "stopped", "stage": 1}

            # Stage 2: Text extraction
            logger.info("Stage 2: Text extraction")
            stage2 = Stage2TextExtractor(settings=self.settings)
            text_blocks, page_manifests = stage2.process(
                pdf_path=pdf_path,
                doc_manifest=doc_manifest,
                page_manifests=page_manifests,
                output_dir=output
            )

            if stop_at_stage == 2:
                logger.info("Stopping at Stage 2 (testing mode)")
                return {"status": "stopped", "stage": 2}

            # Stage 3: Table extraction
            logger.info("Stage 3: Table extraction")
            stage3 = Stage3TableExtractor(settings=self.settings)
            table_rows, page_manifests = stage3.process(
                pdf_path=pdf_path,
                doc_manifest=doc_manifest,
                page_manifests=page_manifests,
                output_dir=output
            )

            if stop_at_stage == 3:
                logger.info("Stopping at Stage 3 (testing mode)")
                return {"status": "stopped", "stage": 3}

            # Stage 4: Metric extraction (LLM-based + structured FSIndex)
            logger.info("Stage 4: Metric extraction")
            stage4 = Stage4MetricExtractor(settings=self.settings)
            metrics = stage4.process(
                pdf_path=pdf_path,
                doc_manifest=doc_manifest,
                page_manifests=page_manifests,
                table_rows=table_rows,
                output_dir=output,
                text_blocks=[b.model_dump() for b in text_blocks]
            )

            # Structured extraction via FSIndex (no LLM, direct parsing)
            logger.info("Stage 4b: Structured financial statement extraction")
            fs_index = FSIndex.from_pdf(Path(pdf_path))
            if fs_index.line_items:
                fs_index.save(output / "fs_index.json")

            if stop_at_stage == 4:
                logger.info("Stopping at Stage 4 (testing mode)")
                return {"status": "stopped", "stage": 4}

            # Stage 5: Aggregation
            logger.info("Stage 5: Aggregation")
            stage5 = Stage5Aggregator(settings=self.settings)
            summary = stage5.process(
                pdf_path=pdf_path,
                doc_manifest=doc_manifest,
                page_manifests=page_manifests,
                text_blocks=text_blocks,
                table_rows=table_rows,
                metrics=metrics,
                output_dir=output
            )

            # Append FSIndex metrics after Stage 5 (which overwrites the file)
            if fs_index.line_items:
                self._write_fs_metrics(fs_index, output)

            logger.info("Pipeline complete!")
            return summary

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

        finally:
            # Restore cache setting if it was overridden
            if force:
                self.settings.cache_enabled = original_cache

    @staticmethod
    def _write_fs_metrics(fs_index: FSIndex, output_dir: Path):
        """Write FSIndex line items to metric_candidates.jsonl (append)."""
        import json
        path = output_dir / "metric_candidates.jsonl"
        with open(path, "a") as f:
            for key, entry in fs_index.line_items.items():
                # Skip section-qualified duplicates (keep only unqualified)
                if "(" in key:
                    continue
                for entity in ["group", "company"]:
                    for period_label, period_key in [("current", "current"), ("prior", "prior")]:
                        col = f"{entity}_{period_key}"
                        val = entry.get(col)
                        if val is None:
                            continue
                        record = {
                            "id": f"fs-{key}-{entity}-{period_label}",
                            "metric_type": key,
                            "value": abs(val),
                            "currency": "MYR",
                            "period": period_label,
                            "source_table_row_id": f"fs-page-{entry.get('page', 0)}",
                            "source_text": entry.get("label", key),
                            "confidence": 1.0,
                            "entity": entity,
                            "statement": entry.get("statement", ""),
                            "section": entry.get("section", ""),
                        }
                        f.write(json.dumps(record) + "\n")
        logger.info(f"Appended FSIndex metrics to {path}")
