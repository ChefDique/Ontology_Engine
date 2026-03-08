"""Tests for Node 1 — OCR Router (TASK_A1).

MVP: Tests native PDF extraction only. Scanned PDF / image OCR
paths are deferred (Tesseract not installed).
"""

import pytest
from pathlib import Path

from ontology_engine.node1_ingestion.ocr_router import (
    detect_pdf_type,
    extract_text,
    _NATIVE_TEXT_THRESHOLD,
)


# ---------- Fixtures ----------

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_PDFS_DIR = FIXTURES_DIR / "sample_pdfs"


@pytest.fixture
def native_pdf(tmp_path):
    """Create a minimal PDF with native text using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        pytest.skip("reportlab not installed — needed for PDF generation in tests")

    pdf_path = tmp_path / "native_test.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    text = "This is a test document with native text layer for extraction. " * 20
    c.drawString(72, 700, text[:80])
    c.drawString(72, 680, text[80:160])
    c.drawString(72, 660, text[160:240])
    c.save()
    return pdf_path


@pytest.fixture
def empty_pdf(tmp_path):
    """Create a PDF with no text (simulates scanned)."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        pytest.skip("reportlab not installed")

    pdf_path = tmp_path / "empty_test.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.showPage()
    c.save()
    return pdf_path


# ---------- detect_pdf_type tests ----------

class TestDetectPdfType:
    def test_native_pdf_detected(self, native_pdf):
        result = detect_pdf_type(native_pdf)
        assert result == "native"

    def test_empty_pdf_detected_as_scanned(self, empty_pdf):
        result = detect_pdf_type(empty_pdf)
        assert result == "scanned"

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            detect_pdf_type(tmp_path / "does_not_exist.pdf")

    def test_accepts_path_string(self, native_pdf):
        result = detect_pdf_type(str(native_pdf))
        assert result in ("native", "scanned")


# ---------- extract_text tests ----------

class TestExtractText:
    def test_native_pdf_extraction(self, native_pdf):
        result = extract_text(native_pdf)
        assert result["method"] == "native"
        assert result["confidence"] == 1.0
        assert result["page_count"] >= 1
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            extract_text(tmp_path / "missing.pdf")

    def test_unsupported_extension_raises(self, tmp_path):
        bad_file = tmp_path / "test.xyz"
        bad_file.write_text("not a pdf")
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text(bad_file)

    def test_scanned_pdf_raises_not_implemented(self, empty_pdf):
        """Scanned PDFs should raise NotImplementedError in MVP."""
        with pytest.raises(NotImplementedError, match="OCR.*deferred"):
            extract_text(empty_pdf)

    def test_image_raises_not_implemented(self, tmp_path):
        """Image OCR should raise NotImplementedError in MVP."""
        from PIL import Image
        img_path = tmp_path / "test.png"
        Image.new("RGB", (100, 100), "white").save(img_path)
        with pytest.raises(NotImplementedError, match="Image OCR"):
            extract_text(img_path)

    def test_output_has_required_keys(self, native_pdf):
        result = extract_text(native_pdf)
        required_keys = {"text", "method", "confidence", "page_count"}
        assert required_keys.issubset(result.keys())

    def test_method_is_valid_enum(self, native_pdf):
        result = extract_text(native_pdf)
        assert result["method"] in ("native", "ocr")

    def test_confidence_in_range(self, native_pdf):
        result = extract_text(native_pdf)
        assert 0.0 <= result["confidence"] <= 1.0


# ---------- Sample PDF tests (TASK_A4 integration) ----------

class TestSamplePDFs:
    """Tests that run against downloaded sample PDFs if available."""

    @pytest.mark.skipif(
        not (Path(__file__).parent.parent / "fixtures" / "sample_pdfs").exists()
        or not list(
            (Path(__file__).parent.parent / "fixtures" / "sample_pdfs").glob("*.pdf")
        ),
        reason="Sample PDFs not downloaded (TASK_A4)",
    )
    def test_sample_pdfs_extract(self):
        pdfs = list(SAMPLE_PDFS_DIR.glob("*.pdf"))
        for pdf in pdfs:
            result = extract_text(pdf)
            assert result["text"], f"No text extracted from {pdf.name}"
            assert result["page_count"] >= 1
