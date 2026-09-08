from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from verifyd.db.base import Base


class PDFExtraction(Base):
    __tablename__ = "pdf_extractions"

    content_hash: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    pages: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    is_scanned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(50), default="text_layer", nullable=False)  # 'text_layer' | 'gemini_vision'
    char_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
