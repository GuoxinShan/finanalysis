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


def test_find_expected_value():
    """Test finding expected value from fs_index.json."""
    find_expected_value = validate_report.find_expected_value

    # Mock fs_index structure
    fs_index = {
        'line_items': {
            'revenue': {'group_current': 3252.0, 'group_prior': 2057.0},
            'pbt': {'group_current': 276.0, 'group_prior': 189.0},
            'total_assets': {'group_current': 5000.0, 'group_prior': 4500.0},
        }
    }

    # Test exact match
    assert find_expected_value('revenue', fs_index) == 3252.0

    # Test alias match (Total Revenue -> revenue)
    assert find_expected_value('Total Revenue', fs_index) == 3252.0

    # Test PBT match
    assert find_expected_value('PBT', fs_index) == 276.0

    # Test not found case
    assert find_expected_value('Nonexistent Metric', fs_index) is None
