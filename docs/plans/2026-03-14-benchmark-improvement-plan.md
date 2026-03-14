# Benchmark Accuracy Improvement Plan

**Date:** 2026-03-14
**Current accuracy:** 6.9% (4/58)
**Target accuracy:** ≥ 80%

---

## Root Cause Analysis

### What the benchmark tests
58 questions from annual report figures (e.g. "What was gross profit for 2024?").
Ground truth comes from `Chin Hin-AR 2024 Profit.csv` — the **annual report**.

### What the PDFs contain
The 3 PDFs are **quarterly interim reports** (Q4 filings), not annual reports.
However, Q4 interim reports include a **cumulative YTD column** which equals the full-year figure.

Example from 2025 PDF page 3:
```
Revenue   1,092,130  995,478  10%   4,072,171   3,252,347  25%
           (Q4 2025)  (Q4 2024)      (FY 2025)   (FY 2024)
```

The annual figures ARE present — the retrieval just fails to find and use them correctly.

### Failure breakdown (54 failures)

| Pattern | Count | Root cause |
|---------|-------|------------|
| Predicted registration number `201401021421` | 24 | Largest number in top chunk is the company reg no. |
| Predicted year number (2023/2024/2025) | 8 | Year appears as a standalone number in chunk |
| Wrong metric value (e.g. revenue instead of gross profit) | 22 | Retrieval returns revenue row; naive "largest number" picks it |

### Why 4 answers were correct
Revenue and total comprehensive income happened to be the largest number in the correct chunk, and the retrieval found the right page.

---

## Improvement Plan

### Phase 1 — Fix numeric extraction (quick wins, ~+20%)

**Task 1.1: Filter known non-financial numbers**

In `scripts/benchmark.py` `extract_number_from_text()`:
- Blacklist `201401021421` (registration number)
- Blacklist 4-digit year numbers (2023, 2024, 2025) when other candidates exist
- Blacklist numbers that appear in "Registration No." context

**Task 1.2: Prefer numbers in the same line as the metric keyword**

Instead of extracting the largest number from the whole chunk, extract the number on the same line as the metric keyword (e.g. "Revenue ... 3,243,547").

```python
def extract_number_near_keyword(text: str, keyword: str) -> float | None:
    for line in text.splitlines():
        if keyword.lower() in line.lower():
            nums = re.findall(r'-?[\d]{1,3}(?:,\d{3})+|-?\d+\.\d+', line)
            if nums:
                return float(nums[-1].replace(',', ''))  # last number on line = value column
    return None
```

**Task 1.3: Pick cumulative column, not individual quarter**

The income statement table has format: `[Q4 value] [Q4 prev] [YTD value] [YTD prev]`.
The 3rd or 4th number on a revenue line is the cumulative figure.
Prefer the larger of the two non-registration numbers on the line.

---

### Phase 2 — LLM-based Q&A retrieval (major improvement, ~+40%)

Replace the naive "extract largest number from top chunk" with an LLM call that uses retrieved chunks as context.

**Task 2.1: Add `ask` command to CLI**

```python
# src/finanalysis/qa.py
class FinancialQA:
    def __init__(self, retriever: ChunkRetriever, llm_client: LLMClient):
        ...

    def answer(self, question: str, top_k: int = 5) -> dict:
        chunks = self.retriever.search(question, top_k=top_k)
        context = "\n\n".join(c["text"] for c in chunks)
        prompt = f"""Answer this financial question using only the provided context.
Return a JSON object: {{"value": <number>, "unit": "RM'000", "reasoning": "..."}}
If you cannot find the answer, return {{"value": null, "reasoning": "not found"}}.

Context:
{context}

Question: {question}"""
        return self.llm_client.extract_json(prompt=prompt, temperature=0.0)
```

**Task 2.2: Update benchmark to use LLM Q&A**

```python
# In benchmark.py
def search_for_answer(retriever, llm_client, question, top_k=5):
    qa = FinancialQA(retriever=retriever, llm_client=llm_client)
    result = qa.answer(question, top_k=top_k)
    return result.get("value")
```

**Task 2.3: Add `finanalysis ask <output_dir> <question>` CLI command**

---

### Phase 3 — Structured income statement parsing (precision improvement, ~+15%)

The income statement on page 3 (2025) / page 20 (2024) is a structured table with labeled rows and 4 value columns. Parse it as a proper key-value store.

**Task 3.1: Detect and parse the income statement table**

In Stage 3 (table extraction), add a specialized parser for the quarterly report format:
```
[Label]  [Q_curr]  [Q_prev]  [YTD_curr]  [YTD_prev]
Revenue  986,678   527,415   3,243,547   2,057,210
```

Store as structured records:
```json
{"label": "Revenue", "q_value": 986678, "ytd_value": 3243547, "year": "2024"}
```

**Task 3.2: Add `metric_candidates.jsonl` entries from structured table**

Map table row labels to `MetricType` enum values and write high-confidence candidates.

**Task 3.3: Update retrieval to search structured records first**

In `ChunkRetriever.search()`, check structured financial records before falling back to text search.

---

### Phase 4 — Retrieval quality improvements

**Task 4.1: Add page-level metadata to chunks**

Tag each chunk with whether it's from the income statement, balance sheet, or cash flow section. Use section headers to detect this.

**Task 4.2: Boost chunks from financial statement pages**

When searching for financial metrics, boost scores for chunks from pages containing "Revenue", "Gross Profit", "Net Income" headers.

**Task 4.3: Add BM25 or TF-IDF scoring**

Replace simple term-match ratio with BM25 for better relevance ranking.

---

## Implementation Priority

| Phase | Effort | Expected accuracy gain | Cumulative |
|-------|--------|----------------------|------------|
| Phase 1 (numeric fix) | 2h | +20% | ~27% |
| Phase 2 (LLM Q&A) | 4h | +40% | ~67% |
| Phase 3 (structured parsing) | 6h | +15% | ~82% |
| Phase 4 (retrieval quality) | 4h | +5% | ~87% |

**Recommended order:** Phase 1 → Phase 2 → Phase 3 → Phase 4

---

## Quick Validation

After each phase, run:
```bash
uv run python scripts/benchmark.py
```

Target checkpoints:
- After Phase 1: ≥ 25%
- After Phase 2: ≥ 65%
- After Phase 3: ≥ 80%

---

## Notes

- The 2024 PDF has a small discrepancy: cumulative revenue = 3,243,547 vs GT = 3,252,347 (~0.27% diff, outside 1% tolerance). This may be a rounding difference between the interim report and the final annual report. Phase 3 structured parsing should resolve this by using the correct column.
- The 2025 PDF page 3 has the full income statement in a single text block — ideal for structured parsing.
- Registration number `201401021421` appears on nearly every page header. Must be filtered globally.
