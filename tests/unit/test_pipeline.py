# tests/unit/test_pipeline.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.finanalysis.pipeline import Pipeline
from src.finanalysis.config import Settings


@pytest.fixture
def settings():
    """Test settings"""
    return Settings(
        openai_api_key="test-key",
        llm_model="qwen3.5-flash",
        cache_enabled=False,
        output_dir="./test_output"
    )


@pytest.fixture
def test_pdf(tmp_path):
    """Create a minimal test PDF path"""
    return "testdata/CHINHIN_Annual_Report_2024.pdf"


def test_pipeline_initialization(settings):
    """Test Pipeline initialization"""
    pipeline = Pipeline(settings=settings)
    assert pipeline.settings == settings


def test_pipeline_rejects_nonexistent_pdf(settings):
    """Test Pipeline rejects nonexistent PDF"""
    pipeline = Pipeline(settings=settings)

    with pytest.raises(FileNotFoundError):
        pipeline.run(pdf_path="nonexistent.pdf")


def test_pipeline_rejects_directory(settings, tmp_path):
    """Test Pipeline rejects directory path"""
    pipeline = Pipeline(settings=settings)

    with pytest.raises(ValueError, match="Not a file"):
        pipeline.run(pdf_path=str(tmp_path))


@patch('src.finanalysis.pipeline.Stage1Preprocessor')
@patch('src.finanalysis.pipeline.Stage2TextExtractor')
@patch('src.finanalysis.pipeline.Stage3TableExtractor')
@patch('src.finanalysis.pipeline.FSIndex')
@patch('src.finanalysis.pipeline.Stage5Aggregator')
def test_pipeline_runs_all_stages(
    mock_stage5_class,
    mock_fsindex_class,
    mock_stage3_class,
    mock_stage2_class,
    mock_stage1_class,
    settings,
    test_pdf,
    tmp_path
):
    """Test Pipeline runs all stages"""
    # Mock all stages
    mock_stage1 = MagicMock()
    mock_stage1.process.return_value = (Mock(), [Mock()])
    mock_stage1_class.return_value = mock_stage1

    mock_stage2 = MagicMock()
    mock_stage2.process.return_value = ([Mock()], [Mock()])
    mock_stage2_class.return_value = mock_stage2

    mock_stage3 = MagicMock()
    mock_stage3.process.return_value = ([Mock()], [Mock()])
    mock_stage3_class.return_value = mock_stage3

    mock_fsindex = MagicMock()
    mock_fsindex.line_items = {}
    mock_fsindex_class.from_pdf.return_value = mock_fsindex

    mock_stage5 = MagicMock()
    mock_stage5.process.return_value = {"status": "success", "statistics": {"metrics": 0}}
    mock_stage5_class.return_value = mock_stage5

    # Run pipeline
    pipeline = Pipeline(settings=settings)
    result = pipeline.run(pdf_path=test_pdf, output_dir=str(tmp_path))

    # Verify all stages called
    assert mock_stage1.process.called
    assert mock_stage2.process.called
    assert mock_stage3.process.called
    assert mock_fsindex_class.from_pdf.called
    assert mock_stage5.process.called

    # Verify result
    assert result["status"] == "success"


@patch('src.finanalysis.pipeline.Stage1Preprocessor')
@patch('src.finanalysis.pipeline.Stage2TextExtractor')
@patch('src.finanalysis.pipeline.Stage3TableExtractor')
@patch('src.finanalysis.pipeline.FSIndex')
@patch('src.finanalysis.pipeline.Stage5Aggregator')
def test_pipeline_stop_at_stage(
    mock_stage5_class,
    mock_fsindex_class,
    mock_stage3_class,
    mock_stage2_class,
    mock_stage1_class,
    settings,
    test_pdf,
    tmp_path
):
    """Test Pipeline can stop at specific stage"""
    mock_stage1 = MagicMock()
    mock_stage1.process.return_value = (Mock(), [Mock()])
    mock_stage1_class.return_value = mock_stage1

    pipeline = Pipeline(settings=settings)
    result = pipeline.run(
        pdf_path=test_pdf,
        output_dir=str(tmp_path),
        stop_at_stage=1
    )

    assert mock_stage1.process.called
    assert result["status"] == "stopped"
    assert result["stage"] == 1


def test_pipeline_force_disables_cache(settings, test_pdf, tmp_path):
    """Test Pipeline force flag disables cache"""
    settings.cache_enabled = True

    with patch('src.finanalysis.pipeline.Stage1Preprocessor') as mock_stage1_class:
        mock_stage1 = MagicMock()
        mock_stage1.process.return_value = (Mock(), [Mock()])
        mock_stage1_class.return_value = mock_stage1

        pipeline = Pipeline(settings=settings)

        pipeline.run(
            pdf_path=test_pdf,
            output_dir=str(tmp_path),
            force=True,
            stop_at_stage=1
        )

        assert settings.cache_enabled  # Should be restored after run
