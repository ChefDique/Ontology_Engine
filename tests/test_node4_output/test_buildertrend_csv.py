"""Tests for Buildertrend CSV Generator (TASK_G1)."""

import csv
import io
from pathlib import Path

import pytest

from ontology_engine.node4_output.buildertrend_csv import (
    BuildertrendAdapter,
    CATEGORY_TO_COST_CODE,
    CSV_COLUMNS,
)


@pytest.fixture
def adapter():
    return BuildertrendAdapter()


@pytest.fixture
def sample_data():
    """Minimal valid Node 3 → 4 payload."""
    return {
        "header": {"estimate_number": "EST-2024-001", "claim_number": "CLM-999"},
        "procurement_items": [
            {
                "category": "RFG",
                "description": "Architectural Shingles",
                "physical_qty": 97,
                "physical_unit": "bundles",
                "trade": "roofing",
                "unit_cost": 25.50,
            },
            {
                "category": "SID",
                "description": "Vinyl Siding Panels",
                "physical_qty": 40,
                "physical_unit": "pieces",
                "trade": "siding",
                "unit_cost": 18.75,
            },
        ],
        "adjusted_totals": {"materials_total": 3222.50, "note": "O&P already stripped"},
    }


class TestBuildertrendFormatOutput:
    """Test format_output produces correct CSV text."""

    def test_csv_has_correct_headers(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        assert set(reader.fieldnames) == set(CSV_COLUMNS)

    def test_csv_has_correct_row_count(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) == 2

    def test_cost_code_mapping(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert rows[0]["Cost Code"] == "100-ROOF"
        assert rows[1]["Cost Code"] == "200-SIDING"

    def test_unknown_category_fallback(self, adapter):
        data = {
            "header": {"estimate_number": "EST-001"},
            "procurement_items": [
                {
                    "category": "XYZ",
                    "description": "Mystery Item",
                    "physical_qty": 5,
                    "physical_unit": "each",
                    "trade": "general",
                    "unit_cost": 10.0,
                }
            ],
            "adjusted_totals": {},
        }
        csv_text = adapter.format_output(data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert rows[0]["Cost Code"] == "9999-XYZ"

    def test_values_propagated_correctly(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert rows[0]["Title"] == "Architectural Shingles"
        assert rows[0]["Quantity"] == "97"
        assert rows[0]["Unit"] == "bundles"
        assert rows[0]["Unit Cost"] == "25.5"

    def test_empty_items_produces_headers_only(self, adapter):
        data = {
            "header": {"estimate_number": "EST-EMPTY"},
            "procurement_items": [],
            "adjusted_totals": {},
        }
        csv_text = adapter.format_output(data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) == 0


class TestBuildertrendExport:
    """Test export writes file to disk."""

    def test_export_creates_file(self, adapter, sample_data, tmp_path):
        csv_text = adapter.format_output(sample_data)
        out = tmp_path / "bt_output.csv"
        result = adapter.export(csv_text, out)
        assert result.exists()
        # csv module writes \r\n; read_text normalizes to \n
        assert result.read_text().replace("\r\n", "\n") == csv_text.replace("\r\n", "\n")

    def test_export_creates_parent_dirs(self, adapter, sample_data, tmp_path):
        csv_text = adapter.format_output(sample_data)
        out = tmp_path / "nested" / "dir" / "bt.csv"
        result = adapter.export(csv_text, out)
        assert result.exists()


class TestBuildertrendValidation:
    """Test validate_output checks."""

    def test_valid_csv_passes(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        assert adapter.validate_output(csv_text) is True

    def test_empty_csv_fails(self, adapter):
        # Headers but no rows
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        assert adapter.validate_output(buf.getvalue()) is False

    def test_wrong_headers_fail(self, adapter):
        assert adapter.validate_output("bad,headers\n1,2\n") is False
