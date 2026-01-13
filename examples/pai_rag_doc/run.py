from fastpdf4llm import to_markdown

files = ["大模型RAG对话系统.pdf"]

for file in files:
    print(f"Converting {file}...")
    markdown_content = to_markdown(file, image_dir="./parsed_images")

    with open(f"{file}.md", "w") as f:
        f.write(markdown_content)
    print(f"Converting {file} done...")
