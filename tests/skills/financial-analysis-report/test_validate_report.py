"""Tests for financial report validation script."""
import importlib.util
import json
import tempfile
from pathlib import Path

# Load the module directly from file path
script_path = Path(__file__).parent.parent.parent.parent / "skills" / "financial-analysis-report" / "scripts" / "validate_report.py"
spec = importlib.util.spec_from_file_location("validate_report", script_path)
validate_report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_report)

ExtractedNumber = validate_report.ExtractedNumber


# ═══════════════════════════════════════════════════════════════════════════════
# EXISTING TESTS (preserved from original)
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# NEW TESTS: Inline text number extraction
# ═══════════════════════════════════════════════════════════════════════════════

class TestInlineTextExtraction:
    """Tests for enhanced number extraction from inline text."""

    def test_extract_inline_percentage(self):
        """Test extracting percentages from inline text (financial claims, not YoY changes)."""
        extract_numbers_from_markdown = validate_report.extract_numbers_from_markdown

        # "grew 58%" is a YoY change value -- correctly NOT extracted (handled by validate_calculations)
        # "RM3.25b" is a currency amount that IS extracted
        report = "Revenue grew 58% to RM3.25b in FY2024."
        numbers = extract_numbers_from_markdown(report)

        # Should find the 3.25 from RM3.25b as an inline text number
        inline_numbers = [n for n in numbers if n.source == "inline_text"]
        values = [n.value for n in inline_numbers]
        assert 3.25 in values
        # 58% should NOT be extracted (it's a YoY change value)
        assert 58.0 not in values

    def test_extract_inline_ratio(self):
        """Test extracting ratio values (0.8x) from inline text."""
        extract_numbers_from_markdown = validate_report.extract_numbers_from_markdown

        report = "Net debt-to-equity of 0.8x remains manageable."
        numbers = extract_numbers_from_markdown(report)

        inline_numbers = [n for n in numbers if n.source == "inline_text"]
        values = [n.value for n in inline_numbers]
        assert 0.8 in values

    def test_skip_years_in_inline_text(self):
        """Test that bare year numbers (2024) are not extracted."""
        extract_numbers_from_markdown = validate_report.extract_numbers_from_markdown

        report = "The company was founded in 2024 and operates in Malaysia."
        numbers = extract_numbers_from_markdown(report)

        inline_numbers = [n for n in numbers if n.source == "inline_text"]
        # 2024 should be skipped
        assert not any(n.value == 2024.0 for n in inline_numbers)

    def test_skip_bullet_numbers(self):
        """Test that small integers (1-12) without context are skipped."""
        extract_numbers_from_markdown = validate_report.extract_numbers_from_markdown

        report = "There are 3 key risks facing the company."
        numbers = extract_numbers_from_markdown(report)

        inline_numbers = [n for n in numbers if n.source == "inline_text"]
        # 3 without financial context should be skipped
        assert not any(n.value == 3.0 for n in inline_numbers)

    def test_skip_fy_references(self):
        """Test that FY2024-style references are not extracted."""
        extract_numbers_from_markdown = validate_report.extract_numbers_from_markdown

        report = "FY2024 revenue reached RM3,252 million."
        numbers = extract_numbers_from_markdown(report)

        inline_numbers = [n for n in numbers if n.source == "inline_text"]
        # 2024 should be skipped
        assert not any(n.value == 2024.0 for n in inline_numbers)

    def test_extract_currency_amount(self):
        """Test extracting RM amounts from inline text."""
        extract_numbers_from_markdown = validate_report.extract_numbers_from_markdown

        report = "Cash position stands at RM410m, providing ample liquidity."
        numbers = extract_numbers_from_markdown(report)

        inline_numbers = [n for n in numbers if n.source == "inline_text"]
        values = [n.value for n in inline_numbers]
        assert 410.0 in values

    def test_source_field_on_extracted_numbers(self):
        """Test that extracted numbers have correct source field."""
        extract_numbers_from_markdown = validate_report.extract_numbers_from_markdown

        report = """
| Revenue | 3,252 | 2,057 |
Gross margin was 15.4% for the year.
"""
        numbers = extract_numbers_from_markdown(report)

        table_numbers = [n for n in numbers if n.source == "table"]
        inline_numbers = [n for n in numbers if n.source == "inline_text"]

        # Table numbers should have source="table"
        assert len(table_numbers) >= 2
        assert all(n.source == "table" for n in table_numbers)

        # 15.4% from gross margin claim should be inline
        assert any(n.value == 15.4 and n.source == "inline_text" for n in inline_numbers)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW TESTS: Unverifiable detection
# ═══════════════════════════════════════════════════════════════════════════════

class TestDetectUnverifiable:
    """Tests for unverifiable financial claim detection."""

    def test_verifiable_margin_not_flagged(self):
        """Test that a margin that can be derived from fs_index is not flagged."""
        detect_unverifiable = validate_report.detect_unverifiable

        report = "Gross margin was 15.4% for the year."

        fs_index = {
            'line_items': {
                'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
                'gross_profit': {'group_current': 502100.0, 'group_prior': 380200.0},
            }
        }

        # gross_profit / revenue * 100 = 502100/3252000 * 100 = 15.44% ~= 15.4%
        issues = detect_unverifiable(report, fs_index)
        # Should not flag since 15.4% is derivable from fs_index (within 0.5pp)
        assert len(issues) == 0

    def test_unverifiable_concentration_flagged(self):
        """Test that a concentration claim with no fs_index match is flagged."""
        detect_unverifiable = validate_report.detect_unverifiable

        report = "Customer concentration at 35% remains a key risk."

        fs_index = {
            'line_items': {
                'revenue': {'group_current': 3252000.0},
            }
        }

        issues = detect_unverifiable(report, fs_index)
        assert len(issues) >= 1
        assert 'Unverifiable' in issues[0][1]

    def test_unverifiable_yield_flagged(self):
        """Test that a yield claim with no fs_index match is flagged."""
        detect_unverifiable = validate_report.detect_unverifiable

        report = "The company achieved a dividend yield of 4.2%."

        fs_index = {
            'line_items': {
                'revenue': {'group_current': 3252000.0},
            }
        }

        issues = detect_unverifiable(report, fs_index)
        assert len(issues) >= 1

    def test_skip_table_rows(self):
        """Test that table rows are not checked by detect_unverifiable."""
        detect_unverifiable = validate_report.detect_unverifiable

        report = """
| Concentration | 35% |
"""

        fs_index = {'line_items': {}}

        issues = detect_unverifiable(report, fs_index)
        # Table rows should be skipped
        assert len(issues) == 0

    def test_verified_number_not_double_flagged(self):
        """Test that already-verified numbers are not flagged as unverifiable."""
        detect_unverifiable = validate_report.detect_unverifiable

        report = "Gross margin was 15.4% for the year."

        fs_index = {
            'line_items': {
                'revenue': {'group_current': 3252000.0},
                'gross_profit': {'group_current': 502100.0},
            }
        }

        # Mark 15.4 at line 1 as already verified
        verified = {(15.4, 1)}
        issues = detect_unverifiable(report, fs_index, verified_numbers=verified)
        assert len(issues) == 0

    def test_market_share_flagged(self):
        """Test that market share claims are flagged."""
        detect_unverifiable = validate_report.detect_unverifiable

        report = "The company holds a market share of 25% in the construction sector."

        fs_index = {
            'line_items': {
                'revenue': {'group_current': 3252000.0},
            }
        }

        issues = detect_unverifiable(report, fs_index)
        assert len(issues) >= 1
        assert 'Unverifiable' in issues[0][1]


# ═══════════════════════════════════════════════════════════════════════════════
# NEW TESTS: Rounded derivation detection
# ═══════════════════════════════════════════════════════════════════════════════

class TestRoundedDerivation:
    """Tests for rounded derivation detection."""

    def test_rounded_derivation_detected(self):
        """Test detection of percentage computed from rounded intermediates."""
        detect_rounded_derivation = validate_report.detect_rounded_derivation

        report = "NCI share was 45.0% of total profit."

        # Values where 3-significant-figure rounding causes a difference:
        # Raw: 97078/215492 = 45.05% -> rounds to 45.0% or 45.1%
        # 3sf rounded: 97100/215000 = 45.16%
        # Difference: 0.11pp -> should be flagged (>0.1pp threshold)
        fs_index = {
            'line_items': {
                'attributable_profit': {'group_current': 97078000.0},
                'pat': {'group_current': 215492000.0},
            }
        }

        issues = detect_rounded_derivation(report, fs_index)
        # Should detect the rounded derivation
        assert len(issues) >= 1
        assert 'rounded' in issues[0][1].lower() or 'Rounded' in issues[0][1]

    def test_no_false_positive_for_exact_match(self):
        """Test that exact percentage matches are not flagged."""
        detect_rounded_derivation = validate_report.detect_rounded_derivation

        report = "Gross margin was 15.4% for the year."

        fs_index = {
            'line_items': {
                'gross_profit': {'group_current': 502100.0},
                'revenue': {'group_current': 3252000.0},
            }
        }

        issues = detect_rounded_derivation(report, fs_index)
        # Should not flag if the difference is tiny
        assert len(issues) == 0

    def test_rounded_derivation_operating_margin(self):
        """Test detection for operating margin."""
        detect_rounded_derivation = validate_report.detect_rounded_derivation

        report = "Operating margin of 8.5% reflected improved efficiency."

        fs_index = {
            'line_items': {
                'operating_profit': {'group_current': 276500.0},
                'revenue': {'group_current': 3252000.0},
            }
        }

        # operating_profit / revenue = 276500/3252000 = 8.5%
        # rounded: 276.5 / 3252.0 = 8.5% -- should match
        issues = detect_rounded_derivation(report, fs_index)
        assert len(issues) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# NEW TESTS: Tone validation
# ═══════════════════════════════════════════════════════════════════════════════

class TestToneValidation:
    """Tests for aggressive language detection."""

    def test_professional_language_passes(self):
        """Test that professional language passes tone check."""
        validate_tone = validate_report.validate_tone

        report = "Revenue showed strong growth of 58% YoY."
        issues = validate_tone(report)
        assert len(issues) == 0

    def test_aggressive_language_detected(self):
        """Test that aggressive language is detected."""
        validate_tone = validate_report.validate_tone

        report = "Revenue skyrocketed to new highs, while costs collapsed."
        issues = validate_tone(report)
        assert len(issues) >= 2
        descriptions = [i[1] for i in issues]
        assert any('skyrocketed' in d for d in descriptions)
        assert any('collapsed' in d for d in descriptions)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW TESTS: Calculation validation
# ═══════════════════════════════════════════════════════════════════════════════

class TestCalculationValidation:
    """Tests for YoY calculation validation."""

    def test_correct_yoy_calculation(self):
        """Test that correct YoY calculations pass."""
        validate_calculations = validate_report.validate_calculations

        # (3252 - 2057) / 2057 * 100 = 58.08% ~= 58.1%
        report = """
| Revenue | 3,252 | 2,057 | +58.1% |
"""
        issues = validate_calculations(report)
        assert len(issues) == 0

    def test_incorrect_yoy_calculation(self):
        """Test that incorrect YoY calculations are caught."""
        validate_calculations = validate_report.validate_calculations

        report = """
| Revenue | 3,252 | 2,057 | +70.0% |
"""
        issues = validate_calculations(report)
        assert len(issues) >= 1
        assert '58.1' in issues[0][2] or '58' in issues[0][2]


# ═══════════════════════════════════════════════════════════════════════════════
# NEW TESTS: Full validate_report() integration
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidateReportIntegration:
    """Integration tests for the full validate_report() function."""

    def test_clean_report_passes(self, tmp_path):
        """Test that a clean report with correct data passes."""
        validate_report_fn = validate_report.validate_report

        report_file = tmp_path / "report.md"
        report_file.write_text("""
# Financial Analysis

| Metric | FY2024 | FY2023 | YoY |
|---|---:|---:|---:|
| Revenue | 3,252 | 2,057 | +58.1% |
| PBT | 276 | 189 | +45.9% |

Gross margin was 15.4% for the year.
Revenue grew 58% year-on-year.
""")

        fs_index_file = tmp_path / "fs_index.json"
        fs_index_file.write_text(json.dumps({
            'line_items': {
                'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
                'pbt': {'group_current': 276000.0, 'group_prior': 189000.0},
                'gross_profit': {'group_current': 502100.0, 'group_prior': 380200.0},
            }
        }))

        result = validate_report_fn(report_file, fs_index_file)
        assert result['passed'] is True
        assert result['summary']['verified'] >= 2

    def test_report_with_mismatch_fails(self, tmp_path):
        """Test that a report with wrong data fails."""
        validate_report_fn = validate_report.validate_report

        report_file = tmp_path / "report.md"
        report_file.write_text("""
| Metric | FY2024 | FY2023 |
|---|---:|---:|
| Revenue | 4,000 | 2,500 |
""")

        fs_index_file = tmp_path / "fs_index.json"
        fs_index_file.write_text(json.dumps({
            'line_items': {
                'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
            }
        }))

        result = validate_report_fn(report_file, fs_index_file)
        assert result['passed'] is False
        assert result['summary']['mismatch'] >= 1

    def test_report_with_tone_issue_still_passes(self, tmp_path):
        """Test that tone issues don't cause failure (data is correct)."""
        validate_report_fn = validate_report.validate_report

        report_file = tmp_path / "report.md"
        report_file.write_text("""
| Revenue | 3,252 | 2,057 |
Revenue skyrocketed to new highs.
""")

        fs_index_file = tmp_path / "fs_index.json"
        fs_index_file.write_text(json.dumps({
            'line_items': {
                'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
            }
        }))

        result = validate_report_fn(report_file, fs_index_file)
        assert result['passed'] is True
        # Should have TONE issue
        tone_issues = [i for i in result['issues'] if i['type'] == 'TONE']
        assert len(tone_issues) >= 1

    def test_output_format_structure(self, tmp_path):
        """Test that output format matches the expected schema."""
        validate_report_fn = validate_report.validate_report

        report_file = tmp_path / "report.md"
        report_file.write_text("""
| Revenue | 3,252 | 2,057 | +58.1% |
Customer concentration at 35% remains a key risk.
Revenue skyrocketed.
""")

        fs_index_file = tmp_path / "fs_index.json"
        fs_index_file.write_text(json.dumps({
            'line_items': {
                'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
            }
        }))

        result = validate_report_fn(report_file, fs_index_file)

        # Check top-level structure
        assert 'passed' in result
        assert 'issues' in result
        assert 'summary' in result

        # Check summary structure
        assert 'verified' in result['summary']
        assert 'mismatch' in result['summary']
        assert 'unverifiable' in result['summary']
        assert 'calculations' in result['summary']

        # Check issue structure
        for issue in result['issues']:
            assert 'line' in issue
            assert 'type' in issue
            assert 'description' in issue
            assert 'detail' in issue
            assert issue['type'] in ('MISMATCH', 'UNVERIFIABLE', 'ROUNDED_DERIVATION', 'TONE')

    def test_unverifiable_with_mismatch(self, tmp_path):
        """Test report with both mismatch and unverifiable issues."""
        validate_report_fn = validate_report.validate_report

        report_file = tmp_path / "report.md"
        report_file.write_text("""
| Revenue | 4,000 | 2,500 | +60.0% |
Customer concentration at 35% remains a risk.
""")

        fs_index_file = tmp_path / "fs_index.json"
        fs_index_file.write_text(json.dumps({
            'line_items': {
                'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
            }
        }))

        result = validate_report_fn(report_file, fs_index_file)
        assert result['passed'] is False  # Mismatch causes failure
        assert result['summary']['mismatch'] >= 1

        # Check issue types present
        issue_types = {i['type'] for i in result['issues']}
        assert 'MISMATCH' in issue_types
        assert 'UNVERIFIABLE' in issue_types

    def test_calculations_counted_in_summary(self, tmp_path):
        """Test that calculation checks are counted in summary."""
        validate_report_fn = validate_report.validate_report

        report_file = tmp_path / "report.md"
        report_file.write_text("""
| Revenue | 3,252 | 2,057 | +58.1% |
| PBT | 276 | 189 | +45.9% |
| Total Assets | 5,500 | 4,800 | +14.6% |
""")

        fs_index_file = tmp_path / "fs_index.json"
        fs_index_file.write_text(json.dumps({
            'line_items': {
                'revenue': {'group_current': 3252000.0, 'group_prior': 2057000.0},
                'pbt': {'group_current': 276000.0, 'group_prior': 189000.0},
                'total_assets': {'group_current': 5500000.0, 'group_prior': 4800000.0},
            }
        }))

        result = validate_report_fn(report_file, fs_index_file)
        assert result['summary']['calculations'] == 3


# ═══════════════════════════════════════════════════════════════════════════════
# NEW TESTS: Helper functions
# ═══════════════════════════════════════════════════════════════════════════════

class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_is_skip_context_years(self):
        """Test _is_skip_context with year patterns."""
        _is_skip_context = validate_report._is_skip_context
        assert _is_skip_context("FY2024 revenue was strong")
        assert _is_skip_context("In 2023, the company...")
        assert not _is_skip_context("Margin of 15.4%")

    def test_is_skip_context_dates(self):
        """Test _is_skip_context with date patterns."""
        _is_skip_context = validate_report._is_skip_context
        assert _is_skip_context("As at 31/12/2024")
        assert _is_skip_context("For the year ended 31-12-2024")

    def test_try_verify_claim_direct_match(self):
        """Test _try_verify_claim with a direct line item match."""
        _try_verify_claim = validate_report._try_verify_claim

        fs_index = {
            'line_items': {
                'revenue': {'group_current': 3252000.0},
            }
        }

        # 3252 in millions should match revenue
        assert _try_verify_claim(3252.0, "Revenue", fs_index) is True

    def test_try_verify_claim_no_match(self):
        """Test _try_verify_claim with no matching data."""
        _try_verify_claim = validate_report._try_verify_claim

        fs_index = {
            'line_items': {
                'revenue': {'group_current': 3252000.0},
            }
        }

        # 35% can't be derived from revenue alone
        assert _try_verify_claim(35.0, "concentration at 35%", fs_index) is False
