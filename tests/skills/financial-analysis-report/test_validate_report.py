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
