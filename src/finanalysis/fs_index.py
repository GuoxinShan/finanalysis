# src/finanalysis/fs_index.py
"""Structured financial statement index.

Parses financial statement pages from PDFs into a structured index:
  line_item -> {group_current, group_prior, company_current, company_prior}

Uses deterministic pattern matching for extraction with direct lookup queries.
"""
import json
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Headers that identify primary financial statement pages
_FS_PATTERNS = [
    re.compile(r"STATEMENTS?\s+OF\s+PROFIT\s+OR\s+LOSS", re.IGNORECASE),
    re.compile(r"STATEMENTS?\s+OF\s+FINANCIAL\s+POSITION", re.IGNORECASE),
    re.compile(r"STATEMENTS?\s+OF\s+CASH\s+FLOWS?", re.IGNORECASE),
    re.compile(r"STATEMENTS?\s+OF\s+COMPREHENSIVE\s+INCOME", re.IGNORECASE),
    re.compile(r"INCOME\s+STATEMENTS?", re.IGNORECASE),
    re.compile(r"BALANCE\s+SHEETS?", re.IGNORECASE),
    re.compile(r"CONSOLIDATED\s+STATEMENTS?\s+OF", re.IGNORECASE),
]

_STMT_CASHFLOW_KW = {"CASH FLOW", "CASH FLOWS"}
_STMT_POSITION_KW = {"FINANCIAL POSITION", "BALANCE SHEET"}

# Map common currency codes to standard ISO codes
_CURRENCY_MAP = {
    "RM": "MYR", "MYR": "MYR",
    "USD": "USD", "US": "USD",
    "SGD": "SGD", "S": "SGD",
    "HKD": "HKD", "HK": "HKD",
    "EUR": "EUR",
    "GBP": "GBP",
    "CNY": "CNY", "RMB": "CNY",
    "IDR": "IDR", "RP": "IDR",
    "THB": "THB",
    "PHP": "PHP",
    "INR": "INR",
    "AUD": "AUD",
    "JPY": "JPY",
}


def _detect_currency(text: str) -> str:
    """Detect currency from financial statement page text.

    Looks for patterns like RM'000, USD'000, $'000 in column headers.
    Returns ISO currency code, defaults to 'USD' if undetectable.
    """
    # Match currency code before '000 (e.g. RM'000, USD'000)
    m = re.search(r"([A-Z]{1,3})['\u2019]\s*000", text)
    if m:
        code = m.group(1)
        if code in _CURRENCY_MAP:
            return _CURRENCY_MAP[code]
        # If it's already a 3-letter ISO code, use it directly
        if len(code) == 3:
            return code
    # Fallback: look for explicit currency mentions in headers
    for pattern, iso in [
        (r"\bRinggit\b", "MYR"),
        (r"\bSingapore\b.*\bDollars?\b", "SGD"),
        (r"\bHong\s+Kong\b.*\bDollars?\b", "HKD"),
        (r"\bAustralian\b.*\bDollars?\b", "AUD"),
        (r"(?:\bUS\b|\bUnited\s+States\b).*\bDollars?\b|\bDollars?\b.*\bUS\b", "USD"),
        (r"\bRupiah\b", "IDR"),
        (r"\bBaht\b", "THB"),
        (r"\bRupees?\b", "INR"),
        (r"\bYuan\b|\bRenminbi\b", "CNY"),
        (r"\bPound\b|\bSterling\b", "GBP"),
        (r"\bYen\b", "JPY"),
        (r"\bEuro\b", "EUR"),
    ]:
        if re.search(pattern, text, re.IGNORECASE):
            return iso
    return "USD"


def _detect_statement_type(text_upper: str) -> str:
    # Normalize whitespace to handle PDF extraction artifacts
    # (e.g., "FINANCIAL     POSITION" → "FINANCIAL POSITION")
    text_normalized = ' '.join(text_upper.split())

    if any(k in text_normalized for k in _STMT_CASHFLOW_KW):
        return "cash_flow"
    if any(k in text_normalized for k in _STMT_POSITION_KW):
        return "balance_sheet"
    return "income_statement"


def _parse_number(s: str) -> Optional[float]:
    s = s.strip()
    if not s or s == '-':
        return None
    negative = s.startswith('(') and s.endswith(')')
    s = s.replace('(', '').replace(')', '').replace(',', '').strip()
    try:
        val = float(s)
        return -val if negative else val
    except ValueError:
        return None


def _is_primary_fs_page(text: str) -> bool:
    """Check if a page is a primary financial statement (not notes/subsidiary)."""
    upper = text.upper()
    # Must have an FS header pattern
    if not any(p.search(upper) for p in _FS_PATTERNS):
        return False
    # Must NOT be inside notes section (normalize whitespace for comparison)
    text_normalized = re.sub(r'\s+', ' ', upper)
    if "NOTES TO THE FINANCIAL" in text_normalized:
        return False
    # Must have currency'000 column headers (e.g. RM'000, USD'000, $'000)
    # Handle both ASCII ' and Unicode right single quote (U+2019)
    if not re.search(r"[A-Z]{2,3}['\u2019]000|['\u2019]\s*000", text):
        return False
    # Must have enough data lines (comma-formatted numbers)
    data_count = len(re.findall(r'[\d,]{4,}', text))
    return data_count >= 5


def _parse_fs_line(line: str) -> Optional[dict]:
    """Parse a financial statement line into label + numeric values."""
    # Find number tokens: comma-formatted, parenthesized, or standalone integers/decimals
    # separated by whitespace (for items like EPS: "3         8")
    tokens = re.findall(
        r'\([\d,]+(?:\.\d+)?\)'       # (1,234) negative
        r'|-?(?:\d{1,3},)+\d{3}'      # 1,234,567 comma-formatted
        r'(?:\.\d+)?'                  # optional decimal
        r'|\d+\.\d+'                   # 3.14 decimal
        , line
    )

    if len(tokens) < 2:
        # Try matching standalone integers separated by whitespace
        # (for lines like "Basic and diluted earnings per share (sen)   3         8")
        # Only if line has a label with parenthetical unit (EPS or percentage)
        # Supports: sen (MYR), cents (USD/AUD/SGD/HKD), pence (GBP), paise (INR), fils (AED), fen (CNY)
        eps_unit_re = re.compile(
            r'\((?:sen|cents?|pence|p|paise|fils|fen|%)\)', re.IGNORECASE
        )
        if eps_unit_re.search(line):
            tokens = re.findall(r'(?<!\w)(\d+)(?!\w)', line)
            # Filter out note references (single digits before the unit marker)
            unit_match = eps_unit_re.search(line)
            unit_pos = unit_match.start() if unit_match else -1
            if unit_pos > 0:
                tokens = [t for t in tokens if line.find(t, unit_pos) >= unit_pos]

    if len(tokens) < 2:
        return None

    first_pos = line.find(tokens[0])
    label = line[:first_pos].strip()
    label = re.sub(r'\s+\d{1,2}\s*$', '', label).strip()

    values = [_parse_number(t) for t in tokens]
    return {"label": label or "", "raw_values": values}


def _is_note_ref(val: Optional[float], others: list[Optional[float]]) -> bool:
    if val is None:
        return False
    if val != int(val):
        return False
    iv = int(val)
    if 1 <= iv <= 50:
        magnitudes = [abs(v) for v in others if v is not None and abs(v) > 100]
        if magnitudes:
            return True
    return False


def _normalize(label: str) -> str:
    label = label.lower().strip()
    label = re.sub(r'\s+', ' ', label)
    # Normalize cash flow label variations:
    # "net cash (used in)/from operating" -> "net cash from operating"
    # "net cash from/(used in) investing" -> "net cash from investing"
    label = re.sub(r'\(used in\)/from', 'from', label)
    label = re.sub(r'from/\(used in\)', 'from', label)
    label = re.sub(r'\(used in\)', 'used in', label)
    return label.strip()


_MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def _detect_fiscal_year_end(text: str) -> Optional[str]:
    """Extract fiscal year end date from FS page text.

    Looks for patterns like:
      'AS AT 31 DECEMBER 2024'
      'FOR THE FINANCIAL YEAR ENDED 31 DECEMBER 2024'
      'YEAR ENDED 31 MARCH 2024'

    Returns ISO date string 'YYYY-MM-DD' or None.
    """
    m = re.search(
        r'(?:AS AT|YEAR ENDED|FINANCIAL YEAR ENDED)\s+(\d{1,2})\s+([A-Z]+)\s+(\d{4})',
        text, re.IGNORECASE
    )
    if m:
        day, month_str, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        month = _MONTH_MAP.get(month_str)
        if month:
            return f"{year}-{month:02d}-{day:02d}"
    return None


class FSIndex:
    """Structured financial statement index built from PDF pages."""

    def __init__(self):
        self.line_items: dict[str, dict] = {}
        self.currency: str = "USD"
        self.fiscal_year_end: Optional[str] = None   # ISO: 'YYYY-MM-DD'
        self.company_name: Optional[str] = None      # Provided by caller

    @classmethod
    def from_pdf(cls, pdf_path: Path, company_name: Optional[str] = None) -> "FSIndex":
        """Build FSIndex from a PDF file.

        Args:
            pdf_path: Path to the annual report PDF
            company_name: Company name or stock code (e.g. "Chin Hin Group Berhad", "CHINHIN")
        """
        index = cls()
        index.company_name = company_name
        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber required for FSIndex")
            return index

        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)

            # Two-phase scan: coarse sampling to locate FS region, then dense scan
            _SAMPLE_STEP = 10
            fs_region_start = None
            fs_region_end = None

            if num_pages > _SAMPLE_STEP * 3:
                # Phase 1: coarse scan every Nth page to find FS region
                for i in range(0, num_pages, _SAMPLE_STEP):
                    text = pdf.pages[i].extract_text(layout=True) or ""
                    if _is_primary_fs_page(text):
                        if fs_region_start is None:
                            fs_region_start = max(0, i - _SAMPLE_STEP)
                        fs_region_end = min(num_pages, i + _SAMPLE_STEP + 1)

                if fs_region_start is not None:
                    # Phase 2: dense scan within the discovered region
                    scan_range = range(fs_region_start, fs_region_end)
                    logger.debug(
                        f"FS region detected: pages {fs_region_start+1}-{fs_region_end} "
                        f"(scanned {num_pages // _SAMPLE_STEP + 1} samples)"
                    )
                else:
                    # No FS pages found in samples — fall back to full scan
                    scan_range = range(num_pages)
            else:
                # Small PDF — just scan everything
                scan_range = range(num_pages)

            found_fs = False
            consecutive_miss = 0
            _MAX_GAP = 15

            for i in scan_range:
                text = pdf.pages[i].extract_text(layout=True) or ""
                if not _is_primary_fs_page(text):
                    if found_fs:
                        consecutive_miss += 1
                        if consecutive_miss >= _MAX_GAP:
                            break
                    continue

                found_fs = True
                consecutive_miss = 0

                # Detect metadata from first FS page found
                if not hasattr(index, '_metadata_detected'):
                    index.currency = _detect_currency(text)
                    fy = _detect_fiscal_year_end(text)
                    if fy:
                        index.fiscal_year_end = fy
                    index._metadata_detected = True

                stmt_type = _detect_statement_type(text.upper())
                has_company = bool(re.search(r'\bCompany\b', text))
                logger.debug(f"Parsing FS page {i+1}: {stmt_type} company={has_company}")
                index._parse_page(text, stmt_type, i + 1, has_company)

        logger.info(f"Indexed {len(index.line_items)} line items from {pdf_path.name}")
        return index

    def _parse_page(self, text: str, stmt_type: str, page_num: int, has_company: bool):
        skip_patterns = re.compile(
            r"^(note|rm|group|company|for the financial|as at|"
            r"annual report|\d{4}\s*$|who we are|"
            r"financial statements|other information|"
            r"statements?\s+of|loss\s+and|comprehensive)",
            re.IGNORECASE
        )
        section_pattern = re.compile(
            r"^\s*(Non-Current\s+Assets|Current\s+Assets|"
            r"Non-Current\s+Liabilities|Current\s+Liabilities|"
            r"Equity|ASSETS|LIABILITIES|"
            r"Cash\s+Flows?\s+from\s+\w+\s+Activities|"
            r"Operating\s+Activities|Investing\s+Activities|Financing\s+Activities)",
            re.IGNORECASE
        )
        current_section = ""
        pending_label = ""  # For multi-line labels

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            # Check for section header
            sec_match = section_pattern.search(stripped)
            if sec_match and not re.search(r'[\d,]{4,}', stripped):
                current_section = sec_match.group(1).strip()
                pending_label = ""
                continue

            parsed = _parse_fs_line(line)
            if not parsed:
                # Line has text but no numbers — could be start of multi-line label
                # But only if it has NO numbers at all (avoid corrupting next line)
                if stripped and not skip_patterns.search(stripped) and not re.search(r'\d', stripped):
                    pending_label = stripped
                else:
                    pending_label = ""
                continue

            label = parsed["label"]

            # If label is short/empty and we have a pending label, join them
            if pending_label and (not label or len(label) < 30):
                label = f"{pending_label} {label}".strip() if label else pending_label
            # Keep pending_label for "attributable to:" patterns (applies to multiple lines)
            if "attributable to:" not in pending_label.lower():
                pending_label = ""

            if skip_patterns.search(label):
                continue

            values = parsed["raw_values"]

            # Strip leading note references
            while values and _is_note_ref(values[0], values[1:]):
                values = values[1:]

            if len(values) < 2:
                continue

            # Empty label = section subtotal
            if not label and current_section:
                label = current_section

            entry = {
                "label": label,
                "section": current_section,
                "statement": stmt_type,
                "page": page_num,
                "group_current": None,
                "group_prior": None,
                "company_current": None,
                "company_prior": None,
            }

            if has_company and len(values) >= 4:
                entry["group_current"] = values[0]
                entry["group_prior"] = values[1]
                entry["company_current"] = values[2]
                entry["company_prior"] = values[3]
            elif len(values) >= 2:
                entry["group_current"] = values[0]
                entry["group_prior"] = values[1]

            key = _normalize(label)
            # For duplicate labels, also store with section qualifier
            if current_section:
                section_key = _normalize(f"{label} ({current_section})")
                self.line_items[section_key] = entry

            # For the unqualified key: prefer current over non-current
            # (most queries about receivables/payables/borrowings mean current)
            existing = self.line_items.get(key)
            current_sections = {"Current Assets", "Current Liabilities"}
            if existing is None:
                self.line_items[key] = entry
            elif current_section in current_sections and existing.get("section") not in current_sections:
                # Override non-current with current
                self.line_items[key] = entry
            elif entry["group_current"] is not None and existing["group_current"] is None:
                self.line_items[key] = entry

    def lookup(self, label: str, entity: str = "group", period: str = "current") -> Optional[float]:
        key = _normalize(label)
        col = f"{entity}_{period}"

        # Direct match
        entry = self.line_items.get(key)
        if entry and entry.get(col) is not None:
            return abs(entry[col])

        # Section-qualified match (items in multiple sections)
        for suffix in [
            "current assets", "current liabilities",
            "non-current assets", "non-current liabilities",
            "equity", "operating activities",
            "investing activities", "financing activities",
        ]:
            qualified = _normalize(f"{label} ({suffix})")
            candidate = self.line_items.get(qualified)
            if candidate and candidate.get(col) is not None:
                return abs(candidate[col])

        # Fuzzy match as last resort
        entry = self._fuzzy_match(key)
        if entry and entry.get(col) is not None:
            return abs(entry[col])
        return None

    def _fuzzy_match(self, key: str) -> Optional[dict]:
        key_words = set(key.split())
        if not key_words:
            return None
        best_score = 0.0
        best_entry = None
        for stored_key, entry in self.line_items.items():
            stored_words = set(stored_key.split())
            overlap = len(key_words & stored_words)
            total = max(len(key_words), len(stored_words))
            score = overlap / total if total else 0
            # Bonus for substring containment
            if key in stored_key or stored_key in key:
                score += 0.3
            # Penalize section-qualified keys to prefer unqualified matches
            if '(' in stored_key and '(' not in key:
                score -= 0.05
            if score > best_score and score >= 0.45:
                best_score = score
                best_entry = entry
        return best_entry

    def save(self, path: Path):
        data = {
            "currency": self.currency,
            "fiscal_year_end": self.fiscal_year_end,
            "company_name": self.company_name,
            "line_items": self.line_items,
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load(cls, path: Path) -> "FSIndex":
        index = cls()
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict) and "line_items" in data:
            index.line_items = data["line_items"]
            index.currency = data.get("currency", "USD")
            index.fiscal_year_end = data.get("fiscal_year_end")
            index.company_name = data.get("company_name")
        else:
            index.line_items = data
        return index
