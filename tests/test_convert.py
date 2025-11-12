"""Tests for PDF to Markdown conversion functionality."""

import os
import tempfile
from pathlib import Path

import pytest

from fastpdf4llm import ProgressInfo, to_markdown
from fastpdf4llm.models.progress import ProcessPhase


@pytest.fixture
def pdf_path():
    """Return the path to the test PDF file."""
    # Get the project root directory (parent of tests directory)
    project_root = Path(__file__).parent.parent
    pdf_file = project_root / "examples" / "convert_table" / "national-capitals.pdf"

    if not pdf_file.exists():
        pytest.skip(f"Test PDF file not found: {pdf_file}")

    return str(pdf_file)


@pytest.fixture
def temp_image_dir():
    """Create a temporary directory for images."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_basic_conversion(pdf_path):
    """Test basic PDF to Markdown conversion."""
    result = to_markdown(pdf_path)

    # Check that result is not empty
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_conversion_with_image_dir(pdf_path, temp_image_dir):
    """Test conversion with custom image directory."""
    result = to_markdown(pdf_path, image_dir=temp_image_dir)

    # Check that result is not empty
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0

    # Check that image directory exists
    assert os.path.exists(temp_image_dir)


def test_conversion_contains_content(pdf_path):
    """Test that converted markdown contains expected content."""
    result = to_markdown(pdf_path)

    # Check for basic markdown structure
    assert len(result) > 100, "Output should contain substantial content"

    # Check for common markdown elements (may or may not be present)
    # This is a flexible test that just ensures we got some content


def test_progress_callback(pdf_path):
    """Test that progress callback is called during conversion."""
    progress_calls = []

    def progress_callback(progress: ProgressInfo):
        progress_calls.append(progress)
        # Verify progress info structure
        assert isinstance(progress.phase, ProcessPhase)
        assert isinstance(progress.current_page, int)
        assert isinstance(progress.total_pages, int)
        assert isinstance(progress.percentage, float)
        assert isinstance(progress.message, str)
        assert 0 <= progress.percentage <= 100
        assert progress.current_page >= 0
        assert progress.total_pages > 0

    result = to_markdown(pdf_path, progress_callback=progress_callback)

    # Verify that callback was called at least once
    assert len(progress_calls) > 0, "Progress callback should be called at least once"

    # Verify that we got progress for both phases
    phases = [call.phase for call in progress_calls]
    assert ProcessPhase.ANALYSIS in phases, "Should have analysis phase progress"
    assert ProcessPhase.CONVERSION in phases, "Should have conversion phase progress"

    # Verify progress percentages are in correct range
    for progress in progress_calls:
        if progress.phase == ProcessPhase.ANALYSIS:
            assert 0 <= progress.percentage <= 70, "Analysis phase should be 0-70%"
        elif progress.phase == ProcessPhase.CONVERSION:
            assert 70 <= progress.percentage <= 100, "Conversion phase should be 70-100%"


def test_progress_callback_ordering(pdf_path):
    """Test that progress callbacks are called in correct order."""
    progress_calls = []

    def progress_callback(progress: ProgressInfo):
        progress_calls.append(progress)

    result = to_markdown(pdf_path, progress_callback=progress_callback)

    # Verify that analysis phase comes before conversion phase
    if len(progress_calls) > 1:
        analysis_indices = [i for i, p in enumerate(progress_calls) if p.phase == ProcessPhase.ANALYSIS]
        conversion_indices = [i for i, p in enumerate(progress_calls) if p.phase == ProcessPhase.CONVERSION]

        if analysis_indices and conversion_indices:
            max_analysis_idx = max(analysis_indices)
            min_conversion_idx = min(conversion_indices)
            assert max_analysis_idx < min_conversion_idx, "Analysis should complete before conversion"


def test_invalid_pdf_path():
    """Test that invalid PDF path raises appropriate error."""
    with pytest.raises((FileNotFoundError, OSError, Exception)):
        to_markdown("nonexistent_file.pdf")


def test_conversion_result_type(pdf_path):
    """Test that conversion returns a string."""
    result = to_markdown(pdf_path)
    assert isinstance(result, str)


def test_empty_progress_callback(pdf_path):
    """Test that conversion works with None progress callback."""
    result = to_markdown(pdf_path, progress_callback=None)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
