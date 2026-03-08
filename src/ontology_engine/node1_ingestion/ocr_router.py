"""
OCR Router — TASK_A1

Detects whether a PDF has a native text layer or is a scanned image.
Routes accordingly:
  - Native PDF → pdfplumber direct extraction
  - Scanned PDF → Tesseract/Textract OCR

Design by Contract:
  Precondition:  File is a valid PDF or image (JPG, PNG, TIFF)
  Postcondition: Returns clean text string with OCR confidence scores
"""

from pathlib import Path


def detect_pdf_type(pdf_path: Path) -> str:
    """Detect if PDF is native text or scanned image.

    Returns: 'native' or 'scanned'
    """
    raise NotImplementedError("TASK_A1: PDF type detection")


def extract_text(pdf_path: Path) -> dict:
    """Extract text from PDF using appropriate method.

    Returns:
        dict with keys:
            - text: str (extracted text)
            - method: str ('native' or 'ocr')
            - confidence: float (0.0–1.0, 1.0 for native)
            - page_count: int
    """
    raise NotImplementedError("TASK_A1: Text extraction routing")
