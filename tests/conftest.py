"""Shared test fixtures for the Ontology Engine test suite."""

import pytest
import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_extraction_data():
    """Load sample extraction JSON for Node 2→3 testing."""
    sample_path = FIXTURES_DIR / "sample_extractions.json"
    if sample_path.exists():
        return json.loads(sample_path.read_text())
    # Minimal fixture for stub testing
    return {
        "header": {
            "estimate_number": "TEST-001",
            "claim_number": None,
            "carrier": "Test Insurance Co",
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
            {
                "category": "RFG",
                "selector": "FELT",
                "description": "Roofing felt - 15 lb",
                "quantity": 32.33,
                "unit_of_measure": "SQ",
                "unit_price": 12.75,
                "total": 412.21,
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
