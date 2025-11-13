from fastpdf4llm import to_markdown



markdown_content = to_markdown("./national-capitals.pdf", image_dir="./parsed_images")

with open("national-capitals.md", "w") as f:
    f.write(markdown_content)
