# src/finanalysis/validation/balance_sheet.py
"""Balance sheet validation checks"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a balance sheet validation issue"""
    check_name: str
    expected: float
    actual: float
    difference: float
    entity: str
    period: str
    severity: str  # "error", "warning", "info"
    details: str


class BalanceSheetValidator:
    """Validates balance sheet mathematical accuracy"""

    def __init__(self, tolerance: float = 1.0):
        """Initialize validator

        Args:
            tolerance: Acceptable difference for floating point comparisons (default: 1.0)
        """
        self.tolerance = tolerance

    def validate(
        self,
        metrics: Dict[str, Dict[str, any]],
        entity: str = "group",
        period: str = "current"
    ) -> List[ValidationIssue]:
        """Run all balance sheet validations

        Args:
            metrics: Dictionary of metric_type -> {entity_period: value}
                    e.g. {"total_assets": {"group_current": 1000, "group_prior": 900}}
            entity: Entity to validate ("group" or "company")
            period: Period to validate ("current" or "prior")

        Returns:
            List of validation issues found
        """
        issues = []

        # Check 1: Total Assets = Non-Current Assets + Current Assets
        issues.extend(self._check_asset_equation(metrics, entity, period))

        # Check 2: Total Liabilities + Equity = Total Assets
        issues.extend(self._check_accounting_equation(metrics, entity, period))

        # Check 3: Total Equity = Share Capital + Reserves + Retained Earnings
        issues.extend(self._check_equity_equation(metrics, entity, period))

        return issues

    def _get_value(
        self,
        metrics: Dict[str, Dict],
        metric_type: str,
        entity: str,
        period: str
    ) -> Optional[float]:
        """Extract value for specific entity and period"""
        col = f"{entity}_{period}"
        if metric_type in metrics:
            return metrics[metric_type].get(col)
        return None

    def _check_asset_equation(
        self,
        metrics: Dict[str, Dict],
        entity: str,
        period: str
    ) -> List[ValidationIssue]:
        """Check: Total Assets = Non-Current Assets + Current Assets + Assets Held for Sale"""
        issues = []

        # Try both underscore and space variants
        total = (
            self._get_value(metrics, "total_assets", entity, period) or
            self._get_value(metrics, "total assets", entity, period)
        )
        non_current = (
            self._get_value(metrics, "non_current_assets", entity, period) or
            self._get_value(metrics, "non-current assets", entity, period)
        )
        current = (
            self._get_value(metrics, "current_assets", entity, period) or
            self._get_value(metrics, "current assets", entity, period)
        )
        assets_held_for_sale = (
            self._get_value(metrics, "assets_held_for_sale", entity, period) or
            self._get_value(metrics, "assets held for sale", entity, period)
        )

        if total is None:
            return issues

        # Calculate expected total
        expected = 0.0
        has_components = False

        if non_current is not None:
            expected += non_current
            has_components = True
        if current is not None:
            expected += current
            has_components = True
        # Assets Held for Sale is a separate category per IFRS 5
        if assets_held_for_sale is not None:
            expected += assets_held_for_sale
            has_components = True

        if not has_components:
            return issues

        difference = abs(total - expected)
        if difference > self.tolerance:
            # Try to identify the cause
            details = self._diagnose_asset_discrepancy(
                metrics, entity, period, total, non_current, current, assets_held_for_sale, difference
            )

            issues.append(ValidationIssue(
                check_name="Asset Equation",
                expected=expected,
                actual=total,
                difference=difference,
                entity=entity,
                period=period,
                severity="error" if difference > 1000 else "warning",
                details=details
            ))

        return issues

    def _check_accounting_equation(
        self,
        metrics: Dict[str, Dict],
        entity: str,
        period: str
    ) -> List[ValidationIssue]:
        """Check: Total Assets = Total Liabilities + Total Equity"""
        issues = []

        # Try both underscore and space variants
        total_assets = (
            self._get_value(metrics, "total_assets", entity, period) or
            self._get_value(metrics, "total assets", entity, period)
        )
        total_liabilities = (
            self._get_value(metrics, "total_liabilities", entity, period) or
            self._get_value(metrics, "total liabilities", entity, period) or
            self._get_value(metrics, "total equity and liabilities", entity, period)
        )
        total_equity = (
            self._get_value(metrics, "total_equity", entity, period) or
            self._get_value(metrics, "total equity", entity, period)
        )

        if total_assets is None:
            return issues

        # Calculate expected total
        expected = 0.0
        has_components = False

        # If we have "total equity and liabilities", use it directly
        if total_liabilities and not total_equity:
            # total_liabilities actually contains "total equity and liabilities"
            expected = total_liabilities
            has_components = True
        else:
            if total_liabilities is not None:
                expected += total_liabilities
                has_components = True
            if total_equity is not None:
                expected += total_equity
                has_components = True

        if not has_components:
            return issues

        difference = abs(total_assets - expected)
        if difference > self.tolerance:
            issues.append(ValidationIssue(
                check_name="Accounting Equation",
                expected=expected,
                actual=total_assets,
                difference=difference,
                entity=entity,
                period=period,
                severity="error",
                details="Total Assets ≠ Total Liabilities + Total Equity"
            ))

        return issues

    def _check_equity_equation(
        self,
        metrics: Dict[str, Dict],
        entity: str,
        period: str
    ) -> List[ValidationIssue]:
        """Check: Total Equity = Share Capital + Reserves + Retained Earnings"""
        issues = []

        # Try both underscore and space variants
        total_equity = (
            self._get_value(metrics, "total_equity", entity, period) or
            self._get_value(metrics, "total equity", entity, period)
        )
        share_capital = (
            self._get_value(metrics, "share_capital", entity, period) or
            self._get_value(metrics, "share capital", entity, period)
        )
        reserves = (
            self._get_value(metrics, "reserves", entity, period)
        )
        retained_earnings = (
            self._get_value(metrics, "retained_earnings", entity, period) or
            self._get_value(metrics, "retained earnings", entity, period)
        )

        if total_equity is None:
            return issues

        # Calculate expected total
        expected = 0.0
        has_components = False

        for component in [share_capital, reserves, retained_earnings]:
            if component is not None:
                expected += component
                has_components = True

        if not has_components:
            return issues

        difference = abs(total_equity - expected)
        if difference > self.tolerance:
            issues.append(ValidationIssue(
                check_name="Equity Equation",
                expected=expected,
                actual=total_equity,
                difference=difference,
                entity=entity,
                period=period,
                severity="warning",
                details="Total Equity ≠ Sum of equity components (may have other items)"
            ))

        return issues

    def _diagnose_asset_discrepancy(
        self,
        metrics: Dict[str, Dict],
        entity: str,
        period: str,
        total: float,
        non_current: Optional[float],
        current: Optional[float],
        assets_held_for_sale: Optional[float],
        difference: float
    ) -> str:
        """Try to identify the cause of asset equation discrepancy"""

        # Build components list for diagnosis
        components = []
        if non_current is not None:
            components.append(f"Non-Current: {non_current:,.0f}")
        if current is not None:
            components.append(f"Current: {current:,.0f}")
        if assets_held_for_sale is not None:
            components.append(f"Assets Held for Sale: {assets_held_for_sale:,.0f}")

        expected_sum = (non_current or 0) + (current or 0) + (assets_held_for_sale or 0)

        if abs(difference) <= self.tolerance:
            return f"Equation balanced: {' + '.join(components)} = {expected_sum:,.0f}"

        return (
            f"Total Assets ({total:,.0f}) ≠ {' + '.join(components)} "
            f"= {expected_sum:,.0f}. "
            f"Unexplained difference: {difference:,.0f}"
        )


def format_validation_report(issues: List[ValidationIssue]) -> str:
    """Format validation issues as readable report"""
    if not issues:
        return "✅ All balance sheet equations validated successfully\n"

    lines = ["❌ Balance Sheet Validation Issues:\n"]

    for issue in issues:
        emoji = "🔴" if issue.severity == "error" else "🟡" if issue.severity == "warning" else "ℹ️"
        lines.append(
            f"{emoji} {issue.check_name} ({issue.entity}, {issue.period}):\n"
            f"   Expected: {issue.expected:,.2f}\n"
            f"   Actual: {issue.actual:,.2f}\n"
            f"   Difference: {issue.difference:,.2f}\n"
            f"   Details: {issue.details}\n"
        )

    return "\n".join(lines)
