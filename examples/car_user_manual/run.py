from fastpdf4llm import to_markdown
from fastpdf4llm.models.parse_options import ParseOptions


files = [
    "tesla_model3_user_manual.pdf"
]

for file in files:
    print(f"Converting {file}...")
    markdown_content = to_markdown(file, image_dir="./parsed_images")

    with open(f"{file}.md", "w") as f:
        f.write(markdown_content)
    print(f"Converting {file} done...")
