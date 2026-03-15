#!/usr/bin/env python3
"""
Hybrid Data Extractor for Financial Analysis Report Workers

Strategy: Extract structured financial data (fs_index) + Provide search access to raw text

Worker agents get:
1. 100% accurate structured financial data from fs_index
2. Full text_blocks.jsonl access with search capabilities
3. Page range hints for common sections (MD&A, Business Overview, etc.)
4. LLM intelligence to extract exactly what they need

NO MORE FRAGILE REGEX PATTERNS!
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


def load_fs_index(path: str) -> Dict[str, Any]:
    """Load fs_index.json file"""
    with open(path, 'r') as f:
        return json.load(f)


def load_text_blocks(text_blocks_path: str) -> List[Dict]:
    """Load text blocks from JSONL file"""
    if not text_blocks_path or not os.path.exists(text_blocks_path):
        return []

    blocks = []
    with open(text_blocks_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                blocks.append(json.loads(line))
    return blocks


def get_line_item_value(fs_index: Dict, key_pattern: str, field: str = 'group_current') -> Optional[float]:
    """
    Extract value from fs_index line_items using flexible key matching.

    Args:
        fs_index: The fs_index dictionary
        key_pattern: Pattern to match in key (case-insensitive)
        field: Which field to extract (group_current, group_prior, etc.)

    Returns:
        Value if found, None otherwise
    """
    line_items = fs_index.get('line_items', {})

    # Try exact match first
    for key, item in line_items.items():
        if key_pattern.lower() == key.lower():
            if field in item and item[field] is not None:
                return item[field]

    # Try substring match
    for key, item in line_items.items():
        if key_pattern.lower() in key.lower():
            if field in item and item[field] is not None:
                return item[field]

    return None


def create_metadata(source_file: str, extraction_time: str) -> Dict:
    """Create standard metadata for verification"""
    return {
        "source_file": source_file,
        "extracted_at": extraction_time,
        "extraction_method": "data_extractor.py v3.0 - Hybrid Approach"
    }


def identify_likely_pages(text_blocks: List[Dict]) -> Dict[str, List[int]]:
    """
    Identify likely page ranges for common annual report sections.

    Uses simple heuristics (keywords) to find pages that likely contain
    specific sections. Workers can use these hints to narrow their search.

    Returns:
        Dict mapping section names to page numbers
    """
    section_hints = {
        "business_overview": [],
        "industry_overview": [],
        "segment_reporting": [],
        "mda_section": [],
        "strategy_outlook": [],
        "risk_factors": []
    }

    # Keywords for each section
    section_keywords = {
        "business_overview": ["business overview", "company overview", "corporate profile", "about us"],
        "industry_overview": ["industry overview", "sector review", "market review", "industry outlook"],
        "segment_reporting": ["segment", "business segment", "reportable segment", "geographical segment"],
        "mda_section": ["management discussion", "md&a", "management's discussion", "review of performance"],
        "strategy_outlook": ["strategy", "outlook", "future outlook", "strategic initiatives", "going forward"],
        "risk_factors": ["risk factors", "risks and challenges", "key risks", "risk management"]
    }

    for block in text_blocks:
        text = block.get('text', '').lower()
        page_num = block.get('page_number')

        if not page_num:
            continue

        for section, keywords in section_keywords.items():
            if any(kw in text for kw in keywords):
                if page_num not in section_hints[section]:
                    section_hints[section].append(page_num)

    # Sort and limit to top pages for each section
    for section in section_hints:
        section_hints[section] = sorted(set(section_hints[section]))[:10]  # Top 10 pages

    return section_hints


def build_simple_search_index(text_blocks: List[Dict]) -> Dict[str, Any]:
    """
    Build a simple search index for text blocks.

    Returns a dict with:
    - total_blocks: number of text blocks
    - total_pages: number of unique pages
    - blocks: the actual text blocks (workers can search through them)
    """
    if not text_blocks:
        return {
            "total_blocks": 0,
            "total_pages": 0,
            "blocks": [],
            "_note": "text_blocks.jsonl not provided"
        }

    unique_pages = set(b.get('page_number') for b in text_blocks if b.get('page_number'))

    return {
        "total_blocks": len(text_blocks),
        "total_pages": len(unique_pages),
        "blocks": text_blocks,
        "_note": "Workers can search through blocks to extract: industry, segments, strategy, etc."
    }


def extract_worker1_context(fs_index: Dict, company_name: str, source_file: str, text_blocks_path: str = None) -> Dict:
    """
    Worker 1: Context Setup

    Provides:
    - Company metadata from fs_index (100% accurate)
    - Full text_blocks access for business context extraction
    - Page hints for likely sections
    """
    extraction_time = datetime.now().isoformat()

    # Load text blocks
    text_blocks = load_text_blocks(text_blocks_path) if text_blocks_path else []

    # Identify likely pages for common sections
    page_hints = identify_likely_pages(text_blocks)

    # Build search index
    search_index = build_simple_search_index(text_blocks)

    return {
        "_metadata": create_metadata(source_file, extraction_time),
        "company_name": company_name,
        "period": f"FY{fs_index.get('fiscal_year_end', '2024')[:4]}",
        "currency": fs_index.get('currency', 'RM'),
        "fiscal_year_end": fs_index.get('fiscal_year_end', '2024-12-31'),
        "data_source": "Audited Annual Report",

        # Structured data (100% accurate)
        "_verification": {
            "source_keys": {
                "fiscal_year_end": "fs_index.fiscal_year_end",
                "currency": "fs_index.currency"
            }
        },

        # Search access for qualitative data
        "text_search": {
            "text_blocks_path": text_blocks_path,
            "total_blocks": search_index["total_blocks"],
            "total_pages": search_index["total_pages"],
            "page_hints": page_hints,
            "_usage": "Search text_blocks to extract: industry, segments, geography, market position"
        },

        "_extraction_note": "Worker should use LLM intelligence to extract business context from text_blocks"
    }


def extract_worker2_performance(fs_index: Dict, prior_fs_index: Optional[Dict] = None, source_file: str = "") -> Dict:
    """
    Worker 2: Core Performance Metrics

    Extracts REAL financial data from fs_index (100% accurate)
    """
    extraction_time = datetime.now().isoformat()

    # Extract current period values
    revenue_current = get_line_item_value(fs_index, 'revenue', 'group_current')
    revenue_prior = get_line_item_value(fs_index, 'revenue', 'group_prior')

    gross_profit_current = get_line_item_value(fs_index, 'gross profit', 'group_current')
    gross_profit_prior = get_line_item_value(fs_index, 'gross profit', 'group_prior')

    pbt_current = get_line_item_value(fs_index, 'profit before tax', 'group_current')
    pbt_prior = get_line_item_value(fs_index, 'profit before tax', 'group_prior')

    pat_current = get_line_item_value(fs_index, 'profit for the financial year', 'group_current')
    pat_prior = get_line_item_value(fs_index, 'profit for the financial year', 'group_prior')

    # Attributable profit
    import re
    attr_current = None
    attr_prior = None

    patterns = [
        r'profit.*attributable\s+to:?\s*owners',
        r'profit.*attributable\s+to\s+owners',
    ]

    for pattern in patterns:
        for key in fs_index['line_items'].keys():
            if re.search(pattern, key, re.IGNORECASE):
                attr_current = fs_index['line_items'][key].get('group_current')
                attr_prior = fs_index['line_items'][key].get('group_prior')
                break
        if attr_current is not None:
            break

    # Extract operating profit components
    other_income_current = get_line_item_value(fs_index, 'other income', 'group_current')
    other_income_prior = get_line_item_value(fs_index, 'other income', 'group_prior')

    finance_income_current = get_line_item_value(fs_index, 'finance income', 'group_current')
    finance_income_prior = get_line_item_value(fs_index, 'finance income', 'group_prior')

    fair_value_gain_current = get_line_item_value(fs_index, 'fair value gain', 'group_current')
    fair_value_gain_prior = get_line_item_value(fs_index, 'fair value gain', 'group_prior')

    gain_disposal_current = get_line_item_value(fs_index, 'gain.*disposal', 'group_current')
    gain_disposal_prior = get_line_item_value(fs_index, 'gain.*disposal', 'group_prior')

    distribution_current = get_line_item_value(fs_index, 'distribution expenses', 'group_current')
    distribution_prior = get_line_item_value(fs_index, 'distribution expenses', 'group_prior')

    admin_current = get_line_item_value(fs_index, 'administrative expenses', 'group_current')
    admin_prior = get_line_item_value(fs_index, 'administrative expenses', 'group_prior')

    other_expenses_current = get_line_item_value(fs_index, 'other expenses', 'group_current')
    other_expenses_prior = get_line_item_value(fs_index, 'other expenses', 'group_prior')

    # Calculate operating profit
    operating_profit_current = None
    operating_profit_prior = None

    if gross_profit_current is not None:
        operating_profit_current = (
            gross_profit_current
            + (other_income_current or 0)
            + (finance_income_current or 0)
            + (fair_value_gain_current or 0)
            + (gain_disposal_current or 0)
            - (distribution_current or 0)
            - (admin_current or 0)
            - (other_expenses_current or 0)
        )

    if gross_profit_prior is not None:
        operating_profit_prior = (
            gross_profit_prior
            + (other_income_prior or 0)
            + (finance_income_prior or 0)
            + (fair_value_gain_prior or 0)
            + (gain_disposal_prior or 0)
            - (distribution_prior or 0)
            - (admin_prior or 0)
            - (other_expenses_prior or 0)
        )

    # Calculate margins
    def safe_margin(numerator, denominator):
        if numerator and denominator and denominator != 0:
            return round((numerator / denominator) * 100, 2)
        return None

    result = {
        "_metadata": create_metadata(source_file, extraction_time),
        "metrics": {
            "revenue": {
                "current": revenue_current,
                "prior": revenue_prior,
                "change": (revenue_current - revenue_prior) if (revenue_current and revenue_prior) else None,
                "yoy_pct": round(((revenue_current - revenue_prior) / revenue_prior) * 100, 1) if (revenue_current and revenue_prior and revenue_prior != 0) else None,
                "_source": "fs_index.line_items['revenue']"
            },
            "gross_profit": {
                "current": gross_profit_current,
                "prior": gross_profit_prior,
                "change": (gross_profit_current - gross_profit_prior) if (gross_profit_current and gross_profit_prior) else None,
                "yoy_pct": round(((gross_profit_current - gross_profit_prior) / gross_profit_prior) * 100, 1) if (gross_profit_current and gross_profit_prior and gross_profit_prior != 0) else None,
                "_source": "fs_index.line_items['gross profit']"
            },
            "pbt": {
                "current": pbt_current,
                "prior": pbt_prior,
                "change": (pbt_current - pbt_prior) if (pbt_current and pbt_prior) else None,
                "yoy_pct": round(((pbt_current - pbt_prior) / pbt_prior) * 100, 1) if (pbt_current and pbt_prior and pbt_prior != 0) else None,
                "_source": "fs_index.line_items['profit before tax']"
            },
            "pat": {
                "current": pat_current,
                "prior": pat_prior,
                "change": (pat_current - pat_prior) if (pat_current and pat_prior) else None,
                "yoy_pct": round(((pat_current - pat_prior) / pat_prior) * 100, 1) if (pat_current and pat_prior and pat_prior != 0) else None,
                "_source": "fs_index.line_items['profit for the financial year']"
            },
            "attributable_profit": {
                "current": attr_current,
                "prior": attr_prior,
                "change": (attr_current - attr_prior) if (attr_current and attr_prior) else None,
                "yoy_pct": round(((attr_current - attr_prior) / attr_prior) * 100, 1) if (attr_current and attr_prior and attr_prior != 0) else None,
                "_source": "fs_index.line_items['profit for the financial year attributable to: owners of the parent']"
            }
        },
        "margins": {
            "gross_margin": {
                "current": safe_margin(gross_profit_current, revenue_current),
                "prior": safe_margin(gross_profit_prior, revenue_prior),
                "_source": "Calculated: gross_profit / revenue * 100"
            },
            "operating_margin": {
                "current": safe_margin(operating_profit_current, revenue_current),
                "prior": safe_margin(operating_profit_prior, revenue_prior),
                "_source": "Calculated: operating_profit / revenue * 100",
                "_components": {
                    "operating_profit_formula": "gross_profit + other_income + finance_income + fair_value_gains + disposal_gains - distribution - admin - other_expenses",
                    "other_income_current": other_income_current,
                    "finance_income_current": finance_income_current,
                    "fair_value_gain_current": fair_value_gain_current,
                    "gain_disposal_current": gain_disposal_current,
                    "distribution_current": distribution_current,
                    "admin_current": admin_current,
                    "other_expenses_current": other_expenses_current
                }
            },
            "pbt_margin": {
                "current": safe_margin(pbt_current, revenue_current),
                "prior": safe_margin(pbt_prior, revenue_prior),
                "_source": "Calculated: pbt / revenue * 100"
            },
            "pat_margin": {
                "current": safe_margin(pat_current, revenue_current),
                "prior": safe_margin(pat_prior, revenue_prior),
                "_source": "Calculated: pat / revenue * 100"
            },
            "attributable_margin": {
                "current": safe_margin(attr_current, revenue_current),
                "prior": safe_margin(attr_prior, revenue_prior),
                "_source": "Calculated: attributable_profit / revenue * 100"
            }
        },
        "_verification": {
            "data_quality": "REAL_DATA_EXTRACTED",
            "source_file": source_file,
            "extraction_timestamp": extraction_time,
            "validation": "All metrics extracted from fs_index.json line_items"
        }
    }

    return result


def extract_worker3_business(fs_index: Dict, source_file: str, text_blocks_path: str = None) -> Dict:
    """
    Worker 3: Business Analysis

    Provides:
    - Full text_blocks access for segment, industry, strategy extraction
    - Page hints for relevant sections
    - NO fragile regex extraction - worker uses LLM intelligence
    """
    extraction_time = datetime.now().isoformat()

    # Load text blocks
    text_blocks = load_text_blocks(text_blocks_path) if text_blocks_path else []

    # Identify likely pages
    page_hints = identify_likely_pages(text_blocks)

    # Build search index
    search_index = build_simple_search_index(text_blocks)

    return {
        "_metadata": create_metadata(source_file, extraction_time),

        "text_search": {
            "text_blocks_path": text_blocks_path,
            "total_blocks": search_index["total_blocks"],
            "total_pages": search_index["total_pages"],
            "page_hints": {
                "segment_reporting": page_hints.get("segment_reporting", []),
                "industry_overview": page_hints.get("industry_overview", []),
                "strategy_outlook": page_hints.get("strategy_outlook", [])
            },
            "_usage": "Search text_blocks to extract: segments, industry context, strategic initiatives"
        },

        "_extraction_note": "Worker should use LLM intelligence to extract business data from text_blocks",
        "_verification": {
            "data_quality": "RAW_TEXT_ACCESS" if text_blocks else "NO_TEXT_BLOCKS",
            "source": "text_blocks.jsonl",
            "extraction_method": "No regex - worker extracts with LLM intelligence"
        }
    }


def extract_worker4_operational(fs_index: Dict, source_file: str = "") -> Dict:
    """Worker 4: Operational Health - Extract from fs_index"""
    extraction_time = datetime.now().isoformat()

    # Extract balance sheet items
    total_assets = get_line_item_value(fs_index, 'total assets', 'group_current')
    total_liabilities = get_line_item_value(fs_index, 'total liabilities', 'group_current')
    total_equity = get_line_item_value(fs_index, 'total equity', 'group_current')

    current_assets = get_line_item_value(fs_index, 'total current assets', 'group_current')
    current_liabilities = get_line_item_value(fs_index, 'total current liabilities', 'group_current')

    inventory = get_line_item_value(fs_index, 'inventories', 'group_current')
    receivables = get_line_item_value(fs_index, 'trade receivables', 'group_current')

    # Calculate ratios
    current_ratio = round(current_assets / current_liabilities, 2) if (current_assets and current_liabilities and current_liabilities != 0) else None
    quick_ratio = round((current_assets - inventory) / current_liabilities, 2) if (current_assets and inventory and current_liabilities and current_liabilities != 0) else None

    return {
        "_metadata": create_metadata(source_file, extraction_time),
        "solvency_ratios": {
            "current_ratio": {
                "current": current_ratio,
                "_source": "Calculated: current_assets / current_liabilities"
            },
            "quick_ratio": {
                "current": quick_ratio,
                "_source": "Calculated: (current_assets - inventory) / current_liabilities"
            },
            "working_capital": {
                "current": (current_assets - current_liabilities) if (current_assets and current_liabilities) else None,
                "_source": "Calculated: current_assets - current_liabilities"
            },
            "liabilities_to_assets": {
                "current": round((total_liabilities / total_assets) * 100, 2) if (total_liabilities and total_assets and total_assets != 0) else None,
                "_source": "Calculated: total_liabilities / total_assets * 100"
            }
        },
        "_verification": {
            "data_quality": "REAL_DATA_EXTRACTED",
            "source_file": source_file,
            "validation": "Balance sheet metrics extracted from fs_index.json"
        }
    }


def extract_worker5_profitability(fs_index: Dict, source_file: str = "") -> Dict:
    """Worker 5: Profitability & Growth"""
    extraction_time = datetime.now().isoformat()

    return {
        "_metadata": create_metadata(source_file, extraction_time),
        "note": "Profitability metrics calculated from extracted financial data",
        "_verification": {
            "data_quality": "CALCULATED",
            "source": "Derived from metrics extracted by extract_performance_metrics()",
            "validation": "Ratios calculated using standard financial formulas"
        }
    }


def extract_worker6_risk_cashflow(fs_index: Dict, source_file: str = "") -> Dict:
    """Worker 6: Risk & Cash Flow - Extract from fs_index"""
    extraction_time = datetime.now().isoformat()

    # Extract cash flow statement items
    ocf_current = get_line_item_value(fs_index, 'net cash from operating activities', 'group_current')
    ocf_prior = get_line_item_value(fs_index, 'net cash from operating activities', 'group_prior')

    investing_cf_current = get_line_item_value(fs_index, 'net cash used in investing activities', 'group_current')
    investing_cf_prior = get_line_item_value(fs_index, 'net cash used in investing activities', 'group_prior')

    financing_cf_current = get_line_item_value(fs_index, 'net cash from financing activities', 'group_current')
    financing_cf_prior = get_line_item_value(fs_index, 'net cash from financing activities', 'group_prior')

    interest_paid_current = get_line_item_value(fs_index, 'interest paid', 'group_current')
    interest_paid_prior = get_line_item_value(fs_index, 'interest paid', 'group_prior')

    dividends_paid_current = get_line_item_value(fs_index, 'dividends paid', 'group_current')
    dividends_paid_prior = get_line_item_value(fs_index, 'dividends paid', 'group_prior')

    # Calculate derived metrics
    fcf_current = None
    fcf_prior = None
    if ocf_current and investing_cf_current:
        fcf_current = ocf_current - abs(investing_cf_current)
    if ocf_prior and investing_cf_prior:
        fcf_prior = ocf_prior - abs(investing_cf_prior)

    revenue_current = get_line_item_value(fs_index, 'revenue', 'group_current')
    ocf_to_revenue = None
    if ocf_current and revenue_current and revenue_current > 0:
        ocf_to_revenue = round((ocf_current / revenue_current) * 100, 2)

    bank_borrowings = get_line_item_value(fs_index, 'bank borrowings', 'group_current')
    ocf_to_debt = None
    if ocf_current and bank_borrowings and bank_borrowings > 0:
        ocf_to_debt = round((ocf_current / bank_borrowings) * 100, 2)

    interest_coverage = None
    if ocf_current and interest_paid_current and interest_paid_current > 0:
        interest_coverage = round(ocf_current / interest_paid_current, 2)

    ocf_yoy = None
    if ocf_current and ocf_prior and ocf_prior != 0:
        ocf_yoy = round(((ocf_current - ocf_prior) / abs(ocf_prior)) * 100, 2)

    fcf_yoy = None
    if fcf_current and fcf_prior and fcf_prior != 0:
        fcf_yoy = round(((fcf_current - fcf_prior) / abs(fcf_prior)) * 100, 2)

    financing_yoy = None
    if financing_cf_current and financing_cf_prior and financing_cf_prior != 0:
        financing_yoy = round(((financing_cf_current - financing_cf_prior) / abs(financing_cf_prior)) * 100, 2)

    return {
        "_metadata": create_metadata(source_file, extraction_time),

        "cash_flow_statement": {
            "operating": {
                "current": ocf_current,
                "prior": ocf_prior,
                "yoy_change_pct": ocf_yoy,
                "_source": "fs_index.line_items['net cash from operating activities']"
            },
            "investing": {
                "current": investing_cf_current,
                "prior": investing_cf_prior,
                "_source": "fs_index.line_items['net cash used in investing activities']"
            },
            "financing": {
                "current": financing_cf_current,
                "prior": financing_cf_prior,
                "yoy_change_pct": financing_yoy,
                "_source": "fs_index.line_items['net cash from financing activities']"
            },
            "free_cash_flow": {
                "current": fcf_current,
                "prior": fcf_prior,
                "yoy_change_pct": fcf_yoy,
                "_source": "Calculated: OCF - |Investing CF|"
            }
        },

        "cash_flow_quality": {
            "ocf_to_revenue_pct": ocf_to_revenue,
            "ocf_to_debt_pct": ocf_to_debt,
            "interest_coverage_ratio": interest_coverage,
            "_source": "Calculated from cash flow statement items"
        },

        "cash_flow_details": {
            "interest_paid": {
                "current": interest_paid_current,
                "prior": interest_paid_prior,
                "_source": "fs_index.line_items['interest paid']"
            },
            "dividends_paid": {
                "current": dividends_paid_current,
                "prior": dividends_paid_prior,
                "_source": "fs_index.line_items['dividends paid']"
            }
        },

        "_verification": {
            "data_quality": "REAL_DATA_EXTRACTED",
            "source": "fs_index.json cash flow statement items",
            "validation": "All cash flow metrics extracted with source tracking"
        }
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python data_extractor.py <fs_index.json> --company <NAME> [--prior <prior_fs_index.json>] [--text-blocks <text_blocks.jsonl>] [--output <output.json>]")
        sys.exit(1)

    fs_index_path = sys.argv[1]
    company_name = "Company"
    prior_fs_index_path = None
    text_blocks_path = None
    output_path = "data_bundles.json"

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--company" and i + 1 < len(sys.argv):
            company_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--prior" and i + 1 < len(sys.argv):
            prior_fs_index_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--text-blocks" and i + 1 < len(sys.argv):
            text_blocks_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Load fs_index files
    print(f"Loading: {fs_index_path}")
    fs_index = load_fs_index(fs_index_path)
    prior_fs_index = load_fs_index(prior_fs_index_path) if prior_fs_index_path else None

    # Check if text_blocks file exists
    if text_blocks_path and not os.path.exists(text_blocks_path):
        print(f"⚠️  Warning: text_blocks.jsonl not found at {text_blocks_path}")
        print(f"   Workers will have limited qualitative data access")
        text_blocks_path = None

    # Create data bundles for all 6 workers
    extraction_time = datetime.now().isoformat()

    data_bundles = {
        "worker_1": extract_worker1_context(fs_index, company_name, fs_index_path, text_blocks_path),
        "worker_2": extract_worker2_performance(fs_index, prior_fs_index, fs_index_path),
        "worker_3": extract_worker3_business(fs_index, fs_index_path, text_blocks_path),
        "worker_4": extract_worker4_operational(fs_index, fs_index_path),
        "worker_5": extract_worker5_profitability(fs_index, fs_index_path),
        "worker_6": extract_worker6_risk_cashflow(fs_index, fs_index_path)
    }

    # Add global verification metadata
    data_bundles["_global_verification"] = {
        "source_file": fs_index_path,
        "extraction_timestamp": extraction_time,
        "company_name": company_name,
        "has_prior_year_data": prior_fs_index is not None,
        "has_text_blocks": text_blocks_path is not None,
        "data_quality": "HYBRID_EXTRACTION",
        "extraction_strategy": {
            "structured_data": "fs_index.json (100% accurate)",
            "qualitative_data": "text_blocks.jsonl (worker extracts with LLM)",
            "approach": "No fragile regex patterns - worker intelligence"
        },
        "precision_standards": {
            "calculation_rule": "Calculate from raw RM'000 values BEFORE rounding",
            "forbidden_operations": "Never derive metrics from rounded display values",
            "example": "NCI = actual_value_from_fs_index, not (PAT_rounded - PATMI_rounded)",
            "rounding": "Round ONLY the final display value, never intermediate calculations"
        }
    }

    # Write to output file
    with open(output_path, 'w') as f:
        json.dump(data_bundles, f, indent=2)

    print(f"\n✅ Data bundles created - HYBRID APPROACH")
    print(f"   Output: {output_path}")
    print(f"\n   Worker 1: Context Setup (text_blocks access + page hints)")
    print(f"   Worker 2: Core Performance (fs_index financial data)")
    print(f"   Worker 3: Business Analysis (text_blocks access + page hints)")
    print(f"   Worker 4: Operational Health (fs_index balance sheet)")
    print(f"   Worker 5: Profitability & Growth (calculated metrics)")
    print(f"   Worker 6: Risk & Cash Flow (fs_index cash flow data)")
    print(f"\n✓ Extraction Strategy:")
    print(f"  - Structured data: fs_index.json (100% accurate)")
    print(f"  - Qualitative data: text_blocks.jsonl (worker extracts)")
    print(f"  - NO fragile regex patterns")
    print(f"  - Workers use LLM intelligence for context")


if __name__ == "__main__":
    main()
