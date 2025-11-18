from pydantic import BaseModel


class ParseOptions(BaseModel):
    y_tolerance: float = 3  # pdfplumber's y_tolerance, used to control spacing between lines
    x_tolerance_ratio: float = 0.15  # ratio of x_tolerance to the width of the text content area
