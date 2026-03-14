"""Tests for financial report validation script."""
import importlib.util
from pathlib import Path

# Load the module directly from file path
script_path = Path(__file__).parent.parent.parent.parent / "skills" / "financial-analysis-report" / "scripts" / "validate_report.py"
spec = importlib.util.spec_from_file_location("validate_report", script_path)
validate_report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_report)

ExtractedNumber = validate_report.ExtractedNumber


def test_extracted_number_creation():
    """Test ExtractedNumber dataclass can be created."""
    num = ExtractedNumber(value=3252.0, context="Revenue", line_num=5)
    assert num.value == 3252.0
    assert num.context == "Revenue"
    assert num.line_num == 5


def test_extract_numbers_from_tables():
    """Test extracting numbers from markdown tables."""
    extract_numbers_from_markdown = validate_report.extract_numbers_from_markdown

    report = """
| Metric | FY2024 | FY2023 | YoY |
|---|---:|---:|---:|
| Revenue | 3,252 | 2,057 | +58.1% |
| PBT | 276 | 189 | +45.9% |
"""

    numbers = extract_numbers_from_markdown(report)

    # Should find 4 numbers (Revenue current/prior, PBT current/prior)
    assert len(numbers) >= 4

    # Check revenue values found
    revenue_values = [n for n in numbers if 'revenue' in n.context.lower()]
    assert len(revenue_values) >= 2

    # Check values are correct
    values = [n.value for n in revenue_values]
    assert 3252.0 in values
    assert 2057.0 in values
