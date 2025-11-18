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
    pdf_file = project_root / "tests" / "data" / "multi_modal_test_tesla.pdf"

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

    _ = to_markdown(pdf_path, progress_callback=progress_callback)

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

    _ = to_markdown(pdf_path, progress_callback=progress_callback)

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


def test_invalid_pdf_file_raises_error():
    """Test that an invalid/corrupted PDF file raises ValueError."""
    import tempfile

    # Create a temporary file that is not a valid PDF
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write("This is not a PDF file")
        tmp_path = tmp_file.name

    try:
        with pytest.raises(Exception) as exc_info:
            to_markdown(tmp_path)

        # Verify error message contains useful information
        error_msg = str(exc_info.value)
        assert (
            "Invalid PDF file" in error_msg
            or "not a valid PDF" in error_msg
            or "corrupted" in error_msg
            or "No /Root object! " in error_msg
        )
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_conversion_with_pathlib_path(pdf_path):
    """Test conversion with pathlib.Path object."""
    from pathlib import Path

    path_obj = Path(pdf_path)
    result = to_markdown(path_obj)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_conversion_with_file_object(pdf_path):
    """Test conversion with file object (BufferedReader)."""
    with open(pdf_path, "rb") as f:
        result = to_markdown(f)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_conversion_with_bytesio(pdf_path):
    """Test conversion with BytesIO object."""
    from io import BytesIO

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    bytes_io = BytesIO(pdf_bytes)
    result = to_markdown(bytes_io)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_conversion_with_parse_options(pdf_path):
    """Test conversion with custom ParseOptions."""
    from fastpdf4llm.models.parse_options import ParseOptions

    parse_options = ParseOptions(x_tolerance_ratio=0.25, y_tolerance=5)
    result = to_markdown(pdf_path, parse_options=parse_options)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_conversion_with_all_options(pdf_path, temp_image_dir):
    """Test conversion with all options combined."""
    from pathlib import Path

    from fastpdf4llm.models.parse_options import ParseOptions

    parse_options = ParseOptions(x_tolerance_ratio=0.15, y_tolerance=3)
    path_obj = Path(pdf_path)

    progress_calls = []

    def progress_callback(progress: ProgressInfo):
        progress_calls.append(progress)

    result = to_markdown(
        path_obj, image_dir=temp_image_dir, parse_options=parse_options, progress_callback=progress_callback
    )

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    assert len(progress_calls) > 0
    assert os.path.exists(temp_image_dir)


def test_no_image_mode(pdf_path):
    """Test conversion with image extraction disabled."""
    import re

    no_image_dir = "./tmp/no_images"

    result = to_markdown(pdf_path, extract_images=False, image_dir=no_image_dir)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0

    # Verify no image markdown syntax in output
    # Pattern matches: ![](url) or ![alt](url)
    image_pattern = r"!\[.*?\]\(.*?\)"
    matches = re.findall(image_pattern, result)
    assert len(matches) == 0, f"Found image markdown patterns in no-image mode: {matches}"

    assert not os.path.exists(no_image_dir), "Image directory should not be created when extract_images is False."


def test_image_mode_vs_no_image_mode(pdf_path, temp_image_dir):
    """Test that extract_images parameter affects image extraction."""
    no_image_dir = "./tmp/no_images"
    image_dir = "./tmp/images"

    # Test with images enabled
    result_with_images = to_markdown(pdf_path, extract_images=True, image_dir=image_dir)

    # Test with images disabled
    result_without_images = to_markdown(pdf_path, extract_images=False, image_dir=no_image_dir)

    # Both should produce markdown
    assert isinstance(result_with_images, str)
    assert isinstance(result_without_images, str)
    assert len(result_with_images) > 0
    assert len(result_without_images) > 0

    # When extract_images=False, markdown should not contain image references
    import re

    # Pattern matches: ![](url) or ![alt](url)
    image_pattern = r"!\[.*?\]\(.*?\)"

    images_with = re.findall(image_pattern, result_with_images)
    images_without = re.findall(image_pattern, result_without_images)

    # When extract_images=False, there should be no image markdown patterns
    assert len(images_without) == 0, f"Found image patterns in no-image mode: {images_without}"

    # If PDF has images, result_with_images should have more image patterns
    # (or at least the same, but typically more)
    assert len(images_with) == 3, "Image mode should have equal or more image patterns"

    assert not os.path.exists(no_image_dir), "Image directory should not be created when extract_images is False."
    assert os.path.exists(image_dir), "Image directory should be created when extract_images is True."
    assert len(os.listdir(image_dir)) == 3, "Image directory should contain images when extract_images is True."
