# src/finanalysis/compare.py
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MetricComparer:
    """Compare financial metrics across multiple output directories (years)"""

    def __init__(self, output_dirs: Dict[str, Path]):
        """Initialize comparer with labeled output directories

        Args:
            output_dirs: Dict mapping label (e.g. "2023") to output directory path
        """
        self.output_dirs = {k: Path(v) for k, v in output_dirs.items()}
        self.metrics = self._load_all_metrics()

    def _load_all_metrics(self) -> Dict[str, List[Dict]]:
        """Load metric_candidates.jsonl from each output directory"""
        result = {}
        for label, path in self.output_dirs.items():
            jsonl = path / "metric_candidates.jsonl"
            if not jsonl.exists():
                logger.warning(f"No metric_candidates.jsonl in {path}")
                result[label] = []
                continue
            metrics = []
            with open(jsonl) as f:
                for line in f:
                    if line.strip():
                        metrics.append(json.loads(line))
            result[label] = metrics
            logger.info(f"Loaded {len(metrics)} metrics for {label}")
        return result

    def compare(self, metric_type: str) -> List[Dict[str, Any]]:
        """Compare a single metric type across all labels

        Args:
            metric_type: e.g. "revenue", "net_income"

        Returns:
            List of rows sorted by label, each with label, value, currency, confidence, yoy_growth
        """
        rows = []
        for label in sorted(self.output_dirs.keys()):
            candidates = [
                m for m in self.metrics.get(label, [])
                if m.get("metric_type") == metric_type
            ]
            if not candidates:
                continue

            # Pick highest confidence candidate
            best = max(candidates, key=lambda m: m.get("confidence", 0))
            rows.append({
                "label": label,
                "value": best.get("value"),
                "currency": best.get("currency"),
                "period": best.get("period"),
                "confidence": best.get("confidence"),
            })

        # Add YoY growth
        for i, row in enumerate(rows):
            if i == 0:
                row["yoy_growth"] = None
            else:
                prev = rows[i - 1]["value"]
                curr = row["value"]
                if prev and prev != 0:
                    row["yoy_growth"] = round((curr - prev) / prev * 100, 2)
                else:
                    row["yoy_growth"] = None

        return rows

    def compare_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Compare all metric types across all labels

        Returns:
            Dict keyed by metric_type, each value is a list of comparison rows
        """
        # Collect all metric types seen across all labels
        all_types = set()
        for metrics in self.metrics.values():
            for m in metrics:
                mt = m.get("metric_type")
                if mt:
                    all_types.add(mt)

        return {mt: self.compare(mt) for mt in sorted(all_types)}
