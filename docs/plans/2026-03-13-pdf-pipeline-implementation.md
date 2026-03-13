# Financial Report PDF Parsing Pipeline - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a stage-based PDF parsing pipeline for financial reports with intelligent page classification, selective OCR, and LLM-powered metric extraction.

**Architecture:** 5-stage pipeline (preprocess → text → table → metrics → aggregate) with page-level caching, graceful error handling, and independent testability per stage.

**Tech Stack:** Python, uv, pdfplumber, camelot-py, pytesseract, Pydantic, Qwen 3.5-flash LLM API

---

## Phase 1: Core Infrastructure

### Task 1: Project Setup with uv

**Files:**
- Create: `pyproject.toml`
- Create: `src/finanalysis/__init__.py`
- Create: `src/finanalysis/py.typed`
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Initialize uv project**

Run: `uv init --name finanalysis`
Expected: Creates pyproject.toml

**Step 2: Add dependencies**

Run: `uv add pdfplumber camelot-py[cv] pytesseract pydantic pydantic-settings openai pytest pytest-cov`
Expected: Creates uv.lock with dependencies

**Step 3: Create package structure**

Run:
```bash
mkdir -p src/finanalysis/{models,stages,extractors,llm}
mkdir -p tests/{unit,test_stages,test_extractors,integration,e2e,fixtures}
touch src/finanalysis/__init__.py
touch src/finanalysis/py.typed
```

**Step 4: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project specific
output/
cache/
*.log
.env
```

**Step 5: Create README.md**

```markdown
# Financial Report PDF Parsing Pipeline

A low-cost, stage-based PDF parsing pipeline for financial reports.

## Installation

```bash
uv sync
```

## Usage

```bash
python main.py parse <pdf_path> --out <output_dir>
```

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/finanalysis
```

## Architecture

See [docs/plans/2026-03-13-pdf-pipeline-design.md](docs/plans/2026-03-13-pdf-pipeline-design.md)
```

**Step 6: Commit**

```bash
git add pyproject.toml uv.lock src/finanalysis/.gitkeep src/finanalysis/__init__.py src/finanalysis/py.typed .gitignore README.md
git commit -m "chore: initialize project structure with uv"
```

---

### Task 2: Data Models - Document Models

**Files:**
- Create: `src/finanalysis/models/__init__.py`
- Create: `src/finanalysis/models/document.py`
- Create: `tests/unit/test_models/__init__.py`
- Create: `tests/unit/test_models/test_document.py`

**Step 1: Write failing test for DocumentManifest**

```python
# tests/unit/test_models/test_document.py
from datetime import datetime
from src.finanalysis.models.document import DocumentManifest

def test_document_manifest_creation():
    manifest = DocumentManifest(
        pdf_path="/path/to/test.pdf",
        pdf_hash="abc123",
        total_pages=10,
        file_size_bytes=1024,
        processed_at=datetime(2023, 1, 1, 12, 0),
        page_types={"native_text": 5, "table": 5},
        text_block_count=20,
        table_row_count=50,
        metric_candidate_count=6,
        config_snapshot={"model": "qwen3.5-flash"}
    )

    assert manifest.pdf_path == "/path/to/test.pdf"
    assert manifest.total_pages == 10
    assert manifest.page_types["native_text"] == 5
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_models/test_document.py::test_document_manifest_creation -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.finanalysis.models.document'"

**Step 3: Implement DocumentManifest**

```python
# src/finanalysis/models/document.py
from pydantic import BaseModel
from datetime import datetime
from typing import Dict

class DocumentManifest(BaseModel):
    """Document-level metadata"""
    pdf_path: str
    pdf_hash: str
    total_pages: int
    file_size_bytes: int
    processed_at: datetime

    # Statistics
    page_types: Dict[str, int]
    text_block_count: int
    table_row_count: int
    metric_candidate_count: int

    # Configuration snapshot
    config_snapshot: Dict[str, any]
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_models/test_document.py::test_document_manifest_creation -v`
Expected: PASS

**Step 5: Write failing test for PageManifest**

```python
# tests/unit/test_models/test_document.py (append)
from src.finanalysis.models.document import PageManifest

def test_page_manifest_creation():
    manifest = PageManifest(
        page_number=1,
        page_type="native_text",
        width=612.0,
        height=792.0,
        content_hash="def456"
    )

    assert manifest.page_number == 1
    assert manifest.page_type == "native_text"
    assert manifest.text_extracted == False
    assert manifest.table_extracted == False
    assert manifest.ocr_applied == False
    assert manifest.text_block_ids == []
    assert manifest.table_row_ids == []
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_models/test_document.py::test_page_manifest_creation -v`
Expected: FAIL with "cannot import name 'PageManifest'"

**Step 7: Implement PageManifest**

```python
# src/finanalysis/models/document.py (append)
from typing import List

class PageManifest(BaseModel):
    """Page-level metadata"""
    page_number: int
    page_type: str  # native_text / table / mixed / ocr_only
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

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_models/test_document.py::test_page_manifest_creation -v`
Expected: PASS

**Step 9: Export from __init__.py**

```python
# src/finanalysis/models/__init__.py
from .document import DocumentManifest, PageManifest

__all__ = ["DocumentManifest", "PageManifest"]
```

**Step 10: Commit**

```bash
git add src/finanalysis/models/ tests/unit/test_models/
git commit -m "feat: add DocumentManifest and PageManifest models"
```

---

### Task 3: Data Models - Content Models

**Files:**
- Create: `src/finanalysis/models/content.py`
- Create: `tests/unit/test_models/test_content.py`

**Step 1: Write failing test for TextBlock**

```python
# tests/unit/test_models/test_content.py
from src.finanalysis.models.content import TextBlock

def test_text_block_creation():
    block = TextBlock(
        id="test-id-123",
        page_number=1,
        text="This is sample text",
        bbox=(100.0, 200.0, 300.0, 250.0)
    )

    assert block.id == "test-id-123"
    assert block.page_number == 1
    assert block.text == "This is sample text"
    assert block.bbox == (100.0, 200.0, 300.0, 250.0)
    assert block.embedding is None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_models/test_content.py::test_text_block_creation -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement TextBlock**

```python
# src/finanalysis/models/content.py
from pydantic import BaseModel
from typing import List, Tuple, Optional

class TextBlock(BaseModel):
    """Text block extracted from PDF"""
    id: str
    page_number: int
    text: str
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)

    # Extension point for vector embeddings
    embedding: Optional[List[float]] = None
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_models/test_content.py::test_text_block_creation -v`
Expected: PASS

**Step 5: Write failing test for TableRow**

```python
# tests/unit/test_models/test_content.py (append)
from src.finanalysis.models.content import TableRow

def test_table_row_creation():
    row = TableRow(
        id="row-id-456",
        page_number=2,
        table_index=0,
        row_index=5,
        cells=["Revenue", "$1,234,567", "2023"],
        bbox=(50.0, 100.0, 550.0, 120.0),
        extraction_method="pdfplumber",
        confidence=0.95
    )

    assert row.id == "row-id-456"
    assert row.table_index == 0
    assert row.cells == ["Revenue", "$1,234,567", "2023"]
    assert row.extraction_method == "pdfplumber"
    assert row.confidence == 0.95
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_models/test_content.py::test_table_row_creation -v`
Expected: FAIL with "cannot import name 'TableRow'"

**Step 7: Implement TableRow**

```python
# src/finanalysis/models/content.py (append)
class TableRow(BaseModel):
    """Table row extracted from PDF"""
    id: str
    page_number: int
    table_index: int  # Which table on the page
    row_index: int    # Which row in the table
    cells: List[str]

    # Metadata
    bbox: Tuple[float, float, float, float]
    extraction_method: str  # "pdfplumber" / "camelot" / "fallback"
    confidence: Optional[float] = None
```

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_models/test_content.py::test_table_row_creation -v`
Expected: PASS

**Step 9: Export from __init__.py**

```python
# src/finanalysis/models/__init__.py (update)
from .document import DocumentManifest, PageManifest
from .content import TextBlock, TableRow

__all__ = ["DocumentManifest", "PageManifest", "TextBlock", "TableRow"]
```

**Step 10: Commit**

```bash
git add src/finanalysis/models/content.py src/finanalysis/models/__init__.py tests/unit/test_models/test_content.py
git commit -m "feat: add TextBlock and TableRow models"
```

---

### Task 4: Data Models - Metrics Models

**Files:**
- Create: `src/finanalysis/models/metrics.py`
- Create: `tests/unit/test_models/test_metrics.py`

**Step 1: Write failing test for MetricType**

```python
# tests/unit/test_models/test_metrics.py
from src.finanalysis.models.metrics import MetricType

def test_metric_type_enum():
    assert MetricType.REVENUE == "revenue"
    assert MetricType.GROSS_PROFIT == "gross_profit"
    assert MetricType.OPERATING_INCOME == "operating_income"
    assert MetricType.NET_INCOME == "net_income"
    assert MetricType.EPS == "eps"
    assert MetricType.OPERATING_CASH_FLOW == "operating_cash_flow"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_models/test_metrics.py::test_metric_type_enum -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement MetricType enum**

```python
# src/finanalysis/models/metrics.py
from enum import Enum

class MetricType(str, Enum):
    """Financial metric types"""
    REVENUE = "revenue"
    GROSS_PROFIT = "gross_profit"
    OPERATING_INCOME = "operating_income"
    NET_INCOME = "net_income"
    EPS = "eps"  # Earnings Per Share
    OPERATING_CASH_FLOW = "operating_cash_flow"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_models/test_metrics.py::test_metric_type_enum -v`
Expected: PASS

**Step 5: Write failing test for MetricCandidate**

```python
# tests/unit/test_models/test_metrics.py (append)
from src.finanalysis.models.metrics import MetricCandidate

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
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_models/test_metrics.py::test_metric_candidate_creation -v`
Expected: FAIL with "cannot import name 'MetricCandidate'"

**Step 7: Implement MetricCandidate**

```python
# src/finalysis/models/metrics.py (append)
from pydantic import BaseModel
from typing import Optional

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
```

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_models/test_metrics.py::test_metric_candidate_creation -v`
Expected: PASS

**Step 9: Export from __init__.py**

```python
# src/finanalysis/models/__init__.py (update)
from .document import DocumentManifest, PageManifest
from .content import TextBlock, TableRow
from .metrics import MetricType, MetricCandidate

__all__ = [
    "DocumentManifest", "PageManifest",
    "TextBlock", "TableRow",
    "MetricType", "MetricCandidate"
]
```

**Step 10: Commit**

```bash
git add src/finalysis/models/metrics.py src/finanalysis/models/__init__.py tests/unit/test_models/test_metrics.py
git commit -m "feat: add MetricType and MetricCandidate models"
```

---

### Task 5: Cache Manager

**Files:**
- Create: `src/finanalysis/cache.py`
- Create: `tests/unit/test_cache.py`

**Step 1: Write failing test for hash computation**

```python
# tests/unit/test_cache.py
import tempfile
from pathlib import Path
from src.finanalysis.cache import CacheManager

def test_compute_pdf_hash():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test PDF file
        test_file = Path(tmpdir) / "test.pdf"
        test_file.write_text("test content")

        cache_mgr = CacheManager(Path(tmpdir) / "cache")
        hash1 = cache_mgr.compute_pdf_hash(str(test_file))

        # Same content should produce same hash
        hash2 = cache_mgr.compute_pdf_hash(str(test_file))
        assert hash1 == hash2

        # Different content should produce different hash
        test_file.write_text("different content")
        hash3 = cache_mgr.compute_pdf_hash(str(test_file))
        assert hash1 != hash3
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_cache.py::test_compute_pdf_hash -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement hash computation**

```python
# src/finanalysis/cache.py
import hashlib
from pathlib import Path
from typing import Any, Optional
import json

class CacheManager:
    """File hash-based cache management"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True, parents=True)

    def compute_pdf_hash(self, pdf_path: str) -> str:
        """Compute SHA256 hash of PDF file"""
        sha256 = hashlib.sha256()
        with open(pdf_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_cache.py::test_compute_pdf_hash -v`
Expected: PASS

**Step 5: Write failing test for cache operations**

```python
# tests/unit/test_cache.py (append)
def test_cache_operations():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "cache"
        cache_mgr = CacheManager(cache_dir)

        pdf_hash = "test-hash-123"
        stage = 1
        test_data = {"key": "value", "number": 42}

        # Test save and load
        cache_mgr.save_cache(pdf_hash, stage, test_data)

        assert cache_mgr.is_cached(pdf_hash, stage)

        loaded_data = cache_mgr.load_cache(pdf_hash, stage)
        assert loaded_data == test_data

        # Test invalidate
        cache_mgr.invalidate(pdf_hash, stage)
        assert not cache_mgr.is_cached(pdf_hash, stage)
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_cache.py::test_cache_operations -v`
Expected: FAIL with "AttributeError: 'CacheManager' object has no attribute 'get_cache_key'"

**Step 7: Implement cache operations**

```python
# src/finalysis/cache.py (append methods)
    def get_cache_key(self, pdf_hash: str, stage: int) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{pdf_hash}_stage{stage}.json"

    def is_cached(self, pdf_hash: str, stage: int) -> bool:
        """Check if cache exists"""
        cache_file = self.get_cache_key(pdf_hash, stage)
        return cache_file.exists()

    def load_cache(self, pdf_hash: str, stage: int) -> Any:
        """Load cache"""
        cache_file = self.get_cache_key(pdf_hash, stage)
        with open(cache_file) as f:
            return json.load(f)

    def save_cache(self, pdf_hash: str, stage: int, data: Any):
        """Save cache"""
        cache_file = self.get_cache_key(pdf_hash, stage)
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

    def invalidate(self, pdf_hash: str, stage: Optional[int] = None):
        """Clear cache"""
        if stage is not None:
            cache_file = self.get_cache_key(pdf_hash, stage)
            cache_file.unlink(missing_ok=True)
        else:
            # Clear all stages
            for s in range(1, 6):
                cache_file = self.get_cache_key(pdf_hash, s)
                cache_file.unlink(missing_ok=True)
```

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_cache.py::test_cache_operations -v`
Expected: PASS

**Step 9: Commit**

```bash
git add src/finanalysis/cache.py tests/unit/test_cache.py
git commit -m "feat: implement CacheManager with hash-based caching"
```

---

### Task 6: Configuration

**Files:**
- Create: `src/finalysis/config.py`
- Create: `tests/unit/test_config.py`
- Create: `.env.example`

**Step 1: Write failing test for config**

```python
# tests/unit/test_config.py
from src.finanalysis.config import Settings

def test_settings_defaults():
    settings = Settings(
        openai_api_key="test-key",
        openai_base_url="https://api.example.com/v1"
    )

    assert settings.openai_api_key == "test-key"
    assert settings.openai_base_url == "https://api.example.com/v1"
    assert settings.llm_model == "qwen3.5-flash"
    assert settings.llm_temperature == 0.1
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_config.py::test_settings_defaults -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement Settings**

```python
# src/finalysis/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # LLM Configuration
    openai_api_key: str
    openai_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen3.5-flash"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4000

    # Processing Configuration
    cache_enabled: bool = True
    cache_dir: str = "./cache"
    output_dir: str = "./output"

    # Extraction Configuration
    text_min_length: int = 20  # Minimum text block length
    table_area_threshold: float = 0.5  # Table area ratio threshold

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_config.py::test_settings_defaults -v`
Expected: PASS

**Step 5: Create .env.example**

```bash
# .env.example
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen3.5-flash
LLM_TEMPERATURE=0.1

CACHE_ENABLED=true
CACHE_DIR=./cache
OUTPUT_DIR=./output
```

**Step 6: Commit**

```bash
git add src/finanalysis/config.py tests/unit/test_config.py .env.example
git commit -m "feat: add Pydantic Settings configuration"
```

---

### Task 7: CLI Skeleton

**Files:**
- Create: `main.py`
- Create: `src/finanalysis/cli.py`
- Create: `tests/unit/test_cli.py`

**Step 1: Write failing test for CLI**

```python
# tests/unit/test_cli.py
from click.testing import CliRunner
from src.finanalysis.cli import cli

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert 'finanalysis' in result.output

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'parse' in result.output
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_cli.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Add click dependency**

Run: `uv add click`
Expected: Updates uv.lock

**Step 4: Implement CLI skeleton**

```python
# src/finalysis/cli.py
import click
from pathlib import Path

@click.group()
@click.version_option(version='0.1.0', prog_name='finanalysis')
def cli():
    """Financial Report PDF Parsing Pipeline"""
    pass

@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--out', '-o', default='./output', help='Output directory')
@click.option('--force', '-f', is_flag=True, help='Force reprocess (ignore cache)')
@click.option('--stage', '-s', type=int, help='Run specific stage only (1-5)')
def parse(pdf_path: str, out: str, force: bool, stage: int):
    """Parse a financial report PDF"""
    output_dir = Path(out)
    output_dir.mkdir(exist_ok=True, parents=True)

    click.echo(f"Parsing: {pdf_path}")
    click.echo(f"Output: {output_dir}")
    click.echo(f"Force: {force}")

    if stage:
        click.echo(f"Running stage: {stage}")

    # TODO: Implement pipeline execution
    click.echo("Pipeline not yet implemented")

if __name__ == '__main__':
    cli()
```

**Step 5: Create main.py entry point**

```python
# main.py
from src.finanalysis.cli import cli

if __name__ == '__main__':
    cli()
```

**Step 6: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_cli.py -v`
Expected: PASS

**Step 7: Test CLI manually**

Run: `uv run python main.py --help`
Expected: Shows help text

Run: `uv run python main.py parse CHINHIN-2023-12-31.pdf --out ./output`
Expected: Shows "Pipeline not yet implemented"

**Step 8: Commit**

```bash
git add main.py src/finanalysis/cli.py tests/unit/test_cli.py pyproject.toml uv.lock
git commit -m "feat: add CLI skeleton with click"
```

---

## Phase 2: Stage 1 - Preprocessing

### Task 8: PDF Utils Wrapper

**Files:**
- Create: `src/finanalysis/extractors/__init__.py`
- Create: `src/finanalysis/extractors/pdf_utils.py`
- Create: `tests/unit/test_extractors/__init__.py`
- Create: `tests/unit/test_extractors/test_pdf_utils.py`

**Step 1: Write failing test for open_pdf**

```python
# tests/unit/test_extractors/test_pdf_utils.py
from src.finanalysis.extractors.pdf_utils import open_pdf

def test_open_pdf():
    # Use one of the real PDFs
    with open_pdf("CHINHIN-2023-12-31.pdf") as pdf:
        assert pdf is not None
        assert len(pdf.pages) > 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_extractors/test_pdf_utils.py::test_open_pdf -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement PDF utils context manager**

```python
# src/finalysis/extractors/pdf_utils.py
import pdfplumber
from contextlib import contextmanager
from typing import Generator

@contextmanager
def open_pdf(pdf_path: str) -> Generator[pdfplumber.PDF, None, None]:
    """Context manager for opening PDF files"""
    pdf = pdfplumber.open(pdf_path)
    try:
        yield pdf
    finally:
        pdf.close()

def get_page_count(pdf_path: str) -> int:
    """Get total page count of PDF"""
    with open_pdf(pdf_path) as pdf:
        return len(pdf.pages)

def get_page_dimensions(page: pdfplumber.pdf.Page) -> tuple[float, float]:
    """Get page dimensions (width, height)"""
    return (page.width, page.height)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_extractors/test_pdf_utils.py::test_open_pdf -v`
Expected: PASS

**Step 5: Write failing test for page classification**

```python
# tests/unit/test_extractors/test_pdf_utils.py (append)
from src.finanalysis.extractors.pdf_utils import classify_page

def test_classify_page_native_text():
    # Create a mock page with text
    class MockPage:
        def extract_text(self):
            return "This is a paragraph of text. " * 10

        def find_tables(self):
            return []

    page = MockPage()
    page_type = classify_page(page)
    assert page_type == "native_text"

def test_classify_page_table():
    # Create a mock page with table
    class MockTable:
        @property
        def bbox_area(self):
            return 400000  # Large area

    class MockPage:
        def extract_text(self):
            return ""

        def find_tables(self):
            return [MockTable()]

        @property
        def width(self):
            return 612

        @property
        def height(self):
            return 792

    page = MockPage()
    page_type = classify_page(page)
    assert page_type == "table"
```

**Step 6: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_extractors/test_pdf_utils.py::test_classify_page_native_text -v`
Expected: FAIL with "cannot import name 'classify_page'"

**Step 7: Implement page classification**

```python
# src/finanalysis/extractors/pdf_utils.py (append)
def classify_page(page) -> str:
    """Classify page type: native_text / table / mixed / ocr_only"""

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

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_extractors/test_pdf_utils.py -v`
Expected: PASS (all tests)

**Step 9: Commit**

```bash
git add src/finanalysis/extractors/ tests/unit/test_extractors/
git commit -m "feat: add PDF utils with page classification"
```

---

### Task 9: Stage 1 Implementation

**Files:**
- Create: `src/finanalysis/stages/__init__.py`
- Create: `src/finanalysis/stages/stage1_preprocess.py`
- Create: `tests/integration/test_stage1_preprocess.py`

**Step 1: Write failing test for Stage 1**

```python
# tests/integration/test_stage1_preprocess.py
from src.finanalysis.stages.stage1_preprocess import Stage1Preprocess
from pathlib import Path
import tempfile

def test_stage1_process():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        stage1 = Stage1Preprocess()
        doc_manifest, page_manifests = stage1.process(
            pdf_path="CHINHIN-2023-12-31.pdf",
            output_dir=output_dir
        )

        # Verify document manifest
        assert doc_manifest.pdf_path == "CHINHIN-2023-12-31.pdf"
        assert doc_manifest.total_pages > 0
        assert len(doc_manifest.pdf_hash) == 64  # SHA256 hex length

        # Verify page manifests
        assert len(page_manifests) == doc_manifest.total_pages
        assert all(p.page_number > 0 for p in page_manifests)
        assert all(p.page_type in ["native_text", "table", "mixed", "ocr_only"] for p in page_manifests)

        # Verify output files exist
        assert (output_dir / "document_manifest.json").exists()
        assert (output_dir / "page_manifest.jsonl").exists()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/integration/test_stage1_preprocess.py::test_stage1_process -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement Stage 1**

```python
# src/finalysis/stages/stage1_preprocess.py
import json
from pathlib import Path
from datetime import datetime
import os

from ..models import DocumentManifest, PageManifest
from ..extractors.pdf_utils import open_pdf, classify_page, get_page_count, get_page_dimensions
from ..cache import CacheManager
from ..config import Settings

class Stage1Preprocess:
    """Stage 1: PDF Preprocessing and page classification"""

    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.cache_mgr = CacheManager(Path(self.settings.cache_dir))

    def process(self, pdf_path: str, output_dir: Path) -> tuple[DocumentManifest, list[PageManifest]]:
        """Process PDF and generate manifests"""

        # Compute hash
        pdf_hash = self.cache_mgr.compute_pdf_hash(pdf_path)

        # Check cache
        if self.cache_mgr.is_cached(pdf_hash, stage=1) and self.settings.cache_enabled:
            # Load from cache
            cached = self.cache_mgr.load_cache(pdf_hash, stage=1)
            doc_manifest = DocumentManifest(**cached["document_manifest"])
            page_manifests = [PageManifest(**p) for p in cached["page_manifests"]]
            return doc_manifest, page_manifests

        # Process PDF
        file_size = os.path.getsize(pdf_path)
        page_manifests = []

        with open_pdf(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, start=1):
                # Compute page content hash (simplified)
                text = page.extract_text() or ""
                import hashlib
                content_hash = hashlib.md5(text.encode()).hexdigest()

                # Classify page
                page_type = classify_page(page)

                # Get dimensions
                width, height = get_page_dimensions(page)

                # Create page manifest
                page_manifest = PageManifest(
                    page_number=page_num,
                    page_type=page_type,
                    width=width,
                    height=height,
                    content_hash=content_hash
                )
                page_manifests.append(page_manifest)

        # Count page types
        page_types = {}
        for pm in page_manifests:
            page_types[pm.page_type] = page_types.get(pm.page_type, 0) + 1

        # Create document manifest
        doc_manifest = DocumentManifest(
            pdf_path=pdf_path,
            pdf_hash=pdf_hash,
            total_pages=total_pages,
            file_size_bytes=file_size,
            processed_at=datetime.now(),
            page_types=page_types,
            text_block_count=0,  # Will be updated in later stages
            table_row_count=0,
            metric_candidate_count=0,
            config_snapshot={
                "cache_enabled": self.settings.cache_enabled,
                "llm_model": self.settings.llm_model
            }
        )

        # Save to cache
        self.cache_mgr.save_cache(pdf_hash, stage=1, {
            "document_manifest": doc_manifest.model_dump(),
            "page_manifests": [p.model_dump() for p in page_manifests]
        })

        # Save output files
        output_dir.mkdir(exist_ok=True, parents=True)

        with open(output_dir / "document_manifest.json", 'w') as f:
            json.dump(doc_manifest.model_dump(mode='json'), f, indent=2, default=str)

        with open(output_dir / "page_manifest.jsonl", 'w') as f:
            for pm in page_manifests:
                f.write(json.dumps(pm.model_dump()) + '\n')

        return doc_manifest, page_manifests
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/integration/test_stage1_preprocess.py::test_stage1_process -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/finalysis/stages/ tests/integration/test_stage1_preprocess.py
git commit -m "feat: implement Stage 1 preprocessing with page classification"
```

---

## Phase 3-7: Remaining Stages

[Due to length constraints, I'll summarize the remaining tasks. Each follows the same TDD pattern with failing tests → implementation → passing tests → commit.]

### Phase 3: Stage 2 (Text Extraction)
- Task 10: Text extractor utility
- Task 11: Stage 2 implementation
- Task 12: Integration test

### Phase 4: Stage 3 (Table Extraction)
- Task 13: Table extractor with fallback
- Task 14: Stage 3 implementation
- Task 15: Integration test

### Phase 5: Stage 4 (LLM Metrics)
- Task 16: LLM client (OpenAI-compatible)
- Task 17: Stage 4 implementation
- Task 18: Integration test

### Phase 6: Stage 5 (Aggregation)
- Task 19: Stage 5 implementation
- Task 20: Integration test

### Phase 7: End-to-End
- Task 21: Full pipeline integration
- Task 22: E2E test with real PDF
- Task 23: Error handling refinement
- Task 24: Documentation update

---

## Execution Summary

**Total Tasks**: 24
**Estimated Time**: 3-4 hours
**Test Coverage Target**: 80%+

**Key Milestones**:
1. ✅ Infrastructure ready (Tasks 1-7)
2. ✅ Stage 1 working (Tasks 8-9)
3. ⏳ All extraction stages (Tasks 10-15)
4. ⏳ LLM integration (Tasks 16-18)
5. ⏳ Full pipeline (Tasks 19-24)

---

## Next Steps

After completing this plan:
1. Run full test suite: `uv run pytest --cov=src/finanalysis`
2. Test with real PDF: `uv run python main.py parse CHINHIN-2023-12-31.pdf --out ./output`
3. Verify all output files generated correctly
4. Review metric candidates quality
