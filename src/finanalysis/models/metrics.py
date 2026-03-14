# src/finanalysis/models/metrics.py
from enum import Enum
from pydantic import BaseModel
from typing import Optional


class MetricType(str, Enum):
    """Financial metric types"""
    # Income statement
    REVENUE = "revenue"
    COST_OF_SALES = "cost_of_sales"
    GROSS_PROFIT = "gross_profit"
    OTHER_INCOME = "other_income"
    FINANCE_INCOME = "finance_income"
    ADMINISTRATIVE_EXPENSES = "administrative_expenses"
    OPERATING_INCOME = "operating_income"
    FINANCE_COSTS = "finance_costs"
    PROFIT_BEFORE_TAX = "profit_before_tax"
    TAXATION = "taxation"
    NET_INCOME = "net_income"
    EPS = "eps"

    # Balance sheet
    TOTAL_ASSETS = "total_assets"
    NON_CURRENT_ASSETS = "non_current_assets"
    CURRENT_ASSETS = "current_assets"
    TOTAL_EQUITY = "total_equity"
    TOTAL_LIABILITIES = "total_liabilities"
    PROPERTY_PLANT_EQUIPMENT = "property_plant_equipment"
    RIGHT_OF_USE_ASSETS = "right_of_use_assets"
    INVESTMENT_PROPERTIES = "investment_properties"
    INTANGIBLE_ASSETS = "intangible_assets"
    INVESTMENT_IN_ASSOCIATES = "investment_in_associates"
    INVENTORIES = "inventories"
    CONTRACT_ASSETS = "contract_assets"
    TRADE_RECEIVABLES = "trade_receivables"
    CASH_AND_BANK_BALANCES = "cash_and_bank_balances"
    SHARE_CAPITAL = "share_capital"
    BANK_BORROWINGS = "bank_borrowings"
    TRADE_PAYABLES = "trade_payables"

    # Cash flow
    OPERATING_CASH_FLOW = "operating_cash_flow"
    INVESTING_CASH_FLOW = "investing_cash_flow"
    FINANCING_CASH_FLOW = "financing_cash_flow"
    NET_CHANGE_IN_CASH = "net_change_in_cash"
    CASH_END_OF_PERIOD = "cash_end_of_period"
    INTEREST_PAID = "interest_paid"
    TAX_PAID = "tax_paid"
    DRAWDOWN_OF_LOANS = "drawdown_of_loans"
    REPAYMENT_OF_LOANS = "repayment_of_loans"


class MetricCandidate(BaseModel):
    """Metric candidate extracted by LLM"""
    id: str
    metric_type: MetricType
    value: float
    unit: Optional[str] = None
    currency: Optional[str] = None
    period: Optional[str] = None

    # Source tracking
    source_table_row_id: str
    source_text: str

    # LLM metadata
    confidence: float  # 0-1
    reasoning: Optional[str] = None
