# Financial Report PDF Parsing Pipeline

A stage-based PDF parsing pipeline for financial reports. Extracts text, tables, and financial metrics using pdfplumber and an LLM (Qwen 3.5-flash via OpenAI-compatible API).

## Features

- 5-stage pipeline: preprocess → text → tables → metrics → aggregate
- SHA256-based caching to avoid reprocessing unchanged PDFs
- LLM-powered financial metric extraction (revenue, net income, EPS, etc.)
- Click CLI with progress output
- 84% test coverage (unit, integration, E2E)

## Installation

```bash
uv sync
```

## Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen3.5-flash
```

## Usage

```bash
# Parse a PDF
uv run finanalysis parse report.pdf --out ./output

# Force reprocess (ignore cache)
uv run finanalysis parse report.pdf --out ./output --force

# Run specific stage only (1-5)
uv run finanalysis parse report.pdf --stage 3

# Check version
uv run finanalysis --version
```

## Output Files

All outputs are written to the specified `--out` directory:

| File | Description |
|------|-------------|
| `document_manifest.json` | PDF metadata, page types, processing stats |
| `page_manifests.jsonl` | Per-page processing status |
| `text_blocks.jsonl` | Extracted text blocks with bounding boxes |
| `table_rows.jsonl` | Extracted table rows with cell data |
| `metric_candidates.jsonl` | LLM-extracted financial metrics with confidence |
| `summary.json` | Processing summary with statistics |

## Pipeline Stages

| Stage | Description |
|-------|-------------|
| 1 | Preprocess: compute PDF hash, classify pages (native_text/table/mixed/ocr_only) |
| 2 | Text: extract text blocks from native_text and mixed pages |
| 3 | Tables: extract table rows from table and mixed pages |
| 4 | Metrics: use LLM to extract financial metrics from table rows |
| 5 | Aggregate: combine all results, generate final output files |

## Development

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/finanalysis --cov-report=term-missing

# Run specific test types
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/e2e/
```

## Project Structure

```
src/finanalysis/
├── cli.py              # Click CLI entry point
├── pipeline.py         # Pipeline orchestrator
├── config.py           # Settings (pydantic-settings)
├── cache.py            # SHA256-based cache manager
├── models/             # Pydantic data models
│   ├── document.py     # DocumentManifest, PageManifest
│   ├── content.py      # TextBlock, TableRow
│   └── metrics.py      # MetricCandidate, MetricType
├── extractors/         # Low-level extraction
│   ├── pdf_utils.py    # pdfplumber wrapper, page classifier
│   ├── text_extractor.py
│   └── table_extractor.py
├── llm/
│   └── client.py       # OpenAI-compatible LLM client
└── stages/
    ├── stage1_preprocess.py
    ├── stage2_text.py
    ├── stage3_tables.py
    ├── stage4_metrics.py
    └── stage5_aggregate.py
```

## Architecture

See [docs/plans/2026-03-13-pdf-pipeline-design.md](docs/plans/2026-03-13-pdf-pipeline-design.md)
