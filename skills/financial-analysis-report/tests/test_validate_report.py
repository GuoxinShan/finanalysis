"""Tests for validate_report.py"""
import json
import sys
from pathlib import Path
from unittest.mock import Mock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


def test_validate_yoy_calculations():
    """Test validating YoY percentage calculations."""
    from validate_report import validate_calculations

    # Correct calculation
    report = """
| Revenue | 3,252 | 2,057 | +58.1% |
"""

    issues = validate_calculations(report)

    # 58.1% is correct: (3252-2057)/2057 = 0.581 = 58.1%
    assert len(issues) == 0

    # Incorrect calculation
    bad_report = """
| Revenue | 3,252 | 2,057 | +60.0% |
"""

    issues = validate_calculations(bad_report)

    # Should catch wrong YoY%
    assert len(issues) == 1
    assert '58.1' in issues[0][2]  # Suggestion shows correct value


def test_validate_yoy_calculations_negative_correct():
    """Test validating correct negative YoY percentage calculations."""
    from validate_report import validate_calculations

    # Correct negative calculation (decline)
    report = """
| Revenue | 2,057 | 3,252 | -36.7% |
"""

    issues = validate_calculations(report)

    # -36.7% is correct: (2057-3252)/3252 = -0.367 = -36.7%
    assert len(issues) == 0


def test_validate_yoy_calculations_negative_incorrect():
    """Test detecting incorrect negative YoY percentage calculations."""
    from validate_report import validate_calculations

    # Incorrect negative calculation
    bad_report = """
| Revenue | 2,057 | 3,252 | -40.0% |
"""

    issues = validate_calculations(bad_report)

    # Should catch wrong negative YoY%
    assert len(issues) == 1
    assert '36.7' in issues[0][2]  # Suggestion shows correct value


def test_validate_tone():
    """Test detecting aggressive language."""
    from validate_report import validate_tone

    # Professional language
    good_report = "Revenue showed strong growth of 58% YoY."
    issues = validate_tone(good_report)
    assert len(issues) == 0

    # Aggressive language
    bad_report = "Revenue showed explosive growth of 58% YoY, while margins collapsed."
    issues = validate_tone(bad_report)

    # Should find 2 issues: 'explosive' and 'collapsed'
    assert len(issues) == 2
    assert any('explosive' in issue[1] for issue in issues)
    assert any('collapsed' in issue[1] for issue in issues)


def test_full_validation(tmp_path):
    """Test complete validation workflow."""
    from validate_report import validate_report

    # Create test files
    report = tmp_path / "test_report.md"
    report.write_text("""
| Revenue | 3,252 | 2,057 | +58.1% |
Revenue showed explosive growth.
""")

    fs_index = tmp_path / "fs_index.json"
    fs_index.write_text(json.dumps({
        'line_items': {
            'revenue': {
                'group_current': 3252347,
                'group_prior': 2057210
            }
        }
    }))

    # Run validation
    result = validate_report(report, fs_index)

    # Should have 0 CRITICAL issues (data is correct)
    assert result['total_critical'] == 0

    # Should have 1 FORMATTING issue (aggressive language)
    assert result['total_formatting'] == 1
    assert result['passed'] is True  # Formatting issues don't block
