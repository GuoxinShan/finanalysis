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


def test_values_match():
    """Test values_match helper with tolerance."""
    values_match = validate_report.values_match

    # Test exact match
    assert values_match(100.0, 100.0, tolerance_pct=0.01)

    # Test within tolerance (1%)
    assert values_match(101.0, 100.0, tolerance_pct=0.01)
    assert values_match(99.0, 100.0, tolerance_pct=0.01)

    # Test outside tolerance
    assert not values_match(102.0, 100.0, tolerance_pct=0.01)
    assert not values_match(98.0, 100.0, tolerance_pct=0.01)

    # Test zero case
    assert values_match(0.0, 0.0, tolerance_pct=0.01)
    assert not values_match(1.0, 0.0, tolerance_pct=0.01)


def test_validate_data_accuracy_correct_values():
    """Test validation with correct values (should return no issues)."""
    validate_data_accuracy = validate_report.validate_data_accuracy

    # Report with correct values (in RM millions)
    # fs_index values are in RM'000, so 3252000 becomes 3252.0 million
    report = """
| Metric | FY2024 | FY2023 | YoY |
|---|---:|---:|---:|
| Revenue | 3,252 | 2,057 | +58.1% |
| PBT | 276 | 189 | +45.9% |
"""

    fs_index = {
        'line_items': {
            'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
            'pbt': {'group_current': 276000.0, 'group_prior': 189000.0},
        }
    }

    issues = validate_data_accuracy(report, fs_index)

    # Should return no issues (values match within tolerance)
    assert len(issues) == 0


def test_validate_data_accuracy_wrong_values():
    """Test validation with wrong values (should return issues)."""
    validate_data_accuracy = validate_report.validate_data_accuracy

    # Report with WRONG values
    report = """
| Metric | FY2024 | FY2023 | YoY |
|---|---:|---:|---:|
| Revenue | 4,000 | 2,500 | +60.0% |
"""

    fs_index = {
        'line_items': {
            'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
        }
    }

    issues = validate_data_accuracy(report, fs_index)

    # Should return issues for wrong revenue
    assert len(issues) >= 1

    # Check issue contains expected information
    line_num, description, suggestion = issues[0]
    assert 'Revenue' in description or 'revenue' in description.lower()
    assert '3252' in suggestion or '3252.0' in suggestion  # Expected value mentioned


def test_validate_data_accuracy_skip_unknown_metrics():
    """Test that metrics not in fs_index are skipped."""
    validate_data_accuracy = validate_report.validate_data_accuracy

    report = """
| Metric | FY2024 | FY2023 | YoY |
|---|---:|---:|---:|
| Custom Metric | 1,000 | 800 | +25.0% |
"""

    fs_index = {
        'line_items': {
            'revenue': {'group_current': 3252000.0},
        }
    }

    issues = validate_data_accuracy(report, fs_index)

    # Should return no issues (metric not in fs_index, so skipped)
    assert len(issues) == 0
