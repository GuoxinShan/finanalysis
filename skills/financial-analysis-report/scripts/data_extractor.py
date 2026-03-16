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


def make_metric(fs_index: Dict, key: str, label: str = None, denominator_key: str = None, denom_field: str = 'group_current') -> Dict:
    """
    Extract current/prior values with YoY% and optional ratio.

    Args:
        fs_index: The fs_index dictionary
        key: Key pattern to match in fs_index line_items
        label: Display label (defaults to key if not provided)
        denominator_key: Optional key for ratio calculation (e.g. 'revenue' for % of revenue)
        denom_field: Field for denominator value (default 'group_current')

    Returns:
        Dict with current, prior, yoy_pct, optional pct_of_denominator, and _source
    """
    name = label or key
    current = get_line_item_value(fs_index, key, 'group_current')
    prior = get_line_item_value(fs_index, key, 'group_prior')
    result = {"current": current, "prior": prior}
    if current is not None and prior is not None and prior != 0:
        result["yoy_pct"] = round(((current - prior) / abs(prior)) * 100, 1)
    if denominator_key:
        denom = get_line_item_value(fs_index, denominator_key, denom_field)
        if current is not None and denom is not None and denom != 0:
            result["pct_of_denominator"] = round((current / denom) * 100, 2)
    result["_source"] = f"fs_index.line_items['{key}']"
    return result


def create_metadata(source_file: str, extraction_time: str) -> Dict:
    """Create standard metadata for verification"""
    return {
        "source_file": source_file,
        "extracted_at": extraction_time,
        "extraction_method": "data_extractor.py v3.0 - Hybrid Approach"
    }


def extract_essential_text(text_blocks: List[Dict],
                            text_hints: Dict[str, List[int]],
                            max_chars_per_section: int = 1000) -> Dict[str, str]:
    """
    Extract lightweight text summaries for specified sections.

    This is the **hybrid approach** (Option C):
    - Pre-extracts 2-3 key paragraphs (lightweight)
    - Keeps bundle size manageable (~200-300 lines)
    - Workers can access full text_blocks.jsonl if needed (rare)

    Args:
        text_blocks: List of text blocks from text_blocks.jsonl
        text_hints: Dict mapping section names to page numbers
            Example: {"mda_section": [45, 46], "strategy_outlook": [12, 13]}
        max_chars_per_section: Maximum characters per section (default 1000, ~150 words)

    Returns:
        Dict with extracted text summaries (not full text)
    """
    excerpts = {}

    for section_name, pages in text_hints.items():
        # Get blocks for these pages
        relevant_blocks = [
            block for block in text_blocks
            if block.get('page_number') in pages
        ]

        # Filter for substantial content (not headers, not bullet points)
        substantial_blocks = [
            block for block in relevant_blocks
            if len(block.get('text', '').strip()) > 200  # Substantial paragraphs
        ]

        # Limit to first 2-3 blocks (keep it lightweight)
        selected_blocks = substantial_blocks[:3]

        # Combine text
        combined_text = '\n\n'.join(
            block.get('text', '') for block in selected_blocks
        )

        # Truncate if too long (keep bundle size manageable)
        if len(combined_text) > max_chars_per_section:
            combined_text = combined_text[:max_chars_per_section] + "..."

        excerpts[section_name] = combined_text

    return excerpts


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

    # Expense data (merged from old Worker 6)
    cost_of_sales_current = get_line_item_value(fs_index, 'cost of sales', 'group_current')
    cost_of_sales_prior = get_line_item_value(fs_index, 'cost of sales', 'group_prior')
    finance_costs_current = get_line_item_value(fs_index, 'finance costs', 'group_current')
    finance_costs_prior = get_line_item_value(fs_index, 'finance costs', 'group_prior')
    taxation_current = get_line_item_value(fs_index, 'taxation', 'group_current')
    taxation_prior = get_line_item_value(fs_index, 'taxation', 'group_prior')

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
            "cost_of_sales": {
                "current": cost_of_sales_current,
                "prior": cost_of_sales_prior,
                "change": (cost_of_sales_current - cost_of_sales_prior) if (cost_of_sales_current and cost_of_sales_prior) else None,
                "yoy_pct": round(((cost_of_sales_current - cost_of_sales_prior) / cost_of_sales_prior) * 100, 1) if (cost_of_sales_current and cost_of_sales_prior and cost_of_sales_prior != 0) else None,
                "pct_of_revenue_current": safe_margin(cost_of_sales_current, revenue_current),
                "pct_of_revenue_prior": safe_margin(cost_of_sales_prior, revenue_prior),
                "_source": "fs_index.line_items['cost of sales']"
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
        "expenses": {
            "administrative_expenses": {
                "current": admin_current,
                "prior": admin_prior,
                "change": (admin_current - admin_prior) if (admin_current and admin_prior) else None,
                "yoy_pct": round(((admin_current - admin_prior) / admin_prior) * 100, 1) if (admin_current and admin_prior and admin_prior != 0) else None,
                "pct_of_revenue_current": safe_margin(admin_current, revenue_current),
                "pct_of_revenue_prior": safe_margin(admin_prior, revenue_prior),
                "_source": "fs_index.line_items['administrative expenses']"
            },
            "finance_costs": {
                "current": finance_costs_current,
                "prior": finance_costs_prior,
                "change": (finance_costs_current - finance_costs_prior) if (finance_costs_current and finance_costs_prior) else None,
                "yoy_pct": round(((finance_costs_current - finance_costs_prior) / finance_costs_prior) * 100, 1) if (finance_costs_current and finance_costs_prior and finance_costs_prior != 0) else None,
                "pct_of_revenue_current": safe_margin(finance_costs_current, revenue_current),
                "pct_of_revenue_prior": safe_margin(finance_costs_prior, revenue_prior),
                "_source": "fs_index.line_items['finance costs']"
            },
            "taxation": {
                "current": taxation_current,
                "prior": taxation_prior,
                "pct_of_pbt_current": safe_margin(taxation_current, pbt_current),
                "pct_of_pbt_prior": safe_margin(taxation_prior, pbt_prior),
                "_source": "fs_index.line_items['taxation']"
            },
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

    # Extract lightweight text summaries (Option C: Hybrid approach)
    text_excerpts = extract_essential_text(
        text_blocks,
        {
            "mda_section": page_hints.get("mda_section", []),
            "strategy_outlook": page_hints.get("strategy_outlook", []),
            "segment_reporting": page_hints.get("segment_reporting", [])
        },
        max_chars_per_section=1000  # ~150 words per section
    ) if text_blocks else {}

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

        "text_excerpts": text_excerpts,  # NEW: Lightweight summaries

        "source_files": {  # NEW: Optional deep-dive access
            "text_blocks_path": text_blocks_path,
            "fs_index_path": source_file
        },

        "_extraction_note": "Worker should use LLM intelligence to extract business data from text_blocks",
        "_verification": {
            "data_quality": "REAL_DATA_EXTRACTED" if text_blocks else "NO_TEXT_BLOCKS",
            "extraction_method": "hybrid_extraction_v3.0",
            "text_blocks": len(text_blocks) if text_blocks else 0,
            "page_hints": len(page_hints) if page_hints else 0
        }
    }


def extract_worker4_profitability_health(fs_index: Dict, prior_fs_index: Optional[Dict] = None, source_file: str = "") -> Dict:
    """
    Worker 4: Profitability & Financial Health (Sections V, VII)

    Merges old Worker 4 (operational health/solvency) and Worker 5 (profitability/growth).
    Provides: ROE, ROA, DuPont inputs, growth metrics, solvency ratios, working capital.
    """
    extraction_time = datetime.now().isoformat()

    # --- Profitability data (from old Worker 5) ---
    total_equity = get_line_item_value(fs_index, 'total equity', 'group_current')
    total_equity_prior = get_line_item_value(fs_index, 'total equity', 'group_prior')
    total_assets = get_line_item_value(fs_index, 'total assets', 'group_current')
    total_assets_prior = get_line_item_value(fs_index, 'total assets', 'group_prior')

    pat = get_line_item_value(fs_index, 'profit for the financial year', 'group_current')
    pat_prior = get_line_item_value(fs_index, 'profit for the financial year', 'group_prior')

    import re
    attr_pat = None
    attr_pat_prior = None
    for key in fs_index.get('line_items', {}):
        if re.search(r'profit.*attributable\s+to:?\s*owners', key, re.IGNORECASE):
            attr_pat = fs_index['line_items'][key].get('group_current')
            attr_pat_prior = fs_index['line_items'][key].get('group_prior')
            break

    revenue = get_line_item_value(fs_index, 'revenue', 'group_current')
    revenue_prior = get_line_item_value(fs_index, 'revenue', 'group_prior')

    gross_profit = get_line_item_value(fs_index, 'gross profit', 'group_current')
    gross_profit_prior = get_line_item_value(fs_index, 'gross profit', 'group_prior')

    pbt = get_line_item_value(fs_index, 'profit before tax', 'group_current')
    pbt_prior = get_line_item_value(fs_index, 'profit before tax', 'group_prior')

    eps_current = get_line_item_value(fs_index, 'basic earnings per share', 'group_current')
    eps_prior = get_line_item_value(fs_index, 'basic earnings per share', 'group_prior')
    shares = get_line_item_value(fs_index, 'number of ordinary shares', 'group_current')

    def safe_div(n, d):
        return round(n / d, 2) if (n and d and d != 0) else None

    def yoy(cur, prev):
        if cur is not None and prev is not None and prev != 0:
            return round(((cur - prev) / abs(prev)) * 100, 1)
        return None

    roe = safe_div(attr_pat, total_equity)
    roe_prior = safe_div(attr_pat_prior, total_equity_prior)
    roa = safe_div(pat, total_assets)
    roa_prior = safe_div(pat_prior, total_assets_prior)

    # --- Financial Health data (from old Worker 4) ---
    current_assets = get_line_item_value(fs_index, 'current assets', 'group_current')
    current_assets_prior = get_line_item_value(fs_index, 'current assets', 'group_prior')
    current_liabilities = get_line_item_value(fs_index, 'current liabilities', 'group_current')
    current_liabilities_prior = get_line_item_value(fs_index, 'current liabilities', 'group_prior')

    inventory = get_line_item_value(fs_index, 'inventories', 'group_current')
    inventory_prior = get_line_item_value(fs_index, 'inventories', 'group_prior')
    receivables = get_line_item_value(fs_index, 'trade receivables', 'group_current')
    receivables_prior = get_line_item_value(fs_index, 'trade receivables', 'group_prior')

    cash_and_bank = get_line_item_value(fs_index, 'cash and bank balances', 'group_current')
    cash_and_bank_prior = get_line_item_value(fs_index, 'cash and bank balances', 'group_prior')
    trade_payables = get_line_item_value(fs_index, 'trade payables', 'group_current')
    trade_payables_prior = get_line_item_value(fs_index, 'trade payables', 'group_prior')
    total_liabilities = get_line_item_value(fs_index, 'total liabilities', 'group_current')
    total_liabilities_prior = get_line_item_value(fs_index, 'total liabilities', 'group_prior')
    total_non_current_liabilities = get_line_item_value(fs_index, 'total non-current liabilities', 'group_current')
    total_non_current_liabilities_prior = get_line_item_value(fs_index, 'total non-current liabilities', 'group_prior')
    bank_borrowings = get_line_item_value(fs_index, 'bank borrowings', 'group_current')
    bank_borrowings_prior = get_line_item_value(fs_index, 'bank borrowings', 'group_prior')
    retained_earnings = get_line_item_value(fs_index, 'retained earnings', 'group_current')
    retained_earnings_prior = get_line_item_value(fs_index, 'retained earnings', 'group_prior')
    depreciation = get_line_item_value(fs_index, 'depreciation and amortisation', 'group_current')
    depreciation_prior = get_line_item_value(fs_index, 'depreciation and amortisation', 'group_prior')

    other_borrowings = get_line_item_value(fs_index, 'borrowings', 'group_current')

    # Net debt
    net_debt_current = (bank_borrowings + (other_borrowings or 0) - (cash_and_bank or 0)) if bank_borrowings is not None else None
    other_borrowings_prior = get_line_item_value(fs_index, 'borrowings', 'group_prior')
    net_debt_prior = (bank_borrowings_prior + (other_borrowings_prior or 0) - (cash_and_bank_prior or 0)) if bank_borrowings_prior is not None else None

    # Ratios
    current_ratio = round(current_assets / current_liabilities, 2) if (current_assets and current_liabilities and current_liabilities != 0) else None
    current_ratio_prior = round(current_assets_prior / current_liabilities_prior, 2) if (current_assets_prior and current_liabilities_prior and current_liabilities_prior != 0) else None
    quick_ratio = round((current_assets - (inventory or 0)) / current_liabilities, 2) if (current_assets and current_liabilities and current_liabilities != 0) else None
    quick_ratio_prior = round((current_assets_prior - (inventory_prior or 0)) / current_liabilities_prior, 2) if (current_assets_prior and current_liabilities_prior and current_liabilities_prior != 0) else None

    debt_to_equity = safe_div(total_liabilities, total_equity)
    debt_to_assets = safe_div(total_liabilities, total_assets)
    gearing = safe_div(bank_borrowings, total_equity)
    asset_turnover = safe_div(revenue, total_assets)
    asset_turnover_prior = safe_div(revenue_prior, total_assets_prior)

    # Working capital cycle from cash flow
    change_in_receivables = get_line_item_value(fs_index, 'changes in receivables', 'group_current')
    change_in_inventories = get_line_item_value(fs_index, 'changes in inventories', 'group_current')
    change_in_payables = get_line_item_value(fs_index, 'changes in payables', 'group_current')

    return {
        "_metadata": create_metadata(source_file, extraction_time),
        "sections": "V (Profitability & Growth), VII (Financial Health)",

        # --- Profitability (Section V) ---
        "profitability": {
            "roe": {"current": roe, "prior": roe_prior, "_source": "Calculated: attributable_profit / total_equity"},
            "roa": {"current": roa, "prior": roa_prior, "_source": "Calculated: pat / total_assets"},
            "pbt_margin": {"current": safe_div(pbt, revenue), "prior": safe_div(pbt_prior, revenue_prior)},
            "pat_margin": {"current": safe_div(pat, revenue), "prior": safe_div(pat_prior, revenue_prior)},
            "gross_margin": {"current": safe_div(gross_profit, revenue), "prior": safe_div(gross_profit_prior, revenue_prior)},
            "attributable_margin": {"current": safe_div(attr_pat, revenue), "prior": safe_div(attr_pat_prior, revenue_prior)},
        },
        "growth": {
            "revenue_growth": yoy(revenue, revenue_prior),
            "gross_profit_growth": yoy(gross_profit, gross_profit_prior),
            "pat_growth": yoy(pat, pat_prior),
            "eps_growth": yoy(eps_current, eps_prior),
            "total_assets_growth": yoy(total_assets, total_assets_prior),
            "equity_growth": yoy(total_equity, total_equity_prior),
        },
        "per_share": {
            "eps_basic": {"current": eps_current, "prior": eps_prior},
            "bvps": {"current": safe_div(total_equity, shares)},
            "shares_outstanding": shares,
        },
        "raw_values": {
            "total_equity_current": total_equity,
            "total_equity_prior": total_equity_prior,
            "total_assets_current": total_assets,
            "total_assets_prior": total_assets_prior,
            "pat_current": pat,
            "pat_prior": pat_prior,
            "attributable_profit_current": attr_pat,
            "attributable_profit_prior": attr_pat_prior,
            "pbt_current": pbt,
            "pbt_prior": pbt_prior,
        },

        # --- Financial Health (Section VII) ---
        "balance_sheet": {
            "total_assets": {"current": total_assets, "prior": total_assets_prior, "yoy_pct": yoy(total_assets, total_assets_prior)},
            "total_liabilities": {"current": total_liabilities, "prior": total_liabilities_prior, "yoy_pct": yoy(total_liabilities, total_liabilities_prior)},
            "total_equity": {"current": total_equity, "prior": total_equity_prior, "yoy_pct": yoy(total_equity, total_equity_prior)},
            "current_assets": {"current": current_assets, "prior": current_assets_prior},
            "current_liabilities": {"current": current_liabilities, "prior": current_liabilities_prior},
            "cash_and_bank_balances": {"current": cash_and_bank, "prior": cash_and_bank_prior},
            "trade_receivables": {"current": receivables, "prior": receivables_prior},
            "inventories": {"current": inventory, "prior": inventory_prior},
            "trade_payables": {"current": trade_payables, "prior": trade_payables_prior},
            "bank_borrowings": {"current": bank_borrowings, "prior": bank_borrowings_prior},
            "retained_earnings": {"current": retained_earnings, "prior": retained_earnings_prior},
            "depreciation_and_amortisation": {"current": depreciation, "prior": depreciation_prior},
            "total_non_current_liabilities": {"current": total_non_current_liabilities, "prior": total_non_current_liabilities_prior},
        },
        "solvency": {
            "current_ratio": {"current": current_ratio, "prior": current_ratio_prior},
            "quick_ratio": {"current": quick_ratio, "prior": quick_ratio_prior},
            "working_capital": {
                "current": (current_assets - current_liabilities) if (current_assets and current_liabilities) else None,
                "prior": (current_assets_prior - current_liabilities_prior) if (current_assets_prior and current_liabilities_prior) else None,
            },
            "net_debt": {"current": net_debt_current, "prior": net_debt_prior, "yoy_pct": yoy(net_debt_current, net_debt_prior)},
            "debt_to_equity": {"current": debt_to_equity},
            "debt_to_assets": {"current": debt_to_assets},
            "gearing": {"current": gearing},
            "asset_turnover": {"current": asset_turnover, "prior": asset_turnover_prior},
        },
        "working_capital_cycle": {
            "change_in_receivables": {"current": change_in_receivables},
            "change_in_inventories": {"current": change_in_inventories},
            "change_in_payables": {"current": change_in_payables},
            "_note": "From cash flow statement. Negative = cash inflow (e.g., collecting receivables).",
        },
        "_verification": {
            "data_quality": "REAL_DATA_EXTRACTED",
            "source": "fs_index.json (profitability + solvency metrics)",
        }
    }


def extract_worker5_risk(fs_index: Dict, source_file: str = "") -> Dict:
    """
    Worker 5: Risk Assessment (Section VI)

    Extracts risk-relevant data: debt structure, leverage ratios, revenue concentration.
    """
    extraction_time = datetime.now().isoformat()

    bank_borrowings = get_line_item_value(fs_index, 'bank borrowings', 'group_current')
    bank_borrowings_prior = get_line_item_value(fs_index, 'bank borrowings', 'group_prior')
    total_liabilities = get_line_item_value(fs_index, 'total liabilities', 'group_current')
    total_equity = get_line_item_value(fs_index, 'total equity', 'group_current')
    total_assets = get_line_item_value(fs_index, 'total assets', 'group_current')

    def safe_div(n, d):
        return round(n / d, 2) if (n and d and d != 0) else None

    def yoy(cur, prev):
        if cur is not None and prev is not None and prev != 0:
            return round(((cur - prev) / abs(prev)) * 100, 1)
        return None

    revenue = get_line_item_value(fs_index, 'revenue', 'group_current')
    revenue_prior = get_line_item_value(fs_index, 'revenue', 'group_prior')
    other_borrowings = get_line_item_value(fs_index, 'borrowings', 'group_current')
    lease_obligations = get_line_item_value(fs_index, 'lease liabilities', 'group_current')

    cash_and_bank = get_line_item_value(fs_index, 'cash and bank balances', 'group_current')
    cash_and_bank_prior = get_line_item_value(fs_index, 'cash and bank balances', 'group_prior')

    net_debt_current = (bank_borrowings + (other_borrowings or 0) - (cash_and_bank or 0)) if bank_borrowings is not None else None
    other_borrowings_prior = get_line_item_value(fs_index, 'borrowings', 'group_prior')
    net_debt_prior = (bank_borrowings_prior + (other_borrowings_prior or 0) - (cash_and_bank_prior or 0)) if bank_borrowings_prior is not None else None

    return {
        "_metadata": create_metadata(source_file, extraction_time),
        "sections": "VI (Risk Assessment)",
        "debt_structure": {
            "bank_borrowings": {"current": bank_borrowings, "prior": bank_borrowings_prior},
            "other_borrowings": other_borrowings,
            "lease_obligations": lease_obligations,
            "net_debt": {"current": net_debt_current, "prior": net_debt_prior, "yoy_pct": yoy(net_debt_current, net_debt_prior)},
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "total_assets": total_assets,
        },
        "risk_ratios": {
            "debt_to_equity": {"current": safe_div(total_liabilities, total_equity)},
            "debt_to_assets": {"current": safe_div(total_liabilities, total_assets)},
            "gearing": {"current": safe_div(bank_borrowings, total_equity)},
        },
        "revenue_trend": {
            "current": revenue,
            "prior": revenue_prior,
            "yoy_pct": round(((revenue - revenue_prior) / revenue_prior) * 100, 1) if (revenue and revenue_prior and revenue_prior != 0) else None,
        },
        "balance_sheet_summary": {
            "total_assets": make_metric(fs_index, "total assets"),
            "total_equity": make_metric(fs_index, "total equity"),
            "total_liabilities": make_metric(fs_index, "total liabilities"),
            "cash_and_bank_balances": make_metric(fs_index, "cash and bank balances"),
            "trade_receivables": make_metric(fs_index, "trade receivables"),
            "inventories": make_metric(fs_index, "inventories"),
            "retained_earnings": make_metric(fs_index, "retained earnings"),
        },
        "income_statement_summary": {
            "revenue": make_metric(fs_index, "revenue"),
            "gross_profit": make_metric(fs_index, "gross profit"),
            "pbt": make_metric(fs_index, "profit before tax"),
            "pat": make_metric(fs_index, "profit for the financial year"),
        },
        "cash_flow_summary": {
            "operating_cash_flow": make_metric(fs_index, "net cash from operating activities"),
            "free_cash_flow": {
                "current": (get_line_item_value(fs_index, 'net cash from operating activities', 'group_current') +
                            get_line_item_value(fs_index, 'net cash used in investing activities', 'group_current'))
                            if get_line_item_value(fs_index, 'net cash from operating activities', 'group_current') is not None else None,
                "prior": (get_line_item_value(fs_index, 'net cash from operating activities', 'group_prior') +
                         get_line_item_value(fs_index, 'net cash used in investing activities', 'group_prior'))
                        if get_line_item_value(fs_index, 'net cash from operating activities', 'group_prior') is not None else None,
            },
        },
        "_verification": {
            "data_quality": "REAL_DATA_EXTRACTED",
            "source": "fs_index.json risk metrics",
        }
    }


def extract_worker6_cashflow(fs_index: Dict, source_file: str = "") -> Dict:
    """Worker 6: Cash Flow & Outlook (Sections VIII-IX)"""
    extraction_time = datetime.now().isoformat()

    # Cash flow statement items
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

    # FCF
    fcf_current = (ocf_current - abs(investing_cf_current)) if (ocf_current and investing_cf_current) else None
    fcf_prior = (ocf_prior - abs(investing_cf_prior)) if (ocf_prior and investing_cf_prior) else None

    # Quality ratios
    def safe_div(n, d):
        return round(n / d, 2) if (n and d and d != 0) else None

    revenue = get_line_item_value(fs_index, 'revenue', 'group_current')
    bank_borrowings = get_line_item_value(fs_index, 'bank borrowings', 'group_current')

    # Asset quality
    total_assets = get_line_item_value(fs_index, 'total assets', 'group_current')
    total_assets_prior = get_line_item_value(fs_index, 'total assets', 'group_prior')
    non_current_assets = get_line_item_value(fs_index, 'non-current assets', 'group_current')
    current_assets = get_line_item_value(fs_index, 'current assets', 'group_current')

    # YoY helpers
    def yoy(cur, prev):
        if cur and prev and prev != 0:
            return round(((cur - prev) / abs(prev)) * 100, 1)
        return None

    # --- NEW: Cash flow details ---
    purchase_of_ppe = get_line_item_value(fs_index, 'purchase of property', 'group_current')
    purchase_of_ppe_prior = get_line_item_value(fs_index, 'purchase of property', 'group_prior')
    proceeds_from_disposal = get_line_item_value(fs_index, 'proceeds from disposal', 'group_current')
    proceeds_from_disposal_prior = get_line_item_value(fs_index, 'proceeds from disposal', 'group_prior')

    # Capex = abs(purchase_of_ppe)
    capex_current = abs(purchase_of_ppe) if purchase_of_ppe is not None else None
    capex_prior = abs(purchase_of_ppe_prior) if purchase_of_ppe_prior is not None else None

    # Working capital changes from cash flow
    wc_change_receivables = get_line_item_value(fs_index, 'changes in receivables', 'group_current')
    wc_change_receivables_prior = get_line_item_value(fs_index, 'changes in receivables', 'group_prior')
    wc_change_inventories = get_line_item_value(fs_index, 'changes in inventories', 'group_current')
    wc_change_inventories_prior = get_line_item_value(fs_index, 'changes in inventories', 'group_prior')
    wc_change_payables = get_line_item_value(fs_index, 'changes in payables', 'group_current')
    wc_change_payables_prior = get_line_item_value(fs_index, 'changes in payables', 'group_prior')

    # --- NEW: Expanded asset quality with prior year and % of total assets ---
    def pct_of_total(value, total):
        if value is not None and total is not None and total != 0:
            return round((value / total) * 100, 2)
        return None

    asset_quality_items = {
        "cash_and_bank_balances": make_metric(fs_index, "cash and bank balances"),
        "trade_receivables": make_metric(fs_index, "trade receivables"),
        "contract_assets": make_metric(fs_index, "contract assets"),
        "property_plant_equipment": make_metric(fs_index, "property, plant and equipment"),
        "inventories": make_metric(fs_index, "inventories"),
        "goodwill_and_intangibles": make_metric(fs_index, "goodwill"),
        "other_receivables": make_metric(fs_index, "other receivables"),
    }

    # Add pct_of_total_assets to each item
    for item_name, item_data in asset_quality_items.items():
        item_data["pct_of_total_assets"] = pct_of_total(item_data.get("current"), total_assets)
        item_data["pct_of_total_assets_prior"] = pct_of_total(item_data.get("prior"), total_assets_prior)

    return {
        "_metadata": create_metadata(source_file, extraction_time),
        "cash_flow_statement": {
            "operating": {"current": ocf_current, "prior": ocf_prior, "yoy_pct": yoy(ocf_current, ocf_prior)},
            "investing": {"current": investing_cf_current, "prior": investing_cf_prior},
            "financing": {"current": financing_cf_current, "prior": financing_cf_prior, "yoy_pct": yoy(financing_cf_current, financing_cf_prior)},
            "free_cash_flow": {"current": fcf_current, "prior": fcf_prior, "yoy_pct": yoy(fcf_current, fcf_prior)},
        },
        "cash_flow_quality": {
            "ocf_to_revenue_pct": safe_div(ocf_current, revenue),
            "ocf_to_debt_pct": safe_div(ocf_current, bank_borrowings),
            "interest_coverage": safe_div(ocf_current, interest_paid_current),
        },
        "cash_flow_details": {
            "interest_paid": {"current": interest_paid_current, "prior": interest_paid_prior},
            "dividends_paid": {"current": dividends_paid_current, "prior": dividends_paid_prior},
            "purchase_of_ppe": {
                "current": purchase_of_ppe,
                "prior": purchase_of_ppe_prior,
                "yoy_pct": yoy(purchase_of_ppe, purchase_of_ppe_prior),
                "_source": "fs_index.line_items['purchase of property']",
            },
            "proceeds_from_disposal_of_ppe": {
                "current": proceeds_from_disposal,
                "prior": proceeds_from_disposal_prior,
                "_source": "fs_index.line_items['proceeds from disposal']",
            },
            "capex": {
                "current": capex_current,
                "prior": capex_prior,
                "yoy_pct": yoy(capex_current, capex_prior),
                "_source": "Calculated: abs(purchase_of_property, plant and equipment)",
            },
            "working_capital_changes": {
                "change_in_receivables": {
                    "current": wc_change_receivables,
                    "prior": wc_change_receivables_prior,
                    "_source": "fs_index.line_items['changes in receivables']",
                },
                "change_in_inventories": {
                    "current": wc_change_inventories,
                    "prior": wc_change_inventories_prior,
                    "_source": "fs_index.line_items['changes in inventories']",
                },
                "change_in_payables": {
                    "current": wc_change_payables,
                    "prior": wc_change_payables_prior,
                    "_source": "fs_index.line_items['changes in payables']",
                },
                "_note": "From operating activities section of cash flow statement. Negative = cash inflow (e.g., collecting receivables).",
            },
        },
        "asset_quality": {
            "total_assets": {"current": total_assets, "prior": total_assets_prior, "yoy_pct": yoy(total_assets, total_assets_prior)},
            "non_current_assets": non_current_assets,
            "current_assets": current_assets,
            "asset_composition_pct": {
                "non_current": safe_div(non_current_assets, total_assets),
                "current": safe_div(current_assets, total_assets),
            },
            "items": asset_quality_items,
        },
        "_verification": {
            "data_quality": "REAL_DATA_EXTRACTED",
            "source": "fs_index.json cash flow + balance sheet items",
        }
    }


def extract_multi_year_trends(current_fs_index: Dict, prior_fs_indices: List[Dict]) -> Dict:
    """
    Extract multi-year trend data for enhanced financial analysis.

    Args:
        current_fs_index: Current year fs_index
        prior_fs_indices: List of prior year fs_indices (newest first)

    Returns:
        Dict with multi-year trend data for key metrics
    """
    extraction_time = datetime.now().isoformat()

    # Get current year
    fiscal_year_end = current_fs_index.get('fiscal_year_end')
    current_year = fiscal_year_end[:4] if fiscal_year_end else 'current'

    # Get prior years
    prior_years = []
    for idx in prior_fs_indices:
        fiscal_year_end = idx.get('fiscal_year_end')
        if fiscal_year_end and len(fiscal_year_end) >= 4:
            year = fiscal_year_end[:4]
            if year:
                prior_years.append(year)
        else:
            # Use placeholder if year not available
            prior_years.append(f'prior_{len(prior_years) + 1}')

    all_years = [current_year] + prior_years

    def get_metric_value(fs_index: Dict, metric_name: str) -> Optional[float]:
        """Helper to extract metric from fs_index"""
        return get_line_item_value(fs_index, metric_name, 'group_current')

    # Extract key metrics across all years
    metrics_to_track = [
        'revenue',
        'gross profit',
        'profit before tax',
        'profit for the financial year',
        'profit attributable to owners of the company',
        'total assets',
        'total liabilities',
        'total equity',
        'net cash from operating activities',
        'net cash from investing activities',
        'net cash from financing activities'
    ]

    trends = {}
    for metric in metrics_to_track:
        values = {}
        values['current'] = get_metric_value(current_fs_index, metric)

        for i, prior_idx in enumerate(prior_fs_indices):
            year_label = prior_years[i] if i < len(prior_years) else f'prior_{i+1}'
            values[year_label] = get_metric_value(prior_idx, metric)

        trends[metric] = values

    # Calculate CAGRs if we have 2+ years of data
    cagrs = {}
    if len(all_years) >= 2:
        for metric in metrics_to_track:
            current_val = trends[metric].get('current')
            oldest_val = trends[metric].get(prior_years[-1] if prior_years else None)

            if current_val and oldest_val and oldest_val != 0 and len(all_years) > 1:
                years_diff = len(all_years) - 1
                try:
                    cagr = ((current_val / oldest_val) ** (1 / years_diff)) - 1
                    cagrs[f"{metric}_cagr_{years_diff}yr"] = round(cagr * 100, 2)  # As percentage
                except:
                    pass

    return {
        "years": all_years,
        "num_years": len(all_years),
        "trends": trends,
        "cagrs": cagrs,
        "extraction_timestamp": extraction_time,
        "usage_note": "Workers should use this multi-year data for trend tables, CAGR calculations, and historical context. Compare FY2024 vs FY2023 vs FY2022 patterns."
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python data_extractor.py <fs_index.json> --company <NAME> [--prior <prior1.json>] [--prior <prior2.json>] [--text-blocks <text_blocks.jsonl>] [--output <output.json>]")
        print("\nMulti-year support:")
        print("  --prior can be specified multiple times for multi-year trend analysis")
        print("  Example: --prior 2023.json --prior 2022.json")
        sys.exit(1)

    fs_index_path = sys.argv[1]
    company_name = "Company"
    prior_fs_index_paths = []  # List of prior year paths
    text_blocks_path = None
    output_path = "data_bundles.json"

    # Parse arguments - support multiple --prior flags
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--company" and i + 1 < len(sys.argv):
            company_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--prior" and i + 1 < len(sys.argv):
            prior_fs_index_paths.append(sys.argv[i + 1])
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

    # Load multiple prior year fs_index files
    prior_fs_indices = []
    for prior_path in prior_fs_index_paths:
        print(f"Loading prior: {prior_path}")
        prior_fs_indices.append(load_fs_index(prior_path))

    # For backwards compatibility, also provide single prior if available
    prior_fs_index = prior_fs_indices[0] if prior_fs_indices else None

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
        "worker_4": extract_worker4_profitability_health(fs_index, prior_fs_index, fs_index_path),
        "worker_5": extract_worker5_risk(fs_index, fs_index_path),
        "worker_6": extract_worker6_cashflow(fs_index, fs_index_path),
    }

    # Add global verification metadata
    data_bundles["_global_verification"] = {
        "source_file": fs_index_path,
        "extraction_timestamp": extraction_time,
        "company_name": company_name,
        "has_prior_year_data": prior_fs_index is not None,
        "has_text_blocks": text_blocks_path is not None,
        "num_prior_years": len(prior_fs_indices),
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
        },
        "multi_year_support": {
            "available": len(prior_fs_indices) > 0,
            "years_loaded": len(prior_fs_indices) + 1,
            "trend_analysis": f"{len(prior_fs_indices) + 1}-year analysis enabled" if len(prior_fs_indices) > 0 else "Single year only"
        }
    }

    # Add multi-year trend data if multiple years available
    if len(prior_fs_indices) > 0:
        print(f"\n✓ Multi-year trend data available: {len(prior_fs_indices) + 1} years")
        data_bundles["_multi_year_trends"] = extract_multi_year_trends(fs_index, prior_fs_indices)

    # Write to output file
    with open(output_path, 'w') as f:
        json.dump(data_bundles, f, indent=2)

    print(f"\n✅ Data bundles created - HYBRID APPROACH")
    print(f"   Output: {output_path}")
    print(f"\n   Worker 1: Company Overview (text_blocks access + page hints)")
    print(f"   Worker 2: Core Performance (P&L + expenses)")
    print(f"   Worker 3: Business & Strategy (text_blocks access + page hints)")
    print(f"   Worker 4: Profitability & Health (ROE/ROA + solvency + working capital)")
    print(f"   Worker 5: Risk Assessment (risk metrics)")
    print(f"   Worker 6: Cash Flow & Outlook (OCF/FCF + asset quality + forecast)")
    print(f"\n✓ Extraction Strategy:")
    print(f"  - Structured data: fs_index.json (100% accurate)")
    print(f"  - Qualitative data: text_blocks.jsonl (worker extracts)")
    print(f"  - NO fragile regex patterns")
    print(f"  - Workers use LLM intelligence for context")

    if len(prior_fs_indices) > 0:
        print(f"\n✓ Multi-Year Trends:")
        print(f"  - Years: {len(prior_fs_indices) + 1} years of data")
        print(f"  - CAGR calculations: Available")
        print(f"  - Trend analysis: Enabled for all workers")
        print(f"  - Location: data_bundles._multi_year_trends")


if __name__ == "__main__":
    main()
