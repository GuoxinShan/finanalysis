# src/finanalysis/stages/stage5_aggregate.py
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from ..config import Settings
from ..models import DocumentManifest, PageManifest, TextBlock, TableRow, MetricCandidate

logger = logging.getLogger(__name__)


class Stage5Aggregator:
    """Stage 5: Aggregate results and generate final outputs"""

    def __init__(self, settings: Settings):
        """Initialize Stage 5 aggregator

        Args:
            settings: Application settings
        """
        self.settings = settings

    def process(
        self,
        pdf_path: str,
        doc_manifest: DocumentManifest,
        page_manifests: List[PageManifest],
        text_blocks: List[TextBlock],
        table_rows: List[TableRow],
        metrics: List[MetricCandidate],
        output_dir: Path
    ) -> Dict[str, Any]:
        """Aggregate all results and generate final outputs

        Args:
            pdf_path: Path to PDF file
            doc_manifest: Document manifest
            page_manifests: List of page manifests
            text_blocks: List of text blocks from Stage 2
            table_rows: List of table rows from Stage 3
            metrics: List of metric candidates from Stage 4
            output_dir: Output directory for results

        Returns:
            Summary dict with processing statistics
        """
        logger.info("Stage 5: Aggregating results")

        # Save all final outputs
        self._save_all_outputs(
            doc_manifest=doc_manifest,
            page_manifests=page_manifests,
            text_blocks=text_blocks,
            table_rows=table_rows,
            metrics=metrics,
            output_dir=output_dir
        )

        # Generate summary
        summary = self._generate_summary(
            pdf_path=pdf_path,
            doc_manifest=doc_manifest,
            text_blocks=text_blocks,
            table_rows=table_rows,
            metrics=metrics
        )

        # Save summary
        self._save_summary(summary=summary, output_dir=output_dir)

        logger.info(f"Stage 5 complete: processed {doc_manifest.total_pages} pages")
        return summary

    def _save_all_outputs(
        self,
        doc_manifest: DocumentManifest,
        page_manifests: List[PageManifest],
        text_blocks: List[TextBlock],
        table_rows: List[TableRow],
        metrics: List[MetricCandidate],
        output_dir: Path
    ):
        """Save all final output files

        Args:
            doc_manifest: Document manifest
            page_manifests: List of page manifests
            text_blocks: List of text blocks
            table_rows: List of table rows
            metrics: List of metric candidates
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save document manifest
        with open(output_dir / "document_manifest.json", 'w') as f:
            json.dump(doc_manifest.model_dump(), f, indent=2, default=str)

        # Save page manifests as JSONL
        with open(output_dir / "page_manifests.jsonl", 'w') as f:
            for pm in page_manifests:
                f.write(json.dumps(pm.model_dump(), default=str) + "\n")

        # Save text blocks as JSONL
        with open(output_dir / "text_blocks.jsonl", 'w') as f:
            for block in text_blocks:
                f.write(json.dumps(block.model_dump(), default=str) + "\n")

        # Save table rows as JSONL
        with open(output_dir / "table_rows.jsonl", 'w') as f:
            for row in table_rows:
                f.write(json.dumps(row.model_dump(), default=str) + "\n")

        # Save metric candidates as JSONL
        with open(output_dir / "metric_candidates.jsonl", 'w') as f:
            for metric in metrics:
                f.write(json.dumps(metric.model_dump(), default=str) + "\n")

        logger.info(f"Saved all outputs to {output_dir}")

    def _generate_summary(
        self,
        pdf_path: str,
        doc_manifest: DocumentManifest,
        text_blocks: List[TextBlock],
        table_rows: List[TableRow],
        metrics: List[MetricCandidate]
    ) -> Dict[str, Any]:
        """Generate processing summary

        Args:
            pdf_path: Path to PDF file
            doc_manifest: Document manifest
            text_blocks: List of text blocks
            table_rows: List of table rows
            metrics: List of metric candidates

        Returns:
            Summary dict
        """
        summary = {
            "status": "success",
            "pdf_path": pdf_path,
            "pdf_hash": doc_manifest.pdf_hash,
            "processed_at": doc_manifest.processed_at.isoformat(),
            "statistics": {
                "total_pages": doc_manifest.total_pages,
                "page_types": doc_manifest.page_types,
                "text_blocks": len(text_blocks),
                "table_rows": len(table_rows),
                "metrics": len(metrics),
            },
            "extracted_metrics": [
                {
                    "type": m.metric_type.value,
                    "value": m.value,
                    "currency": m.currency,
                    "period": m.period,
                    "confidence": m.confidence,
                }
                for m in metrics
            ],
            "processing_notes": []
        }

        # Add processing notes based on results
        if len(text_blocks) == 0:
            summary["processing_notes"].append("No text blocks extracted")

        if len(table_rows) == 0:
            summary["processing_notes"].append("No table rows extracted")

        if len(metrics) == 0:
            summary["processing_notes"].append("No metrics extracted")
        elif len(metrics) < 3:
            summary["processing_notes"].append(
                f"Only {len(metrics)} metrics extracted - manual review recommended"
            )

        return summary

    def _save_summary(self, summary: Dict[str, Any], output_dir: Path):
        """Save summary to JSON file

        Args:
            summary: Summary dict
            output_dir: Output directory
        """
        summary_path = output_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Saved summary to {summary_path}")
