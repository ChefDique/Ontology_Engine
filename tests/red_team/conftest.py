"""Shared fixtures for the Red Team adversarial test suite."""

import json
import math
import os
import struct
import tempfile
from pathlib import Path

import pytest


# ── PDF Factories ───────────────────────────────────────────────────────────

def _minimal_pdf(text: str = "Hello World", num_pages: int = 1) -> bytes:
    """Create a minimal valid PDF with native text layer."""
    objects = []
    obj_id = 1

    # Catalog
    catalog_id = obj_id
    objects.append(f"{obj_id} 0 obj\n<< /Type /Catalog /Pages {obj_id + 1} 0 R >>\nendobj")
    obj_id += 1

    # Pages
    pages_id = obj_id
    kid_ids = list(range(obj_id + 1, obj_id + 1 + num_pages))
    kids_str = " ".join(f"{kid} 0 R" for kid in kid_ids)
    objects.append(
        f"{obj_id} 0 obj\n"
        f"<< /Type /Pages /Kids [{kids_str}] /Count {num_pages} >>\n"
        f"endobj"
    )
    obj_id += 1

    # Pages + Content streams
    for i in range(num_pages):
        page_text = f"{text} Page {i + 1}" if num_pages > 1 else text

        # Content stream
        content_id = obj_id + 1
        stream_data = f"BT /F1 12 Tf 100 700 Td ({page_text}) Tj ET"
        stream_len = len(stream_data)

        # Font
        font_id = obj_id + 2

        objects.append(
            f"{obj_id} 0 obj\n"
            f"<< /Type /Page /Parent {pages_id} 0 R "
            f"/MediaBox [0 0 612 792] "
            f"/Contents {content_id} 0 R "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>\n"
            f"endobj"
        )
        obj_id += 1

        objects.append(
            f"{obj_id} 0 obj\n"
            f"<< /Length {stream_len} >>\nstream\n{stream_data}\nendstream\n"
            f"endobj"
        )
        obj_id += 1

        objects.append(
            f"{obj_id} 0 obj\n"
            f"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n"
            f"endobj"
        )
        obj_id += 1

    # Build the file
    body = "\n".join(objects)
    xref_offset = len(f"%PDF-1.4\n{body}\n")

    pdf_bytes = (
        f"%PDF-1.4\n"
        f"{body}\n"
        f"xref\n"
        f"0 {obj_id}\n"
        f"0000000000 65535 f \n"
    )

    for i in range(1, obj_id):
        pdf_bytes += f"{str(i * 100).zfill(10)} 00000 n \n"

    pdf_bytes += (
        f"trailer\n"
        f"<< /Size {obj_id} /Root {catalog_id} 0 R >>\n"
        f"startxref\n"
        f"{xref_offset}\n"
        f"%%EOF"
    )
    return pdf_bytes.encode("latin-1")


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory(prefix="redteam_") as d:
        yield Path(d)


@pytest.fixture
def valid_pdf(tmp_dir):
    """Create a valid PDF with extractable text for baseline testing."""
    pdf_path = tmp_dir / "valid.pdf"
    # Use reportlab-free minimal approach: write actual text into a pdfplumber-readable PDF
    # For real testing, we write a simple PDF that pdfplumber can extract text from
    pdf_path.write_bytes(_minimal_pdf("Xactimate Estimate Report Line Item RFG 32.33 SQ"))
    return pdf_path


@pytest.fixture
def zero_byte_pdf(tmp_dir):
    """Create a zero-byte file with .pdf extension."""
    pdf_path = tmp_dir / "empty.pdf"
    pdf_path.write_bytes(b"")
    return pdf_path


@pytest.fixture
def corrupt_header_pdf(tmp_dir):
    """Create a file with corrupt PDF header (not starting with %PDF)."""
    pdf_path = tmp_dir / "corrupt_header.pdf"
    pdf_path.write_bytes(b"NOT_A_PDF_HEADER\x00\x01\x02\x03garbage data here")
    return pdf_path


@pytest.fixture
def binary_garbage_pdf(tmp_dir):
    """Create a file filled with random binary garbage."""
    pdf_path = tmp_dir / "binary_garbage.pdf"
    pdf_path.write_bytes(os.urandom(4096))
    return pdf_path


@pytest.fixture
def truncated_pdf(tmp_dir):
    """Create a PDF with valid header but truncated body."""
    pdf_path = tmp_dir / "truncated.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog")  # Truncated mid-object
    return pdf_path


# ── Valid Data Factories ────────────────────────────────────────────────────

@pytest.fixture
def valid_node1_output():
    """Valid Node 1 → Node 2 contract payload."""
    return {
        "text": "Xactimate Estimate RFG 32.33 SQ $185.50 Roofing shingles",
        "method": "native",
        "confidence": 1.0,
        "page_count": 1,
        "pii_redacted": True,
        "chunks": [
            {
                "chunk_text": "Xactimate Estimate RFG 32.33 SQ $185.50 Roofing shingles",
                "chunk_index": 0,
                "token_count": 12,
            }
        ],
    }


@pytest.fixture
def valid_node2_output():
    """Valid Node 2 → Node 3 contract payload."""
    return {
        "header": {
            "estimate_number": "TEST-001",
            "claim_number": None,
            "carrier": "Test Insurance",
            "loss_date": "2026-01-15",
        },
        "line_items": [
            {
                "category": "RFG",
                "selector": "240",
                "description": "Remove & replace comp. shingles - 240 lb",
                "quantity": 32.33,
                "unit_of_measure": "SQ",
                "unit_price": 185.50,
                "total": 5997.22,
                "has_override_note": False,
                "f9_note_text": None,
            },
        ],
        "totals": {
            "rcv": 15000.00,
            "depreciation": 3000.00,
            "acv": 12000.00,
            "overhead": 1500.00,
            "profit": 1500.00,
            "tax": 675.00,
            "net_claim": 10500.00,
        },
    }


@pytest.fixture
def valid_node3_output():
    """Valid Node 3 → Node 4 contract payload."""
    return {
        "header": {"estimate_number": "TEST-001"},
        "procurement_items": [
            {
                "category": "RFG",
                "description": "Remove & replace comp. shingles - 240 lb",
                "physical_qty": 102,
                "physical_unit": "bundles",
                "trade": "roofing",
                "unit_cost": 185.50,
            },
        ],
        "credit_items": [],
        "adjusted_totals": {
            "rcv": 12000.00,
            "depreciation": 3000.00,
            "acv": 9000.00,
            "overhead": 0.0,
            "profit": 0.0,
            "tax": 540.00,
            "net_claim": 9540.00,
        },
        "hitl_flags": [],
    }


@pytest.fixture
def valid_node5_input(valid_node3_output):
    """Valid Node 5 input (two Node 3 outputs)."""
    import copy
    contractor = copy.deepcopy(valid_node3_output)
    contractor["procurement_items"][0]["physical_qty"] = 110
    contractor["adjusted_totals"]["rcv"] = 14000.00
    return {
        "adjuster_estimate": valid_node3_output,
        "contractor_estimate": contractor,
    }
