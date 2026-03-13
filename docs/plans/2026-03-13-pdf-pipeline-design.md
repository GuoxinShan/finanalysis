# Financial Report PDF Parsing Pipeline - Design Document

**Date**: 2026-03-13
**Author**: Claude
**Status**: Design Approved

## Overview

A low-cost, stage-based PDF parsing pipeline for financial reports with intelligent page classification, selective OCR, and LLM-powered metric extraction.

### Goals

- Avoid full-document OCR (reduce cost and processing time)
- Stage-based processing with independent testability
- Page-level caching based on content hash
- Extract structured metrics using LLM
- Support extensibility (future: vector embeddings, advanced table extraction)

### Non-Goals (MVP)

- Vector database integration (extension point reserved)
- Complex agent orchestration
- Multi-language support (English-only for MVP)
- Perfect extraction (aim for "good enough", manual review for edge cases)

---

## Architecture

### Chosen Approach: Stage-Based Pipeline

The pipeline consists of 5 independent stages, each producing cached outputs:

```
Stage 1: PDF Preprocessing (page classification)
Stage 2: Text Block Extraction (native_text + mixed pages)
Stage 3: Table Extraction (table + mixed pages)
Stage 4: Metric Recognition (LLM-powered)
Stage 5: Result Aggregation (final output generation)
```

### Project Structure

```
finanalysis/
├── src/finanalysis/
│   ├── __init__.py
│   ├── cli.py                    # CLI entry point
│   ├── config.py                 # Configuration management
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── document.py          # DocumentManifest, PageManifest
│   │   ├── content.py           # TextBlock, TableRow
│   │   └── metrics.py           # MetricCandidate
│   ├── stages/                   # 5 processing stages
│   │   ├── __init__.py
│   │   ├── stage1_preprocess.py
│   │   ├── stage2_text.py
│   │   ├── stage3_table.py
│   │   ├── stage4_metrics.py
│   │   └── stage5_aggregate.py
│   ├── extractors/              # Low-level extraction tools
│   │   ├── __init__.py
│   │   ├── pdf_utils.py         # pdfplumber wrapper
│   │   ├── table_extractor.py   # Table extraction (pdfplumber + camelot)
│   │   └── ocr_extractor.py     # OCR wrapper (Tesseract)
│   ├── llm/                     # LLM-related code
│   │   ├── __init__.py
│   │   └── qwen_client.py       # Qwen 3.5-flash API client
│   └── cache.py                 # Cache management
├── tests/                       # Test suite
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── pyproject.toml               # uv project config
├── README.md
└── main.py                      # CLI entry: python main.py parse <pdf>
```

---

## Core Data Models

### DocumentManifest

Document-level metadata tracking processing state:

```python
class DocumentManifest(BaseModel):
    pdf_path: str
    pdf_hash: str                    # SHA256 for caching
    total_pages: int
    file_size_bytes: int
    processed_at: datetime

    # Statistics
    page_types: dict[str, int]      # {"native_text": 10, "table": 5, ...}
    text_block_count: int
    table_row_count: int
    metric_candidate_count: int

    # Configuration snapshot
    config_snapshot: dict           # For reproducibility
```

### PageManifest

Page-level metadata with processing status:

```python
class PageManifest(BaseModel):
    page_number: int                # 1-based
    page_type: str                  # native_text / table / mixed / ocr_only
    width: float
    height: float

    # Processing status
    text_extracted: bool = False
    table_extracted: bool = False
    ocr_applied: bool = False

    # References
    text_block_ids: List[str] = []
    table_row_ids: List[str] = []

    # Caching
    content_hash: str
```

### Content Models

```python
class TextBlock(BaseModel):
    id: str                         # UUID
    page_number: int
    text: str
    bbox: tuple[float, float, float, float]

    # Extension point for vector embeddings
    embedding: List[float] | None = None

class TableRow(BaseModel):
    id: str
    page_number: int
    table_index: int                # Which table on the page
    row_index: int                  # Which row in the table
    cells: List[str]

    # Metadata
    bbox: tuple[float, float, float, float]
    extraction_method: str          # "pdfplumber" / "camelot" / "fallback"
    confidence: float | None = None
```

### MetricCandidate

```python
class MetricType(str, Enum):
    REVENUE = "revenue"
    GROSS_PROFIT = "gross_profit"
    OPERATING_INCOME = "operating_income"
    NET_INCOME = "net_income"
    EPS = "eps"
    OPERATING_CASH_FLOW = "operating_cash_flow"

class MetricCandidate(BaseModel):
    id: str
    metric_type: MetricType
    value: float
    unit: str | None = None        # "million", "billion", None
    currency: str | None = None    # "USD", "CNY", None
    period: str | None = None      # "2023", "Q1 2023", None

    # Source tracking
    source_table_row_id: str
    source_text: str

    # LLM metadata
    confidence: float              # 0-1
    reasoning: str | None = None
```

---

## Stage Details

### Stage 1: PDF Preprocessing

**Responsibilities**:
- Compute PDF hash (SHA256)
- Check cache (skip if unchanged)
- Classify each page type
- Generate manifests

**Page Classification Algorithm**:

```python
def classify_page(page) -> str:
    text = page.extract_text()
    tables = page.find_tables()

    text_length = len(text) if text else 0
    has_tables = len(tables) > 0

    # Check if scanned image
    if text_length < 50 and not has_tables:
        return "ocr_only"

    # Calculate table coverage
    if has_tables:
        table_area = sum(t.bbox_area for t in tables)
        page_area = page.width * page.height
        table_ratio = table_area / page_area

        if table_ratio > 0.5:
            return "table"
        else:
            return "mixed"
    else:
        return "native_text"
```

**Outputs**:
- `document_manifest.json`
- `page_manifest.jsonl`

---

### Stage 2: Text Block Extraction

**Responsibilities**:
- Extract text from `native_text` and `mixed` pages
- Preserve positional information
- Filter short blocks (< 20 chars)

**Processing Flow**:
1. Filter pages with `page_type in ["native_text", "mixed"]`
2. Extract text using pdfplumber with position
3. Split by paragraphs (empty lines)
4. Generate TextBlock objects
5. Save to `text_blocks.jsonl`

**Outputs**:
- `text_blocks.jsonl`

---

### Stage 3: Table Extraction

**Responsibilities**:
- Extract tables from `table` and `mixed` pages
- Fallback strategy for failed extractions
- Mark extraction method and confidence

**Extraction Strategy**:

```python
def extract_table_with_fallback(page):
    # Method 1: pdfplumber (fast, simple tables)
    tables = page.extract_tables()
    if tables and validate_tables(tables):
        return tables, "pdfplumber", 0.9

    # Method 2: camelot (powerful, complex tables)
    try:
        tables = camelot.read_pdf(...)
        return tables, "camelot", 0.8
    except:
        pass

    # Fallback: mark for manual review
    return [], "fallback", 0.0
```

**Outputs**:
- `table_rows.jsonl`

---

### Stage 4: Metric Recognition (LLM)

**Responsibilities**:
- Send TableRows to LLM in batches
- Parse LLM JSON responses
- Validate extracted metrics

**LLM Prompt Template**:

```
You are a financial data extractor. Extract the following metrics from the table row:
- revenue
- gross_profit
- operating_income
- net_income
- eps (earnings per share)
- operating_cash_flow

Table row data:
{table_row_text}

Return a JSON array with this format:
[
  {
    "metric_type": "revenue",
    "value": 1234567,
    "unit": "million",
    "currency": "USD",
    "period": "2023",
    "confidence": 0.95,
    "reasoning": "Found in 'Total Revenue' column"
  }
]

Only include metrics that are clearly present in the data.
```

**Error Handling**:
- Retry failed API calls (exponential backoff, 3 attempts)
- Validate JSON structure
- Log low-confidence extractions

**Outputs**:
- `metric_candidates.jsonl`

---

### Stage 5: Result Aggregation

**Responsibilities**:
- Update DocumentManifest statistics
- Validate all output files
- Generate processing report
- Write final outputs

**Final Outputs**:
- `document_manifest.json`
- `page_manifest.jsonl`
- `text_blocks.jsonl`
- `table_rows.jsonl`
- `metric_candidates.jsonl`
- `summary.json` (processing summary)

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Input: PDF File                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Preprocessing                                      │
│  - Compute PDF hash                                          │
│  - Check cache ──→ If exists and unchanged ──→ Skip to S5   │
│  - Page classification                                       │
│  Output: document_manifest.json, page_manifest.jsonl         │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│  Stage 2: Text       │      │  Stage 3: Table      │
│  - native_text pages │      │  - table pages       │
│  - mixed page text   │      │  - mixed page tables │
│  Output: text_blocks │      │  Output: table_rows  │
└──────────┬───────────┘      └──────────┬───────────┘
           │                              │
           └──────────────┬───────────────┘
                          ▼
          ┌───────────────────────────────────┐
          │  Stage 4: LLM Metric Recognition   │
          │  - Batch process table_rows        │
          │  - Qwen 3.5-flash API calls        │
          │  Output: metric_candidates         │
          └──────────────┬────────────────────┘
                         ▼
          ┌───────────────────────────────────┐
          │  Stage 5: Aggregation              │
          │  - Update statistics               │
          │  - Generate all output files       │
          │  Output: Final 5 JSON/JSONL files  │
          └───────────────────────────────────┘
```

---

## Caching Mechanism

### Cache Manager

```python
class CacheManager:
    def compute_pdf_hash(self, pdf_path: str) -> str:
        """SHA256 hash of PDF file"""
        sha256 = hashlib.sha256()
        with open(pdf_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def get_cache_key(self, pdf_hash: str, stage: int) -> Path:
        """Cache file path: {cache_dir}/{pdf_hash}_stage{N}.json"""
        return self.cache_dir / f"{pdf_hash}_stage{stage}.json"

    def is_cached(self, pdf_hash: str, stage: int) -> bool:
        """Check if cache exists"""
        return self.get_cache_key(pdf_hash, stage).exists()
```

### Cache Strategy

- Each stage saves results to cache after completion
- If PDF hash unchanged, can resume from any stage
- `--force` flag invalidates all caches
- Cache files: `{pdf_hash}_stage{N}.json`

---

## Error Handling

### Exception Hierarchy

```python
class FinAnalysisError(Exception):
    """Base exception"""
    def __init__(self, message: str, stage: Optional[int] = None):
        self.message = message
        self.stage = stage

class PDFExtractionError(FinAnalysisError):
    """PDF extraction failed"""
    pass

class TableExtractionError(FinAnalysisError):
    """Table extraction failed (marked as fallback)"""
    pass

class LLMError(FinAnalysisError):
    """LLM API call failed"""
    pass

class ValidationError(FinAnalysisError):
    """Data validation failed"""
    pass
```

### Stage-Specific Handling

**Stage 1**: Fail fast on missing/corrupted PDF
**Stage 2 & 3**: Mark failed pages, continue processing others
**Stage 3**: Fallback strategy (pdfplumber → camelot → fallback)
**Stage 4**: Retry LLM calls (exponential backoff, 3 attempts)
**Stage 5**: Validate all outputs, generate error report

### Failure Reporting

```json
{
  "status": "partial_success",
  "failed_pages": [
    {
      "page_number": 23,
      "error": "Table extraction failed",
      "stage": 3
    }
  ],
  "recommendations": [
    "Page 23 table extraction failed - manual review recommended"
  ]
}
```

---

## Testing Strategy

### Test Layers

```
tests/
├── unit/                    # Unit tests (individual classes/functions)
├── integration/             # Integration tests (per-stage)
├── e2e/                     # End-to-end tests (full pipeline)
└── fixtures/                # Test data (sample PDFs)
```

### Coverage Targets

- Overall: 80%+
- models/: 90%+ (core data structures)
- extractors/: 75%+ (low-level tools)
- stages/: 80%+ (core logic)
- cache.py: 85%+ (state management)
- cli.py: 70%+ (entry point)

### Test Examples

**Unit Test**:
```python
def test_extract_simple_table():
    with pdfplumber.open("tests/fixtures/sample_table.pdf") as pdf:
        page = pdf.pages[0]
        tables, method, confidence = extract_table_with_fallback(page)

        assert len(tables) > 0
        assert method == "pdfplumber"
        assert confidence >= 0.9
```

**Integration Test**:
```python
def test_stage3_process_table_pages():
    page_manifests = [...]
    extractor = Stage3TableExtractor("tests/fixtures/sample.pdf")
    table_rows = extractor.process(page_manifests)

    assert all(row.page_number in [1, 3] for row in table_rows)
```

**E2E Test**:
```python
def test_full_pipeline():
    result = run_pipeline(
        pdf_path="CHINHIN-2023-12-31.pdf",
        output_dir=output_dir,
        force=True
    )

    assert (output_dir / "metric_candidates.jsonl").exists()
    assert len(result["metrics"]) >= 3
```

---

## Technology Stack

### Package Management
- **uv**: Fast Python package manager

### PDF Processing
- **pdfplumber**: Primary extraction tool
- **camelot-py**: Fallback for complex tables
- **pytesseract**: OCR for scanned pages

### LLM Integration
- **Qwen 3.5-flash**: Via Alibaba Cloud API (OpenAI-compatible)
- **API config**:
  - model: `qwen3.5-flash`
  - base_url: `https://dashscope.aliyuncs.com/compatible-mode/v1`

### Data Validation
- **Pydantic**: Type-safe data models and validation

### Configuration
- **Pydantic Settings**: Environment-based configuration

---

## CLI Interface

```bash
# Basic usage
python main.py parse CHINHIN-2023-12-31.pdf --out ./output

# Force reprocess (ignore cache)
python main.py parse CHINHIN-2023-12-31.pdf --out ./output --force

# Run specific stage only
python main.py parse CHINHIN-2023-12-31.pdf --out ./output --stage 2
```

---

## Extension Points

### Vector Embeddings (Reserved)

```python
class TextBlock(BaseModel):
    # ...
    embedding: List[float] | None = None  # Future: embedding integration
```

When ready, user will provide embedding model API.

### Additional Metrics

- Extend `MetricType` enum
- Update LLM prompt template
- No code changes to extraction logic

### Custom Table Extraction

- Implement new extractor in `extractors/`
- Register in `table_extractor.py` fallback chain

---

## Implementation Priorities (MVP)

### Phase 1: Core Infrastructure
1. Project setup (uv, dependencies)
2. Data models (Pydantic)
3. Cache manager
4. CLI skeleton

### Phase 2: Stages 1-3
5. Stage 1: PDF preprocessing
6. Stage 2: Text extraction
7. Stage 3: Table extraction (pdfplumber + camelot)

### Phase 3: Stages 4-5
8. LLM client (Qwen API)
9. Stage 4: Metric recognition
10. Stage 5: Aggregation

### Phase 4: Testing & Polish
11. Unit tests
12. Integration tests
13. E2E tests with real PDFs
14. Error handling refinement

---

## Success Criteria

- ✅ All 5 stages functional
- ✅ Cache mechanism working
- ✅ Successfully process CHINHIN-2023 PDF
- ✅ Extract at least 3 of 6 target metrics
- ✅ Test coverage ≥ 80%
- ✅ All CLI commands working
- ✅ Graceful error handling (no crashes)

---

## Future Enhancements (Post-MVP)

- [ ] Vector embeddings integration
- [ ] Multi-language support
- [ ] Advanced table recognition (ML-based)
- [ ] Web UI for review/editing
- [ ] Batch processing multiple PDFs
- [ ] Export to Excel/CSV
- [ ] Comparison across multiple years
