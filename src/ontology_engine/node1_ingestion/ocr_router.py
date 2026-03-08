"""
OCR Router — TASK_A1

Detects whether a PDF has a native text layer or is a scanned image.
Routes accordingly:
  - Native PDF → pdfplumber direct extraction
  - Scanned PDF → graceful error (Tesseract not required for MVP)

Design by Contract:
  Precondition:  File is a valid PDF or image (JPG, PNG, TIFF)
  Postcondition: Returns clean text string with extraction confidence scores

MVP Note (ADR):
  Tesseract/OCR dependencies are deferred. 90%+ of Xactimate PDFs are
  software-generated (native text layer). Scanned PDF support can be
  added later as a drop-in upgrade without changing the public API.
"""

from pathlib import Path
from typing import Literal

import pdfplumber

# Minimum character threshold to consider a PDF page as having native text
_NATIVE_TEXT_THRESHOLD = 50

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"}


def detect_pdf_type(pdf_path: Path) -> Literal["native", "scanned"]:
    """Detect if PDF is native text or scanned image.

    Strategy: Open the first few pages with pdfplumber and check if they
    contain extractable text.  If the combined text from the first 3 pages
    (or fewer if the PDF is short) exceeds the threshold, it's native.

    Returns: 'native' or 'scanned'
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        sample_pages = pdf.pages[: min(3, len(pdf.pages))]
        combined_text = ""
        for page in sample_pages:
            text = page.extract_text() or ""
            combined_text += text

    if len(combined_text.strip()) >= _NATIVE_TEXT_THRESHOLD:
        return "native"
    return "scanned"


def _extract_native(pdf_path: Path) -> dict:
    """Extract text from a native (text-layer) PDF using pdfplumber."""
    pages_text: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

    full_text = "\n\n".join(pages_text)
    return {
        "text": full_text,
        "method": "native",
        "confidence": 1.0,  # Native text is always high-confidence
        "page_count": page_count,
    }


def _extract_ocr(pdf_path: Path) -> dict:
    """Extract text from a scanned PDF using Tesseract OCR.

    MVP: This is a stub that raises a clear error directing users
    to install OCR dependencies when scanned PDF support is needed.
    The architecture supports drop-in Tesseract integration later.
    """
    raise NotImplementedError(
        f"Scanned PDF detected: {pdf_path.name}. "
        "OCR (Tesseract) support deferred for MVP. "
        "Install pytesseract + pdf2image for scanned PDF support, "
        "or convert to native text PDF first."
    )


def _extract_image(image_path: Path) -> dict:
    """Extract text from a standalone image file.

    MVP: Stub — raises clear error. Drop-in pytesseract later.
    """
    raise NotImplementedError(
        f"Image OCR not available for MVP: {image_path.name}. "
        "Install pytesseract for image text extraction."
    )


def extract_text(file_path: Path) -> dict:
    """Extract text from a PDF or image using the appropriate method.

    Routing logic:
      1. If file is an image → OCR (deferred for MVP)
      2. If file is a PDF → detect native vs scanned, route accordingly

    Returns:
        dict with keys:
            - text: str (extracted text)
            - method: str ('native' or 'ocr')
            - confidence: float (0.0–1.0, 1.0 for native)
            - page_count: int
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix in _IMAGE_EXTENSIONS:
        return _extract_image(file_path)

    if suffix != ".pdf":
        raise ValueError(
            f"Unsupported file type: {suffix}. "
            f"Supported: .pdf, {', '.join(sorted(_IMAGE_EXTENSIONS))}"
        )

    pdf_type = detect_pdf_type(file_path)
    if pdf_type == "native":
        return _extract_native(file_path)
    else:
        return _extract_ocr(file_path)
