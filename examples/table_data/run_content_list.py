"""
Example: Convert PDF to content list and annotate PDF with bounding boxes.

This example demonstrates:
1. Using to_content_list to extract structured content from PDF
2. Saving content list as JSON
3. Using pypdfium2 to annotate the PDF with bounding boxes based on content_list

Note: pypdfium2's annotation API is limited. This example uses a workaround by:
- Rendering each page to an image
- Drawing bounding boxes on the image using PIL
- Creating a new PDF from the annotated images
"""

import json
from pathlib import Path

try:
    import pypdfium2 as pdfium
    from PIL import ImageDraw
except ImportError as e:
    print(f"Required packages not installed: {e}")
    print("Please install them with: pip install pypdfium2 pillow")
    raise

from fastpdf4llm import to_content_list


def annotate_pdf_with_content_list(pdf_path: str, content_list: list, output_path: str):
    """
    Annotate PDF with bounding boxes from content_list.

    This function renders each PDF page to an image, draws bounding boxes,
    and creates a new PDF from the annotated images.

    Args:
        pdf_path: Path to input PDF
        content_list: List of ContentBlock objects (or dicts)
        output_path: Path to save annotated PDF
    """
    # Open the PDF
    pdf = pdfium.PdfDocument(pdf_path)

    # Group content blocks by page
    pages_content = {}
    for block in content_list:
        # Handle both dict and ContentBlock objects
        if isinstance(block, dict):
            page = block.get("page")
            bbox = block.get("bbox")
        else:
            page = block.page
            bbox = block.bbox

        if page is not None and bbox is not None:
            page_num = page - 1  # Convert to 0-based indexing
            if page_num not in pages_content:
                pages_content[page_num] = []
            pages_content[page_num].append(block)

    # Process each page
    annotated_images = []

    for page_num in range(len(pdf)):
        page = pdf[page_num]

        # Render page to image (scale factor for better quality)
        scale = 2.0  # Higher scale = better quality but larger file
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()

        # Create a drawing context
        draw = ImageDraw.Draw(pil_image)

        # Draw bounding boxes for content blocks on this page
        if page_num in pages_content:
            for block in pages_content[page_num]:
                # Extract bbox
                if isinstance(block, dict):
                    bbox = block.get("bbox")
                    block_type = block.get("type", "text")
                else:
                    bbox = block.bbox
                    block_type = block.type if hasattr(block, "type") else "text"

                if bbox is None:
                    continue

                x0, y0, x1, y1 = bbox

                # Scale coordinates to match rendered image
                x0_scaled = x0 * scale
                y0_scaled = y0 * scale
                x1_scaled = x1 * scale
                y1_scaled = y1 * scale

                # pdfplumber uses top-left origin, PIL also uses top-left
                # So no coordinate flipping needed

                # Choose color based on content type
                if block_type == "table":
                    color = "red"
                    width_line = 3
                elif block_type == "image":
                    color = "blue"
                    width_line = 3
                else:  # text
                    color = "green"
                    width_line = 2

                # Draw rectangle
                draw.rectangle([(x0_scaled, y0_scaled), (x1_scaled, y1_scaled)], outline=color, width=width_line)

        annotated_images.append(pil_image)

    # Create a new PDF from annotated images
    if annotated_images:
        # Save first image as PDF, then append others
        annotated_images[0].save(
            output_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=annotated_images[1:] if len(annotated_images) > 1 else [],
        )

    pdf.close()
    print(f"Annotated PDF saved to {output_path}")


def main():
    """Main function to run the example."""
    # Paths
    script_dir = Path(__file__).parent
    pdf_path = script_dir / "national-capitals.pdf"
    json_path = script_dir / "content_list.json"
    annotated_pdf_path = script_dir / "national-capitals-annotated.pdf"

    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return

    print(f"Processing PDF: {pdf_path}")

    # Step 1: Convert PDF to content list
    print("Converting PDF to content list...")
    content_list = to_content_list(str(pdf_path), extract_images=True)

    print(f"Extracted {len(content_list)} content blocks")

    # Step 2: Save content list as JSON
    print(f"Saving content list to {json_path}...")
    # Convert Pydantic models to dict for JSON serialization
    content_dicts = [block.model_dump() for block in content_list]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(content_dicts, f, indent=2, ensure_ascii=False)

    print(f"Content list saved to {json_path}")

    # Step 3: Annotate PDF with bounding boxes
    print("Annotating PDF with bounding boxes...")
    try:
        annotate_pdf_with_content_list(str(pdf_path), content_list, str(annotated_pdf_path))
        print(f"Annotated PDF saved to {annotated_pdf_path}")
    except Exception as e:
        print(f"Error annotating PDF: {e}")
        print("Note: PDF annotation requires pypdfium2 with proper setup")


if __name__ == "__main__":
    main()
