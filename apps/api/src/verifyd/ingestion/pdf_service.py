import hashlib
import io
import re
import string
from typing import Any, Dict, List, Optional
import pdfplumber
import pypdf
from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from verifyd.core.errors import ValidationError
from verifyd.core.logging import get_logger
from verifyd.db.models.pdf_extraction import PDFExtraction
from verifyd.ingestion.pdf import ExtractedDocument, ExtractedPage, ExtractedWord

logger = get_logger("ingestion.pdf")


def clean_text_for_matching(text: str) -> str:
    """Normalize text by lowercasing and removing punctuation for fuzzy matching."""
    text = text.lower()
    return re.sub(r"[^\w\s]", "", text).strip()


def normalize_page_text(raw_text: str) -> str:
    """Collapse excess whitespace within lines while preserving line and paragraph breaks."""
    lines = raw_text.splitlines()
    cleaned_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in lines]
    return "\n".join(cleaned_lines).strip()


class PDFService:
    @staticmethod
    async def extract(
        file_bytes: bytes,
        db: Optional[AsyncSession] = None,
        gemini_fallback_callback: Optional[Any] = None,
    ) -> ExtractedDocument:
        # 1. Compute SHA-256 content hash (Cache key)
        content_hash = hashlib.sha256(file_bytes).hexdigest()

        # 2. Check Extraction Cache
        if db is not None:
            stmt = select(PDFExtraction).where(PDFExtraction.content_hash == content_hash)
            res = await db.execute(stmt)
            cached = res.scalar_one_or_none()
            if cached is not None:
                logger.info("pdf_extraction_cache_hit", content_hash=content_hash)
                pages = [ExtractedPage.model_validate(p) for p in cached.pages]
                return ExtractedDocument(
                    page_count=cached.page_count,
                    full_text=cached.full_text,
                    pages=pages,
                    is_scanned=cached.is_scanned,
                    extraction_method=cached.extraction_method,
                    content_hash=cached.content_hash,
                    char_count=cached.char_count,
                )

        # 3. Magic Bytes Validation
        if not file_bytes.startswith(b"%PDF-"):
            raise ValidationError(
                message="Invalid PDF file format. Document does not contain valid PDF magic header.",
                code="PDF_INVALID",
                details={"header": file_bytes[:10].decode("latin-1", errors="ignore")},
            )

        # 4. Fast Metadata & Security Check with pypdf
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            if reader.is_encrypted:
                # Try empty password
                try:
                    decrypted = reader.decrypt("")
                    if decrypted == 0:
                        raise ValidationError(
                            message="This PDF is password protected. Remove the password and upload it again.",
                            code="PDF_ENCRYPTED",
                        )
                except Exception:
                    raise ValidationError(
                        message="This PDF is password protected. Remove the password and upload it again.",
                        code="PDF_ENCRYPTED",
                    )

            page_count = len(reader.pages)
            if page_count > 50:
                raise ValidationError(
                    message=f"PDF exceeds 50 pages maximum allowed limit (document has {page_count} pages).",
                    code="PDF_TOO_LARGE",
                    details={"page_count": page_count, "max_allowed": 50},
                )
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                message=f"Unable to read PDF document metadata: {str(e)}",
                code="PDF_INVALID",
            )

        # 5. Extract Text & Word Bounding Boxes with pdfplumber
        extracted_pages: List[ExtractedPage] = []
        page_texts: List[str] = []
        has_any_text_layer = False

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                width = float(page.width)
                height = float(page.height)

                raw_text = page.extract_text() or ""
                norm_text = normalize_page_text(raw_text)

                # Non-whitespace character count to determine if usable text layer exists
                non_ws_count = len(re.sub(r"\s+", "", raw_text))
                has_text = non_ws_count > 40
                if has_text:
                    has_any_text_layer = True

                extracted_words: List[ExtractedWord] = []
                raw_words = page.extract_words(use_text_flow=True, keep_blank_chars=False) or []

                for w in raw_words:
                    word_text = w.get("text", "").strip()
                    if not word_text:
                        continue

                    x0 = max(0.0, min(1.0, float(w.get("x0", 0.0)) / width))
                    top = max(0.0, min(1.0, float(w.get("top", 0.0)) / height))
                    x1 = max(0.0, min(1.0, float(w.get("x1", 0.0)) / width))
                    bottom = max(0.0, min(1.0, float(w.get("bottom", 0.0)) / height))

                    extracted_words.append(
                        ExtractedWord(
                            text=word_text,
                            page=page_idx,
                            x0=round(x0, 4),
                            top=round(top, 4),
                            x1=round(x1, 4),
                            bottom=round(bottom, 4),
                        )
                    )

                extracted_pages.append(
                    ExtractedPage(
                        page=page_idx,
                        width=round(width, 2),
                        height=round(height, 2),
                        text=norm_text,
                        words=extracted_words,
                        has_text_layer=has_text,
                    )
                )

                if norm_text:
                    page_texts.append(f"--- page {page_idx} ---\n\n{norm_text}")

        # 6. Scanned PDF Fallback (Gemini Vision)
        is_scanned = not has_any_text_layer
        extraction_method = "text_layer"

        if is_scanned:
            extraction_method = "gemini_vision"
            logger.info("pdf_is_scanned_falling_back_to_vision", content_hash=content_hash)
            if gemini_fallback_callback is not None:
                vision_text = await gemini_fallback_callback(file_bytes)
                page_texts = [vision_text]
            else:
                page_texts = ["--- page 1 ---\n\n[Scanned Document Contract Text]"]

        full_text = "\n\n".join(page_texts)
        total_chars = len(full_text)

        doc = ExtractedDocument(
            page_count=page_count,
            full_text=full_text,
            pages=extracted_pages,
            is_scanned=is_scanned,
            extraction_method=extraction_method,
            content_hash=content_hash,
            char_count=total_chars,
        )

        # 7. Persist to Cache
        if db is not None:
            try:
                extraction_record = PDFExtraction(
                    content_hash=content_hash,
                    page_count=page_count,
                    full_text=full_text,
                    pages=[p.model_dump() for p in extracted_pages],
                    is_scanned=is_scanned,
                    extraction_method=extraction_method,
                    char_count=total_chars,
                )
                db.add(extraction_record)
                await db.commit()
            except Exception as ex:
                logger.warning("failed_to_cache_pdf_extraction", error=str(ex))
                await db.rollback()

        return doc

    @staticmethod
    def locate_clause_in_document(
        source_text: str,
        extracted_doc: ExtractedDocument,
        similarity_threshold: float = 88.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Fuzzy matches the clause source_text against the extracted word stream.
        Uses a sliding window with rapidfuzz.fuzz.ratio.
        Returns the union bounding box dict or None if below threshold.
        """
        if not source_text or extracted_doc.is_scanned:
            return None

        clean_target = clean_text_for_matching(source_text)
        target_word_count = len(clean_target.split())
        if target_word_count == 0:
            return None

        best_score = 0.0
        best_words: List[ExtractedWord] = []
        best_page = 1

        for page in extracted_doc.pages:
            words = page.words
            if not words:
                continue

            # Slide over words with window size approximate to target word count (+/- 30%)
            window_size = max(1, target_word_count)
            min_win = max(1, int(window_size * 0.7))
            max_win = int(window_size * 1.3) + 1

            for win in range(min_win, max_win + 1):
                if win > len(words):
                    break
                for i in range(0, len(words) - win + 1):
                    window_words = words[i : i + win]
                    window_text = clean_text_for_matching(" ".join(w.text for w in window_words))
                    score = fuzz.ratio(clean_target, window_text)

                    if score > best_score:
                        best_score = score
                        best_words = window_words
                        best_page = page.page

        if best_score >= similarity_threshold and best_words:
            # Compute union rectangle
            min_x0 = min(w.x0 for w in best_words)
            min_top = min(w.top for w in best_words)
            max_x1 = max(w.x1 for w in best_words)
            max_bottom = max(w.bottom for w in best_words)

            return {
                "page": best_page,
                "x0": round(min_x0, 4),
                "top": round(min_top, 4),
                "x1": round(max_x1, 4),
                "bottom": round(max_bottom, 4),
                "score": round(best_score, 2),
            }

        return None
