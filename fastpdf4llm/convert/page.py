import hashlib
import os
import re
from io import BytesIO
from typing import Dict, List, Optional

from loguru import logger
from pdfplumber.page import Page
from pdfplumber.table import Table

from fastpdf4llm.models.constants import DEFAULT_IMAGE_SAVE_DIR
from fastpdf4llm.models.content import Content
from fastpdf4llm.models.line import Line, LineType
from fastpdf4llm.utils.font import is_bold_font, round_font_size
from fastpdf4llm.utils.table_utils import is_table_empty, table_to_markdown


class PageConverter:
    def __init__(
        self,
        page: Page,
        size_to_level: Dict[float, str],
        normal_text_size: float,
        image_dir: Optional[str] = None,
    ):
        self.page = page
        self.size_to_level = size_to_level
        self.normal_text_size = normal_text_size
        self.image_dir = image_dir or DEFAULT_IMAGE_SAVE_DIR
        self.text_content_area = self.page
        os.makedirs(self.image_dir, exist_ok=True)

    def _is_valid_table(self, table: Table) -> bool:
        """Check if table bounds are within page bounds."""
        page_bbox = self.page.bbox
        table_bbox = table.bbox

        return (
            table_bbox[0] >= 0
            and table_bbox[1] >= 0
            and table_bbox[2] <= page_bbox[2]
            and table_bbox[3] <= page_bbox[3]
        )

    def extract_contents(self) -> List[Content]:
        contents: List[Content] = []
        tables = self.page.dedupe_chars().find_tables()
        valid_tables = [table for table in tables if self._is_valid_table(table)]

        media_contents = []
        # Extract non-table content
        for table in valid_tables:
            if is_table_empty(table):
                continue

            try:
                self.text_content_area = self.text_content_area.outside_bbox(table.bbox)
            except ValueError:
                logger.warning(f"Table {table.bbox} is not within the text content area.")
                continue

            word = {
                "text": table_to_markdown(table),
                "x0": table.bbox[0],
                "x1": table.bbox[2],
                "top": table.bbox[1],
                "bottom": table.bbox[3],
                "fontname": "",
                "size": self.normal_text_size,
            }
            logger.info(f"Table to markdown: {word['text']}")

            media_contents.append(
                Content(
                    lines=[
                        Line(
                            words=[word],
                            left=table.bbox[0],
                            right=table.bbox[2],
                            top=table.bbox[1],
                            bottom=table.bbox[3],
                            type=LineType.TABLE,
                        )
                    ],
                    left=table.bbox[0],
                    right=table.bbox[2],
                    top=table.bbox[1],
                    bottom=table.bbox[3],
                )
            )

        for image in self.page.images:
            image_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])

            try:
                # 按照固定尺寸剪切出来，直接使用“stream”的bytes会加载报错 https://github.com/jsvine/pdfplumber/discussions/496
                image_page = self.page.crop(image_bbox)
                img_obj = image_page.to_image(width=image["width"])
                image_bytes_io = BytesIO()
                img_obj.save(image_bytes_io, format="PNG")
                image_bytes = image_bytes_io.getvalue()

                # 写入文件
                image_md5 = hashlib.md5(image_bytes).hexdigest()
                image_path = os.path.join(self.image_dir, f"{image_md5}.png")
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                    logger.info(f"Save image to {image_path} successfully.")

                word = {
                    "text": f"![]({image_path})\n\n",
                    "x0": image["x0"],
                    "x1": image["x1"],
                    "top": image["top"],
                    "bottom": image["bottom"],
                    "fontname": "",
                    "size": self.normal_text_size,
                }

                media_contents.append(
                    Content(
                        lines=[
                            Line(
                                words=[word],
                                left=image["x0"],
                                right=image["x1"],
                                top=image["top"],
                                bottom=image["bottom"],
                                type=LineType.IMAGE,
                            )
                        ],
                        left=image["x0"],
                        right=image["x1"],
                        top=image["top"],
                        bottom=image["bottom"],
                    )
                )

            except Exception as ex:
                logger.warning(f"Parse image failed: {ex}")
                continue

            try:
                self.text_content_area = self.text_content_area.outside_bbox(image_bbox)
            except ValueError as ex:
                logger.warning(f"Image is not within the text content area. {ex}")
                continue

        # Process text content with font information
        cur_line = None
        for word in self.text_content_area.dedupe_chars().extract_words(extra_attrs=["size", "fontname"]):
            if cur_line and cur_line.should_merge(word["x0"], word["x1"], word["top"], word["bottom"]):
                cur_line.merge(word)
            else:
                if cur_line:
                    for sub_line in cur_line.split():
                        if contents and contents[-1].should_add(sub_line):
                            contents[-1].add_line(sub_line)
                        else:
                            contents.append(
                                Content(
                                    lines=[sub_line],
                                    left=cur_line.left,
                                    right=cur_line.right,
                                    top=cur_line.top,
                                    bottom=cur_line.bottom,
                                )
                            )

                rounded_size = round_font_size(word["size"])
                level = "" if rounded_size == self.normal_text_size else self.size_to_level.get(rounded_size, "")

                cur_line = Line(
                    words=[word],
                    left=word["x0"],
                    right=word["x1"],
                    top=word["top"],
                    bottom=word["bottom"],
                    level=level,
                    type=LineType.TEXT,
                )

        if contents and contents[-1].should_add(cur_line):
            contents[-1].add_line(cur_line)
        else:
            contents.append(
                Content(
                    lines=[cur_line], left=cur_line.left, right=cur_line.right, top=cur_line.top, bottom=cur_line.bottom
                )
            )

        contents.extend(media_contents)
        contents = sorted(contents)
        final_contents = []
        visited = [False] * len(contents)
        for i in range(len(contents)):
            if visited[i]:
                continue

            content = contents[i]
            new_merged = True
            while new_merged:
                new_merged = False
                for j in range(i + 1, len(contents)):
                    if visited[j]:
                        continue
                    if content.should_merge(contents[j]):
                        content.merge(contents[j])
                        visited[j] = True
                        new_merged = True

            final_contents.append(content)
            visited[i] = True

        final_contents = sorted(final_contents)

        return final_contents

    def should_break_line(self, text: str) -> bool:
        if re.search(r"[:：.?!。？！….]\s*$", text) and not re.search(r"\d\.$", text):
            return True

        return False

    # Process text with mixed styles
    def to_markdown(self) -> str:
        contents = self.extract_contents()

        md_content = ""
        for content in contents:
            content_markdown = ""
            last_line_end = -1
            for line in content.lines:
                if line.type == LineType.TEXT:
                    if not line.words:
                        continue
                    line_markdown = ""
                    last_is_bold = is_bold_font(line.words[0]["fontname"])
                    current_bbox = (
                        line.words[0]["x0"],
                        line.words[0]["top"],
                        line.words[0]["x1"],
                        line.words[0]["bottom"],
                    )
                    for word in line.words[1:]:
                        word_is_bold = is_bold_font(word["fontname"])
                        word_bbox = (word["x0"], word["top"], word["x1"], word["bottom"])

                        if word_is_bold != last_is_bold:
                            try:
                                span_text = (
                                    self.text_content_area.within_bbox(current_bbox).dedupe_chars().extract_text().strip()
                                )
                            except Exception as ex:
                                logger.warning(f"Failed to find span {current_bbox}, processing word {word}")
                                continue
                            
                            if last_is_bold:
                                line_markdown += f"**{span_text}**"
                            else:
                                line_markdown += span_text
                            current_bbox = word_bbox
                            last_is_bold = word_is_bold
                        else:
                            current_bbox = (
                                min(current_bbox[0], word_bbox[0]),
                                min(current_bbox[1], word_bbox[1]),
                                max(current_bbox[2], word_bbox[2]),
                                max(current_bbox[3], word_bbox[3]),
                            )

                    try:
                        span_text = (
                            self.text_content_area.within_bbox(current_bbox).dedupe_chars().extract_text().strip()
                        )
                    except Exception as ex:
                        logger.error(f"Failed to find span {current_bbox}.")
                        continue

                    if last_is_bold:
                        line_markdown += f"**{span_text}**"
                    else:
                        line_markdown += span_text

                    if line.right < last_line_end * 0.9 or line.level:
                        should_break_line = True
                    else:
                        should_break_line = self.should_break_line(span_text)

                    if should_break_line:
                        line_markdown += "\n"

                    last_line_end = max(last_line_end, line.right)

                    if line.level:
                        line_markdown = f"{line.level} {line_markdown}"
                else:
                    line_markdown = "\n" + line.words[0]["text"]

                if line_markdown:
                    content_markdown += line_markdown + "\n"

            if content_markdown:
                md_content += content_markdown + "\n\n"

        return md_content
