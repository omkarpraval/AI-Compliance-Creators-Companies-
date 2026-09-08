import io
import os
import pytest
from pypdf import PdfWriter
from verifyd.core.errors import ValidationError
from verifyd.ingestion.pdf_service import PDFService

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.mark.asyncio
async def test_pdf_extraction_text_layer_normalized_coords():
    pdf_path = os.path.join(FIXTURES_DIR, "clean_contract.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    doc = await PDFService.extract(pdf_bytes)

    assert doc.page_count == 2
    assert not doc.is_scanned
    assert doc.extraction_method == "text_layer"
    assert "Lumen Hydration Serum" in doc.full_text
    assert len(doc.pages) == 2

    # Check that word coordinates are strictly between 0.0 and 1.0
    for page in doc.pages:
        assert page.has_text_layer
        assert len(page.words) > 0
        for w in page.words:
            assert 0.0 <= w.x0 <= 1.0
            assert 0.0 <= w.top <= 1.0
            assert 0.0 <= w.x1 <= 1.0
            assert 0.0 <= w.bottom <= 1.0
            assert w.x0 <= w.x1
            assert w.top <= w.bottom


@pytest.mark.asyncio
async def test_pdf_extraction_scanned_fallback():
    pdf_path = os.path.join(FIXTURES_DIR, "scanned_contract.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    doc = await PDFService.extract(pdf_bytes)

    assert doc.is_scanned is True
    assert doc.extraction_method == "gemini_vision"
    assert doc.page_count >= 1


@pytest.mark.asyncio
async def test_pdf_extraction_encrypted_rejection():
    pdf_path = os.path.join(FIXTURES_DIR, "encrypted_contract.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    with pytest.raises(ValidationError) as exc_info:
        await PDFService.extract(pdf_bytes)

    assert exc_info.value.code == "PDF_ENCRYPTED"
    assert "password protected" in exc_info.value.message


@pytest.mark.asyncio
async def test_pdf_extraction_oversized_rejection():
    writer = PdfWriter()
    for _ in range(55):
        writer.add_blank_page(width=612, height=792)

    buf = io.BytesIO()
    writer.write(buf)
    oversized_bytes = buf.getvalue()

    with pytest.raises(ValidationError) as exc_info:
        await PDFService.extract(oversized_bytes)

    assert exc_info.value.code == "PDF_TOO_LARGE"
    assert "exceeds 50 pages" in exc_info.value.message


@pytest.mark.asyncio
async def test_locate_clause_in_document_fuzzy_matching():
    pdf_path = os.path.join(FIXTURES_DIR, "clean_contract.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    doc = await PDFService.extract(pdf_bytes)

    # 1. Exact or altered whitespace sentence from page 1
    query_text = "The   Creator agrees to feature the   Lumen Hydration Serum for a minimum of thirty continuous seconds."
    bbox = PDFService.locate_clause_in_document(query_text, doc)

    assert bbox is not None
    assert bbox["page"] == 1
    assert 0.0 <= bbox["x0"] <= 1.0
    assert 0.0 <= bbox["top"] <= 1.0
    assert bbox["score"] >= 88.0

    # 2. Sentence from page 2
    page2_query = "No competitor skincare products such as GlowCo or PureSkin may appear"
    bbox2 = PDFService.locate_clause_in_document(page2_query, doc)

    assert bbox2 is not None
    assert bbox2["page"] == 2

    # 3. Completely unrelated text returns None (never a wrong highlight)
    unrelated_text = "The tenant shall pay monthly rent of five thousand dollars to the landlord on the first day of each month."
    bbox_none = PDFService.locate_clause_in_document(unrelated_text, doc)

    assert bbox_none is None
