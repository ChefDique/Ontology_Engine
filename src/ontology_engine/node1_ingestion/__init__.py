"""Node 1 — Ingestion: OCR routing + PII redaction + token chunking.

Public API:
    ingest(file_path) → NODE_1_TO_2_SCHEMA-validated dict
"""

from ontology_engine.node1_ingestion.ocr_router import extract_text, detect_pdf_type
from ontology_engine.node1_ingestion.pii_sanitizer import redact_pii
from ontology_engine.node1_ingestion.token_chunker import chunk_text

__all__ = ["extract_text", "detect_pdf_type", "redact_pii", "chunk_text", "ingest"]


def ingest(file_path, max_tokens: int = 4000, overlap_tokens: int = 200) -> dict:
    """Full Node 1 pipeline: OCR → PII redaction → chunking.

    Returns a dict validated against NODE_1_TO_2_SCHEMA:
        - text: str
        - method: 'native' | 'ocr'
        - confidence: float 0.0–1.0
        - page_count: int
        - pii_redacted: True
        - chunks: list[{chunk_text, chunk_index, token_count}]
    """
    from pathlib import Path
    import jsonschema
    from ontology_engine.contracts.schemas import NODE_1_TO_2_SCHEMA

    file_path = Path(file_path)

    # Step 1: Extract text via OCR router
    extraction = extract_text(file_path)

    # Step 2: Redact PII (CONST_001 — mandatory)
    pii_result = redact_pii(extraction["text"])

    # Step 3: Chunk for LLM context windows
    chunks = chunk_text(
        pii_result["redacted_text"],
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
    )

    # Build output conforming to NODE_1_TO_2_SCHEMA
    output = {
        "text": pii_result["redacted_text"],
        "method": extraction["method"],
        "confidence": extraction["confidence"],
        "page_count": extraction["page_count"],
        "pii_redacted": True,
        "chunks": [
            {
                "chunk_text": c["chunk_text"],
                "chunk_index": c["chunk_index"],
                "token_count": c["token_count"],
            }
            for c in chunks
        ],
    }

    # Validate against contract before passing downstream
    jsonschema.validate(instance=output, schema=NODE_1_TO_2_SCHEMA)

    return output
