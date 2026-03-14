# src/finanalysis/qa.py
import logging
from pathlib import Path
from typing import Optional

from .config import Settings
from .retrieval import ChunkRetriever
from .llm.client import LLMClient

logger = logging.getLogger(__name__)

# Common stopwords for financial question parsing
_STOPWORDS = frozenset({
    "what", "was", "the", "for", "in", "of", "is", "are", "were", "how",
    "much", "as", "at", "end", "did", "do", "does", "a", "an", "and",
    "or", "to", "be", "been", "being", "have", "has", "had", "its",
    "this", "that", "these", "those", "from", "by", "on", "with",
})

# Headers that identify primary financial statement pages (works across companies)
_FS_HEADERS = {
    "STATEMENTS OF PROFIT",
    "STATEMENT OF PROFIT",
    "STATEMENTS OF FINANCIAL POSITION",
    "STATEMENT OF FINANCIAL POSITION",
    "STATEMENTS OF CASH FLOWS",
    "STATEMENT OF CASH FLOWS",
    "STATEMENTS OF COMPREHENSIVE INCOME",
    "STATEMENT OF COMPREHENSIVE INCOME",
    "INCOME STATEMENT",
    "BALANCE SHEET",
    "CASH FLOW STATEMENT",
    "CONSOLIDATED STATEMENT OF PROFIT",
    "CONSOLIDATED STATEMENT OF FINANCIAL POSITION",
    "CONSOLIDATED STATEMENT OF CASH FLOWS",
}


class FinancialQA:
    """Answer financial questions using full-page PDF text + LLM.

    Generic across any company — no company-specific logic.
    """

    def __init__(self, retriever: ChunkRetriever, settings: Settings, pdf_path: Optional[Path] = None):
        self.retriever = retriever
        self.pdf_path = Path(pdf_path) if pdf_path else None
        self.llm = LLMClient(
            settings=settings,
            system_prompt="You are a financial analyst. Extract exact numeric values from financial report excerpts."
        )
        self._page_index: dict[int, str] = {}
        self._fs_pages: set[int] = set()
        if self.pdf_path and self.pdf_path.exists():
            self._build_page_index()

    def _build_page_index(self) -> None:
        """Build full-text index of all PDF pages using pdfplumber layout extraction"""
        try:
            import pdfplumber
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text(layout=True) or ""
                    if text.strip():
                        self._page_index[i + 1] = text
                        text_upper = text.upper()
                        if any(h in text_upper for h in _FS_HEADERS):
                            self._fs_pages.add(i + 1)
            logger.info(
                f"Built page index: {len(self._page_index)} pages, "
                f"{len(self._fs_pages)} financial statement pages from {self.pdf_path.name}"
            )
        except Exception as e:
            logger.warning(f"Failed to build page index: {e}")

    def _search_pages(self, query: str, top_k: int = 5) -> list[tuple[int, str]]:
        """Search page index by keyword matching, return (page_num, text) pairs"""
        query_terms = set(query.lower().split()) - _STOPWORDS
        if not query_terms:
            return []

        scored: list[tuple[float, int, str]] = []
        for page_num, text in self._page_index.items():
            text_lower = text.lower()
            matches = sum(1 for t in query_terms if t in text_lower)
            if matches > 0:
                score = matches / len(query_terms)
                # Boost primary financial statement pages
                if page_num in self._fs_pages:
                    score += 0.5
                scored.append((score, page_num, text))

        scored.sort(key=lambda x: -x[0])
        return [(page_num, text) for _, page_num, text in scored[:top_k]]

    def answer(self, question: str, top_k: int = 5) -> Optional[float]:
        """Answer a financial question, returning a numeric value or None"""
        if self._page_index:
            pages = self._search_pages(question, top_k=top_k)
            if not pages:
                return None
            context = "\n\n---\n\n".join(f"[Page {pg}]\n{text}" for pg, text in pages)
        else:
            chunks = self.retriever.search(question, top_k=top_k)
            if not chunks:
                return None
            context = "\n\n---\n\n".join(
                f"[Page {c['page_number']}]\n{c['text']}" for c in chunks
            )

        prompt = f"""You are given pages from a company's financial annual report. Answer the question with a single number.

Context:
{context}

Question: {question}

Rules:
- Return ONLY a JSON object: {{"value": <number or null>, "unit": "<unit>"}}
- Look at the column headers to determine the unit (e.g. RM'000, USD'000, $'000)
- Return the number exactly as shown in the financial statements (do not multiply by unit)
- If the report shows values in millions (e.g. "RM X million"), convert to the table unit
- If you cannot find the answer in the provided context, return {{"value": null}}
- Do NOT return year numbers as the value
- If the report has Group vs Company columns, match the entity asked about in the question
- "Profit for the financial year" = net profit AFTER tax, not profit before tax
- Return absolute values (positive) for items like expenses, outflows, repayments
- For EPS, return the value in the unit shown (e.g. sen, cents)"""

        try:
            result = self.llm.extract_json(prompt=prompt, temperature=0.0)
            val = result.get("value")
            if val is None:
                return None
            return float(val)
        except Exception as e:
            logger.warning(f"LLM Q&A failed: {e}")
            return None
