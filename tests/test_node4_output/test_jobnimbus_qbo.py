"""Tests for JobNimbus QBO Bridge CSV Generator (TASK_G2)."""

import csv
import io

import pytest

from ontology_engine.node4_output.jobnimbus_qbo import (
    JobNimbusQBOAdapter,
    QBO_COLUMNS,
)


@pytest.fixture
def adapter():
    return JobNimbusQBOAdapter()


@pytest.fixture
def sample_data():
    """Minimal valid Node 3 → 4 payload."""
    return {
        "header": {"estimate_number": "EST-2024-002", "claim_number": None},
        "procurement_items": [
            {
                "category": "RFG",
                "description": "30-Year Shingles",
                "physical_qty": 50,
                "physical_unit": "bundles",
                "trade": "roofing",
                "unit_cost": 30.00,
            },
            {
                "category": "GUT",
                "description": "Seamless Aluminum Gutters",
                "physical_qty": 120,
                "physical_unit": "linear_feet",
                "trade": "gutters",
                "unit_cost": 8.50,
            },
        ],
        "adjusted_totals": {"note": "O&P already stripped"},
    }


class TestJobNimbusFormatOutput:
    """Test QBO CSV generation."""

    def test_csv_has_qbo_columns(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        assert set(reader.fieldnames) == set(QBO_COLUMNS)

    def test_csv_row_count(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert len(rows) == 2

    def test_display_names_are_unique(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        names = [row["Display Name"] for row in reader]
        assert len(names) == len(set(names)), "Display Names must be unique"

    def test_display_names_contain_unique_id(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            # unique_id is appended in brackets
            assert "[" in row["Display Name"] and "]" in row["Display Name"]

    def test_income_account_mapping(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert rows[0]["Income Account"] == "Roofing Income"
        assert rows[1]["Income Account"] == "Gutters Income"

    def test_unknown_trade_maps_to_misc(self, adapter):
        data = {
            "header": {"estimate_number": "EST-003"},
            "procurement_items": [
                {
                    "category": "CUSTOM",
                    "description": "Custom Item",
                    "physical_qty": 1,
                    "physical_unit": "each",
                    "trade": "custom_trade",
                    "unit_cost": 100.0,
                }
            ],
            "adjusted_totals": {},
        }
        csv_text = adapter.format_output(data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert rows[0]["Income Account"] == "Miscellaneous Income"

    def test_price_is_qty_times_unit_cost(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        # Row 0: 50 bundles * $30.00 = $1500.00
        assert float(rows[0]["Price"]) == 1500.0
        # Row 1: 120 lf * $8.50 = $1020.00
        assert float(rows[1]["Price"]) == 1020.0

    def test_type_is_inventory(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            assert row["Type"] == "Inventory"


class TestJobNimbusExport:
    """Test file export."""

    def test_export_creates_file(self, adapter, sample_data, tmp_path):
        csv_text = adapter.format_output(sample_data)
        out = tmp_path / "jn_output.csv"
        result = adapter.export(csv_text, out)
        assert result.exists()
        # csv module writes \r\n; read_text normalizes to \n
        assert result.read_text().replace("\r\n", "\n") == csv_text.replace("\r\n", "\n")


class TestJobNimbusValidation:
    """Test validation catches duplicates."""

    def test_valid_csv_passes(self, adapter, sample_data):
        csv_text = adapter.format_output(sample_data)
        assert adapter.validate_output(csv_text) is True

    def test_duplicate_display_names_fail(self, adapter):
        """Manually craft CSV with duplicate names — must fail."""
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=QBO_COLUMNS)
        writer.writeheader()
        for _ in range(2):
            writer.writerow(
                {
                    "Display Name": "SAME NAME",
                    "Type": "Inventory",
                    "Description": "test",
                    "Price": 100,
                    "Cost": 10,
                    "Qty on Hand": 5,
                    "Income Account": "General Income",
                }
            )
        assert adapter.validate_output(buf.getvalue()) is False

    def test_wrong_headers_fail(self, adapter):
        assert adapter.validate_output("wrong,headers\n1,2\n") is False
