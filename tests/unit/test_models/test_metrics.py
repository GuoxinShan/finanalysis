# tests/unit/test_models/test_metrics.py
from src.finanalysis.models.metrics import MetricType, MetricCandidate

def test_metric_type_enum():
    assert MetricType.REVENUE == "revenue"
    assert MetricType.GROSS_PROFIT == "gross_profit"
    assert MetricType.OPERATING_INCOME == "operating_income"
    assert MetricType.NET_INCOME == "net_income"
    assert MetricType.EPS == "eps"
    assert MetricType.OPERATING_CASH_FLOW == "operating_cash_flow"

def test_metric_candidate_creation():
    candidate = MetricCandidate(
        id="metric-id-789",
        metric_type=MetricType.REVENUE,
        value=1234567.0,
        unit="million",
        currency="USD",
        period="2023",
        source_table_row_id="row-id-456",
        source_text="Total Revenue: $1,234,567 million",
        confidence=0.95,
        reasoning="Found in 'Total Revenue' column"
    )

    assert candidate.metric_type == MetricType.REVENUE
    assert candidate.value == 1234567.0
    assert candidate.unit == "million"
    assert candidate.confidence == 0.95
