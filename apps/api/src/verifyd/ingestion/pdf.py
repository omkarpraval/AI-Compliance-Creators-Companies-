from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedWord(BaseModel):
    text: str
    page: int          # 1-indexed
    x0: float          # normalised 0-1 against page width
    top: float         # normalised 0-1 against page height
    x1: float          # normalised 0-1 against page width
    bottom: float      # normalised 0-1 against page height


class ExtractedPage(BaseModel):
    page: int
    width: float       # points, for the frontend to scale overlays
    height: float
    text: str
    words: List[ExtractedWord] = Field(default_factory=list)
    has_text_layer: bool = True


class ExtractedDocument(BaseModel):
    page_count: int
    full_text: str
    pages: List[ExtractedPage]
    is_scanned: bool = False               # True when no page has a usable text layer
    extraction_method: str = "text_layer"  # "text_layer" | "gemini_vision"
    content_hash: str                      # sha256 of the raw file bytes
    char_count: int


class BoundingBox(BaseModel):
    page: int
    x0: float
    top: float
    x1: float
    bottom: float
