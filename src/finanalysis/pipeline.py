# src/finanalysis/pipeline.py
import json
import logging
from pathlib import Path
from typing import Optional

from .config import Settings
from .stages.stage1_preprocess import Stage1Preprocessor
from .stages.stage2_text import Stage2TextExtractor
from .stages.stage3_tables import Stage3TableExtractor
from .stages.stage5_aggregate import Stage5Aggregator
from .fs_index import FSIndex

logger = logging.getLogger(__name__)


class Pipeline:
    """PDF parsing pipeline orchestrator"""

    def __init__(self, settings: Settings):
        self.settings = settings

    def run(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        force: bool = False,
        stop_at_stage: Optional[int] = None,
        company_name: Optional[str] = None,
    ) -> dict:
        """Run full PDF parsing pipeline

        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory (default: settings.output_dir)
            force: Force reprocess, ignore cache
            stop_at_stage: Stop after this stage (1-5), for testing
            company_name: Company name or stock code (e.g. "Chin Hin Group Berhad", "CHINHIN")

        Returns:
            Summary dict with processing results

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF path is invalid
        """
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if not pdf_path_obj.is_file():
            raise ValueError(f"Not a file: {pdf_path}")

        output = Path(output_dir) if output_dir else Path(self.settings.output_dir)
        output.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting pipeline for {pdf_path}")
        logger.info(f"Output directory: {output}")

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

            # Stage 4: Structured financial statement extraction
            logger.info("Stage 4: Structured financial statement extraction")
            fs_index = FSIndex.from_pdf(Path(pdf_path), company_name=company_name)
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
                metrics=[],
                output_dir=output
            )

            # Write FSIndex metrics as metric_candidates.jsonl
            # (after Stage 5 which creates the file)
            if fs_index.line_items:
                records_written = self._write_fs_metrics(fs_index, output)
                doc_manifest.metric_candidate_count = records_written
                summary["statistics"]["metrics"] = records_written

                # Re-save manifest with updated metric count
                with open(output / "document_manifest.json", "w") as f:
                    json.dump(doc_manifest.model_dump(mode="json"), f, indent=2, default=str)

            logger.info("Pipeline complete!")
            return summary

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

        finally:
            if force:
                self.settings.cache_enabled = original_cache

    @staticmethod
    def _write_fs_metrics(fs_index: FSIndex, output_dir: Path) -> int:
        """Write FSIndex line items to metric_candidates.jsonl.

        Returns:
            Number of records written
        """
        import json
        from datetime import date

        # Load page manifests to get page types for confidence scoring
        page_types = {}
        page_manifests_path = output_dir / "page_manifests.jsonl"
        if page_manifests_path.exists():
            with open(page_manifests_path, "r") as f:
                for line in f:
                    pm = json.loads(line)
                    page_types[pm["page_number"]] = pm.get("page_type", "mixed")

        # Derive absolute year labels from fiscal_year_end
        # e.g. fiscal_year_end="2024-12-31" -> current_year="FY2024", prior_year="FY2023"
        current_year = None
        prior_year = None
        if fs_index.fiscal_year_end:
            try:
                fy = date.fromisoformat(fs_index.fiscal_year_end)
                current_year = f"FY{fy.year}"
                prior_year = f"FY{fy.year - 1}"
            except ValueError:
                pass

        records_written = 0
        path = output_dir / "metric_candidates.jsonl"
        with open(path, "w") as f:
            for key, entry in fs_index.line_items.items():
                if "(" in key:
                    continue
                for entity in ["group", "company"]:
                    for period_label, period_key, year_label in [
                        ("current", "current", current_year),
                        ("prior", "prior", prior_year),
                    ]:
                        col = f"{entity}_{period_key}"
                        val = entry.get(col)
                        if val is None:
                            continue

                        # Calculate confidence based on page type
                        page_num = entry.get("page", 0)
                        page_type = page_types.get(page_num, "mixed")
                        confidence = Pipeline._calculate_confidence(page_type)

                        record = {
                            "id": f"fs-{key}-{entity}-{period_label}",
                            "metric_type": key,
                            "value": abs(val),
                            "currency": fs_index.currency,
                            "period": year_label or period_label,
                            "fiscal_year_end": fs_index.fiscal_year_end,
                            "company_name": fs_index.company_name,
                            "source_table_row_id": f"fs-page-{page_num}",
                            "source_text": entry.get("label", key),
                            "confidence": confidence,
                            "entity": entity,
                            "statement": entry.get("statement", ""),
                            "section": entry.get("section", ""),
                        }
                        f.write(json.dumps(record) + "\n")
                        records_written += 1
        logger.info(f"Wrote FSIndex metrics to {path}")
        return records_written

    @staticmethod
    def _calculate_confidence(page_type: str) -> float:
        """Calculate confidence score based on page type.

        Args:
            page_type: One of "native_text", "table", "mixed", "ocr_only"

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence for structured FSIndex extraction
        base_confidence = 0.95

        # Adjust based on page quality
        if page_type == "native_text":
            # High quality - direct text extraction
            return min(1.0, base_confidence + 0.05)
        elif page_type == "table":
            # High quality - structured table extraction
            return min(1.0, base_confidence + 0.05)
        elif page_type == "mixed":
            # Good quality - combination of text and tables
            return base_confidence
        elif page_type == "ocr_only":
            # Lower quality - OCR required
            return max(0.85, base_confidence - 0.10)
        else:
            # Unknown page type
            return 0.90
