"""Integration tests for the full Node 1 pipeline (OCR → PII → Chunking → Contract)."""

import pytest
import jsonschema
from pathlib import Path
from unittest.mock import patch

from ontology_engine.node1_ingestion import ingest
from ontology_engine.contracts.schemas import NODE_1_TO_2_SCHEMA


@pytest.fixture
def native_pdf(tmp_path):
    """Create a PDF with native text including some PII."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        pytest.skip("reportlab not installed")

    pdf_path = tmp_path / "integration_test.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    # Write text with embedded PII
    lines = [
        "Xactimate Estimate Report",
        "Insured: John Smith",
        "SSN: 123-45-6789",
        "Email: john@example.com",
        "Phone: (808) 555-1234",
        "Policy: POL-12345678",
        "",
        "Line Items:",
        "RFG - Remove & replace comp shingles - 32.33 SQ - $185.50",
        "RFG - Roofing felt 15 lb - 32.33 SQ - $12.75",
        "RFG - Drip edge - 250 LF - $3.25",
        "RFG - Ridge cap shingles - 65 LF - $8.50",
    ]
    y = 750
    for line in lines:
        c.drawString(72, y, line)
        y -= 15
    c.save()
    return pdf_path


class TestFullPipeline:
    def test_ingest_produces_valid_contract(self, native_pdf):
        """The full pipeline must produce output conforming to NODE_1_TO_2_SCHEMA."""
        result = ingest(native_pdf)
        # Should not raise
        jsonschema.validate(instance=result, schema=NODE_1_TO_2_SCHEMA)

    def test_pii_redacted_flag_is_true(self, native_pdf):
        result = ingest(native_pdf)
        assert result["pii_redacted"] is True

    def test_ssn_not_in_output(self, native_pdf):
        result = ingest(native_pdf)
        assert "123-45-6789" not in result["text"]
        for chunk in result.get("chunks", []):
            assert "123-45-6789" not in chunk["chunk_text"]

    def test_email_not_in_output(self, native_pdf):
        result = ingest(native_pdf)
        assert "john@example.com" not in result["text"]

    def test_construction_data_preserved(self, native_pdf):
        result = ingest(native_pdf)
        # Xactimate line item data must survive PII redaction
        assert "32.33" in result["text"]
        assert "185.50" in result["text"]

    def test_method_is_native_for_text_pdf(self, native_pdf):
        result = ingest(native_pdf)
        assert result["method"] == "native"

    def test_confidence_is_1_for_native(self, native_pdf):
        result = ingest(native_pdf)
        assert result["confidence"] == 1.0

    def test_chunks_present(self, native_pdf):
        result = ingest(native_pdf)
        assert "chunks" in result
        assert len(result["chunks"]) >= 1

    def test_chunk_structure(self, native_pdf):
        result = ingest(native_pdf)
        for chunk in result["chunks"]:
            assert "chunk_text" in chunk
            assert "chunk_index" in chunk
            assert "token_count" in chunk

    def test_page_count_positive(self, native_pdf):
        result = ingest(native_pdf)
        assert result["page_count"] >= 1

    def test_text_not_empty(self, native_pdf):
        result = ingest(native_pdf)
        assert len(result["text"]) > 0

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ingest(tmp_path / "nonexistent.pdf")
