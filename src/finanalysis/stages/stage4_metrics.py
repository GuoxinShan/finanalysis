# src/finanalysis/stages/stage4_metrics.py
import json
import logging
from pathlib import Path
from typing import List, Optional

from ..config import Settings
from ..models import DocumentManifest, PageManifest, TableRow, MetricCandidate, MetricType
from ..llm.client import LLMClient

logger = logging.getLogger(__name__)


class Stage4MetricExtractor:
    """Stage 4: Extract financial metrics from table rows using LLM"""

    def __init__(self, settings: Settings):
        """Initialize Stage 4 extractor

        Args:
            settings: Application settings
        """
        self.settings = settings

        # Initialize LLM client with system prompt
        system_prompt = """You are a financial analyst expert at extracting key metrics from financial tables.

Given table row data, identify and extract financial metrics such as:
- Revenue
- Gross Profit
- Operating Income
- Net Income
- Earnings Per Share (EPS)
- Operating Cash Flow

For each metric found, provide:
- metric_type: One of "revenue", "gross_profit", "operating_income", "net_income", "eps", "operating_cash_flow"
- value: Numeric value (float)
- unit: Unit if applicable (e.g., "millions", "thousands")
- currency: Currency code if mentioned (e.g., "USD", "CNY")
- period: Time period if mentioned (e.g., "2023", "Q4 2023")
- confidence: Confidence score between 0.0 and 1.0
- reasoning: Brief explanation of your extraction

Only extract metrics with high confidence (>0.7). Skip headers, labels, or unclear data."""

        self.llm_client = LLMClient(settings=settings, system_prompt=system_prompt)

    def process(
        self,
        pdf_path: str,
        doc_manifest: DocumentManifest,
        page_manifests: List[PageManifest],
        table_rows: List[TableRow],
        output_dir: Path,
        text_blocks: Optional[List] = None
    ) -> List[MetricCandidate]:
        """Extract financial metrics from table rows and text blocks

        Args:
            pdf_path: Path to PDF file
            doc_manifest: Document manifest
            page_manifests: List of page manifests
            table_rows: List of table rows from Stage 3
            output_dir: Output directory for results
            text_blocks: Optional list of text blocks from Stage 2

        Returns:
            List of MetricCandidate objects
        """
        logger.info(f"Stage 4: Extracting metrics from {len(table_rows)} table rows")

        # Extract metrics using LLM
        try:
            metrics = self._extract_metrics_from_tables(table_rows, text_blocks or [])

            # Update manifest
            doc_manifest.metric_candidate_count = len(metrics)

            # Save results
            self._save_results(
                metrics=metrics,
                doc_manifest=doc_manifest,
                page_manifests=page_manifests,
                output_dir=output_dir
            )

            logger.info(f"Extracted {len(metrics)} metric candidates")
            return metrics

        except Exception as e:
            logger.error(f"Failed to extract metrics: {e}")
            # Return empty list on error
            return []

    def _extract_metrics_from_tables(self, table_rows: List[TableRow], text_blocks: List = []) -> List[MetricCandidate]:
        """Extract metrics from table rows and text blocks using LLM

        Args:
            table_rows: List of table rows
            text_blocks: List of text blocks

        Returns:
            List of MetricCandidate objects
        """
        # Build content for LLM - prioritize text blocks with financial keywords
        financial_keywords = ["revenue", "profit", "income", "earnings", "cash flow", "eps"]
        relevant_text_blocks = [
            b for b in text_blocks
            if any(kw in b.get("text", "").lower() for kw in financial_keywords)
        ] if text_blocks else []

        # Format content
        content_parts = []
        if relevant_text_blocks:
            content_parts.append("TEXT BLOCKS:")
            for idx, block in enumerate(relevant_text_blocks[:10]):  # limit to 10
                content_parts.append(f"Block {idx} (page {block.get('page_number')}): {block.get('text', '')[:300]}")

        if table_rows:
            content_parts.append("\nTABLE ROWS:")
            for idx, row in enumerate(table_rows):
                cells_text = " | ".join(row.cells)
                content_parts.append(f"Row {idx} (page {row.page_number}): {cells_text}")

        if not content_parts:
            return []

        content = "\n".join(content_parts)

        # Create prompt
        prompt = f"""Analyze the following content from a financial report and extract key financial metrics.

{content}

IMPORTANT: For each metric, you MUST use the exact "metric_type" values listed below. Do NOT use "name" or other field names.

Valid metric_type values (use these EXACTLY):
- "revenue"
- "gross_profit"
- "operating_income"
- "net_income"
- "eps"
- "operating_cash_flow"

Extract all relevant financial metrics. Respond with a JSON object containing a "metrics" array.

Example format:
{{
  "metrics": [
    {{
      "metric_type": "revenue",
      "value": 1000000.0,
      "currency": "MYR",
      "period": "2023",
      "confidence": 0.95,
      "reasoning": "Revenue row clearly labeled"
    }}
  ]
}}"""

        try:
            # Call LLM
            response = self.llm_client.extract_json(prompt=prompt, temperature=0.0)

            # Parse metrics
            metrics = []
            for metric_data in response.get("metrics", []):
                try:
                    # Map metric type string to enum
                    metric_type_str = metric_data.get("metric_type", "").lower()
                    metric_type = MetricType(metric_type_str)

                    # Create MetricCandidate
                    metric = MetricCandidate(
                        id=f"metric-{len(metrics)}",
                        metric_type=metric_type,
                        value=metric_data.get("value", 0.0),
                        unit=metric_data.get("unit"),
                        currency=metric_data.get("currency"),
                        period=metric_data.get("period"),
                        source_table_row_id="row-unknown",  # We'll link this properly later
                        source_text=", ".join(metric_data.keys()),
                        confidence=metric_data.get("confidence", 0.8),
                        reasoning=metric_data.get("reasoning")
                    )
                    metrics.append(metric)

                except ValueError as e:
                    logger.warning(f"Invalid metric type {metric_type_str}: {e}")
                    continue

            return metrics

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            raise

    def _format_rows_for_llm(self, table_rows: List[TableRow]) -> str:
        """Format table rows as text for LLM

        Args:
            table_rows: List of table rows

        Returns:
            Formatted text
        """
        lines = []
        for idx, row in enumerate(table_rows):
            cells_text = " | ".join(row.cells)
            lines.append(f"Row {idx}: {cells_text}")
        return "\n".join(lines)

    def _save_results(
        self,
        metrics: List[MetricCandidate],
        doc_manifest: DocumentManifest,
        page_manifests: List[PageManifest],
        output_dir: Path
    ):
        """Save Stage 4 results to files

        Args:
            metrics: List of extracted metrics
            doc_manifest: Document manifest
            page_manifests: List of page manifests
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save metrics as JSON
        metrics_json = output_dir / "stage4_metrics.json"
        with open(metrics_json, 'w') as f:
            json.dump([m.model_dump() for m in metrics], f, indent=2, default=str)

        # Save metrics as JSONL
        metrics_jsonl = output_dir / "stage4_metrics.jsonl"
        with open(metrics_jsonl, 'w') as f:
            for metric in metrics:
                f.write(json.dumps(metric.model_dump(), default=str) + "\n")

        # Save updated manifest
        manifest_json = output_dir / "manifest.json"
        with open(manifest_json, 'w') as f:
            json.dump(doc_manifest.model_dump(), f, indent=2, default=str)

        logger.info(f"Saved Stage 4 results to {output_dir}")
