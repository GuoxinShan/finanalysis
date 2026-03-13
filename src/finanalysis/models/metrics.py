# src/finanalysis/models/metrics.py
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class MetricType(str, Enum):
    """Financial metric types"""
    REVENUE = "revenue"
    GROSS_PROFIT = "gross_profit"
    OPERATING_INCOME = "operating_income"
    NET_INCOME = "net_income"
    EPS = "eps"  # Earnings Per Share
    OPERATING_CASH_FLOW = "operating_cash_flow"

class MetricCandidate(BaseModel):
    """Metric candidate extracted by LLM"""
    id: str
    metric_type: MetricType
    value: float
    unit: Optional[str] = None  # "million", "billion", None
    currency: Optional[str] = None  # "USD", "CNY", None
    period: Optional[str] = None  # "2023", "Q1 2023", None

    # Source tracking
    source_table_row_id: str
    source_text: str

    # LLM metadata
    confidence: float  # 0-1
    reasoning: Optional[str] = None
