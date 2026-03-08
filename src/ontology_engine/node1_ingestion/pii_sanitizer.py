"""
PII Sanitizer — TASK_A2

Redacts Personally Identifiable Information from extracted text
BEFORE any data reaches an LLM API.

Uses Microsoft Presidio for detection and anonymization.

Design by Contract:
  Precondition:  Input is a text string from OCR router
  Postcondition: Output contains ZERO PII — no names, addresses, SSNs, policy numbers
  Invariant:     ZERO PII IN OUTPUT — NO EXCEPTIONS (CONST_001)
"""


def redact_pii(text: str) -> dict:
    """Redact all PII from input text.

    Returns:
        dict with keys:
            - redacted_text: str (PII-free text)
            - pii_found: list of dicts with type, original (masked), position
            - pii_count: int (number of PII items found and redacted)
    """
    raise NotImplementedError("TASK_A2: PII redaction pipeline")
