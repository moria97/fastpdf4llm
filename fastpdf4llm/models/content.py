from typing import Literal, Optional, Tuple

from pydantic import BaseModel


class ContentBlock(BaseModel):
    type: Literal["text", "table", "image"]
    text: Optional[str] = None
    text_level: Optional[int] = None
    page: Optional[int] = None
    bbox: Optional[Tuple[float, float, float, float]] = None
