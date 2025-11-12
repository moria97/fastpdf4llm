# 🚀 fastpdf4llm: PDF to LLM-Ready Markdown in Seconds


[![CI](https://github.com/moria97/fastpdf4llm/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/moria97/fastpdf4llm/actions/workflows/ci.yml)


A fast and efficient PDF to Markdown converter optimized for LLM (Large Language Model) processing. This tool intelligently extracts text, tables, and images from PDF files and converts them into well-structured Markdown format.

## Features

- 🚀 **Fast Processing**: Efficient PDF parsing and conversion
- 📊 **Table Extraction**: Automatically detects and converts tables to Markdown format
- 🖼️ **Image Support**: Extracts and saves images from PDFs
- 📝 **Smart Formatting**: Intelligently identifies headings based on font sizes
- 📈 **Progress Tracking**: Built-in progress callback support
- 🎯 **LLM Optimized**: Output format optimized for LLM consumption
- 📜 **Free & Open Source**: MIT licensed, free to use for commercial and personal projects

## Installation

### Using Poetry (Recommended)

```bash
poetry add fastpdf4llm
```

### Using pip

```bash
pip install fastpdf4llm
```

## Quick Start

### Basic Usage

```python
from fastpdf4llm import to_markdown

# Convert PDF to Markdown
markdown_content = to_markdown("path/to/your/document.pdf")

# Save to file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)
```

### With Custom Image Directory

```python
from fastpdf4llm import to_markdown

# Specify custom directory for extracted images
markdown_content = to_markdown(
    "path/to/your/document.pdf",
    image_dir="./images"
)
```

### With Progress Callback

```python
from fastpdf4llm import to_markdown, ProgressInfo

def progress_callback(progress: ProgressInfo):
    print(f"{progress.phase.value}: {progress.current_page}/{progress.total_pages} "
          f"({progress.percentage:.1f}%) - {progress.message}")

markdown_content = to_markdown(
    "path/to/your/document.pdf",
    progress_callback=progress_callback
)
```

## API Reference

### `to_markdown`

Convert a PDF file to Markdown format.

**Parameters:**

- `pdf_path` (str): Path to the PDF file to convert
- `image_dir` (Optional[str]): Directory to save extracted images. Defaults to `./tmp/images/`
- `progress_callback` (Optional[Callable[[ProgressInfo], None]]): Callback function for progress updates

**Returns:**

- `str`: Markdown content of the PDF

**Example:**

```python
from fastpdf4llm import to_markdown, ProgressInfo
from typing import Callable

def on_progress(progress: ProgressInfo):
    print(f"Progress: {progress.percentage:.1f}%")

content = to_markdown(
    pdf_path="document.pdf",
    image_dir="./output_images",
    progress_callback=on_progress
)
```

### `ProgressInfo`

Progress information model for tracking conversion progress.

**Attributes:**

- `phase` (ProcessPhase): Current processing phase (`ANALYSIS` or `CONVERSION`)
- `current_page` (int): Current page being processed
- `total_pages` (int): Total number of pages in the PDF
- `percentage` (float): Overall progress percentage (0-100)
- `message` (str): Status message

## How It Works

1. **Analysis Phase**: Analyzes the PDF to identify font sizes and determine heading hierarchy
2. **Conversion Phase**: Extracts text, tables, and images, converting them to Markdown format
3. **Smart Formatting**: Automatically detects headings based on font size analysis
4. **Table Detection**: Identifies and converts tables to Markdown table format
5. **Image Extraction**: Extracts images and saves them to the specified directory

## Examples

See the `examples/` directory for more usage examples:

- `convert_financial_report/`: Converting financial reports with tables and images
- `convert_table/`: Converting PDFs with complex tables

## Requirements

- Python >= 3.9
- pdfplumber >= 0.11.3
- loguru >= 0.7.0
- pydantic >= 2.0.0

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/moria97/fastpdf4llm.git
cd fastpdf4llm

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .
```

## Acknowledgements

This project is inspired by the [pdf2markdown4llm](https://github.com/HawkClaws/pdf2markdown4llm/tree/main) project by HawkClaws. We appreciate their work on PDF to Markdown conversion for LLM applications.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Yue Fei - [feiyue297@qq.com](mailto:feiyue297@qq.com)

## Repository

[https://github.com/moria97/fastpdf4llm](https://github.com/moria97/fastpdf4llm)

