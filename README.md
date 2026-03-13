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
