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
