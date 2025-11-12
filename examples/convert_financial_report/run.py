from fastpdf4llm import to_markdown, ProgressInfo

def progress_callback(progress: ProgressInfo):
    print(f"{progress.phase.value}: {progress.current_page}/{progress.total_pages} "
          f"({progress.percentage:.1f}%) - {progress.message}")


markdown_content = to_markdown("./000001_2016_平安银行_2016年年度报告_2017-03-16.pdf", image_dir="./parsed_images", progress_callback=progress_callback)

with open("平安财报2016.md", "w") as f:
    f.write(markdown_content)
