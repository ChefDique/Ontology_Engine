"""Tests for AccuLynx REST API Adapter (TASK_G3) and Dedup Logic (TASK_G4)."""

import csv
import io
import json

import pytest

from ontology_engine.node4_output.acculynx_api import AccuLynxAdapter
from ontology_engine.node4_output.dedup import deduplicate


# ── Deduplication Tests (TASK_G4) ──────────────────────────────────────────


class TestDeduplicate:
    """Test the deduplicate function."""

    def test_adds_unique_id_to_every_record(self):
        records = [{"description": "item1"}, {"description": "item2"}]
        result = deduplicate(records, "JOB-1", timestamp="20240101120000")
        for r in result:
            assert "unique_id" in r

    def test_unique_ids_are_globally_unique(self):
        records = [{"description": f"item{i}"} for i in range(100)]
        result = deduplicate(records, "JOB-1", timestamp="20240101120000")
        ids = [r["unique_id"] for r in result]
        assert len(ids) == len(set(ids))

    def test_does_not_mutate_input(self):
        original = [{"description": "item1"}]
        result = deduplicate(original, "JOB-1", timestamp="20240101120000")
        assert "unique_id" not in original[0]
        assert "unique_id" in result[0]

    def test_job_id_included_in_uid(self):
        result = deduplicate(
            [{"description": "a"}], "MY-JOB-42", timestamp="20240101120000"
        )
        assert "MY-JOB-42" in result[0]["unique_id"]

    def test_timestamp_included_in_uid(self):
        result = deduplicate(
            [{"description": "a"}], "JOB-1", timestamp="20240315093000"
        )
        assert "20240315093000" in result[0]["unique_id"]

    def test_empty_job_id_raises(self):
        with pytest.raises(ValueError, match="job_id must be non-empty"):
            deduplicate([{"x": 1}], "")

    def test_empty_records_returns_empty(self):
        result = deduplicate([], "JOB-1")
        assert result == []


# ── AccuLynx Adapter Tests (TASK_G3) ──────────────────────────────────────


@pytest.fixture
def adapter():
    return AccuLynxAdapter()


@pytest.fixture
def sample_data():
    return {
        "header": {"estimate_number": "EST-2024-003", "claim_number": "CLM-555"},
        "procurement_items": [
            {
                "category": "RFG",
                "description": "Architectural Shingles",
                "physical_qty": 97,
                "physical_unit": "bundles",
                "trade": "roofing",
                "unit_cost": 25.50,
            },
        ],
        "adjusted_totals": {"note": "O&P already stripped"},
    }


class TestAccuLynxFormatOutput:
    """Test JSON payload generation."""

    def test_returns_dict(self, adapter, sample_data):
        result = adapter.format_output(sample_data)
        assert isinstance(result, dict)

    def test_has_material_order(self, adapter, sample_data):
        result = adapter.format_output(sample_data)
        assert "material_order" in result
        assert "items" in result["material_order"]

    def test_item_count_matches(self, adapter, sample_data):
        result = adapter.format_output(sample_data)
        items = result["material_order"]["items"]
        assert len(items) == result["material_order"]["item_count"]

    def test_meta_indicates_partner_only(self, adapter, sample_data):
        result = adapter.format_output(sample_data)
        assert "partner_only" in result["_meta"]["api_status"]

    def test_job_reference_set(self, adapter, sample_data):
        result = adapter.format_output(sample_data)
        assert result["job_reference"] == "EST-2024-003"

    def test_item_total_calculated(self, adapter, sample_data):
        result = adapter.format_output(sample_data)
        item = result["material_order"]["items"][0]
        assert item["total"] == round(97 * 25.50, 2)


class TestAccuLynxExport:
    """Test dual-file export (JSON + CSV)."""

    def test_creates_json_and_csv(self, adapter, sample_data, tmp_path):
        payload = adapter.format_output(sample_data)
        out = tmp_path / "acculynx_output"
        csv_path = adapter.export(payload, out)

        json_path = out.with_suffix(".json")
        assert json_path.exists()
        assert csv_path.exists()
        assert csv_path.suffix == ".csv"

    def test_json_is_valid(self, adapter, sample_data, tmp_path):
        payload = adapter.format_output(sample_data)
        out = tmp_path / "acculynx_output"
        adapter.export(payload, out)

        json_path = out.with_suffix(".json")
        data = json.loads(json_path.read_text())
        assert data["job_reference"] == "EST-2024-003"

    def test_csv_has_correct_columns(self, adapter, sample_data, tmp_path):
        payload = adapter.format_output(sample_data)
        out = tmp_path / "acculynx_output"
        csv_path = adapter.export(payload, out)

        reader = csv.DictReader(io.StringIO(csv_path.read_text()))
        assert set(reader.fieldnames) == set(AccuLynxAdapter.ACCULYNX_CSV_COLUMNS)


class TestAccuLynxValidation:
    """Test validation logic."""

    def test_valid_payload_passes(self, adapter, sample_data):
        payload = adapter.format_output(sample_data)
        assert adapter.validate_output(payload) is True

    def test_missing_material_order_fails(self, adapter):
        assert adapter.validate_output({"job_reference": "X"}) is False

    def test_empty_items_fails(self, adapter):
        payload = {"material_order": {"items": []}}
        assert adapter.validate_output(payload) is False

    def test_non_dict_fails(self, adapter):
        assert adapter.validate_output("not a dict") is False

    def test_missing_required_item_fields_fails(self, adapter):
        payload = {
            "material_order": {
                "items": [{"item_name": "shingles"}]  # missing category, quantity, unit
            }
        }
        assert adapter.validate_output(payload) is False
