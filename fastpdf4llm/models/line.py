import re
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from fastpdf4llm.models.constants import MAX_WIDTH_GAP_SIZE
from fastpdf4llm.utils.font import is_bold_font


class LineType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"


def is_hierarchical_number(s: str) -> bool:
    """
    Returns True if `s` is a hierarchical number like:
      '1', '1.', '1.1', '2.10.3', '1.2.3.', ' 3.4.5 ' (whitespace allowed)

    Rules:
      - Only digits and dots
      - Starts and ends with digit (ignoring surrounding whitespace)
      - No leading zeros (e.g., '01.2' → False, but '1.02' → False)
      - At least one digit; dots only as separators
    """
    # Strip surrounding whitespace
    s = s.strip()
    if not s:
        return False

    # Regex explanation:
    # ^              : start of string
    # \d+            : one or more digits (no leading zero unless single '0')
    # (?:\.\d+)*     : zero or more occurrences of: dot + digits (again, no leading zero)
    # $              : end of string
    # BUT: allow trailing dot (common in titles: "1.", "2.1.")
    # So optionally allow a trailing dot after the last digit group
    pattern = r"^\d+(?:\.\d+)*(?:\.)?$"

    if not re.match(pattern, s):
        return False

    return True


class Line(BaseModel):
    words: List[Dict[str, Any]]
    left: float
    right: float
    top: float
    bottom: float
    level: Optional[str] = None
    type: LineType = LineType.TEXT

    def should_merge(self, left: float, right: float, top: float, bottom: float) -> bool:
        # 同一行
        if abs(self.top - top) > 3:
            return False

        return True

    def merge(self, word: Dict[str, Any]):
        self.left = min(self.left, word["x0"])
        self.right = max(self.right, word["x1"])
        self.top = min(self.top, word["top"])
        self.bottom = max(self.bottom, word["bottom"])

        if not self.words:
            self.words = [word]
        else:
            # 距离接近且字体相同，直接合并
            if is_bold_font(word["fontname"]) == is_bold_font(self.words[-1]["fontname"]) and word["x0"] - self.words[-1]["x1"] < MAX_WIDTH_GAP_SIZE:
                self.words[-1]["top"] = min(self.words[-1]["top"], word["top"])
                self.words[-1]["bottom"] = max(self.words[-1]["bottom"], word["bottom"])
                self.words[-1]["x0"] = min(self.words[-1]["x0"], word["x0"])
                self.words[-1]["x1"] = max(self.words[-1]["x1"], word["x1"])
                self.words[-1]["text"] += "++" + word["text"]
            else:
                self.words.append(word)
    
    def split(self) -> List["Line"]:
        if len(self.words) >= 4 or len(self.words) <= 1:
            return [self]

        if len(self.words) <= 3 and is_hierarchical_number(self.words[0]["text"]):
            return [self]

        # 2 列或者3列的情况，拆分
        return [
            Line(
                words=[word],
                left=word["x0"],
                right=word["x1"],
                top=word["top"],
                bottom=word["bottom"],
                level=self.level,
                type=self.type,
            ) for word in self.words
        ]
