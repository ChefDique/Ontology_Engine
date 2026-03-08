"""Buildertrend CSV Generator — TASK_G1. Assembly import format.

Maps Node 3 procurement items → Buildertrend Cost Code CSV.
Columns mirror the official Buildertrend Assembly Import template:
  Cost Code | Title | Quantity | Unit | Unit Cost
"""

import csv
import io
from pathlib import Path

from .base_adapter import BaseCRMAdapter
from .dedup import deduplicate

# Xactimate CAT → Buildertrend Cost Code mapping.
# Extend this dict as new categories appear in estimates.
CATEGORY_TO_COST_CODE: dict[str, str] = {
    "RFG": "100-ROOF",
    "SID": "200-SIDING",
    "GUT": "300-GUTTERS",
    "DRY": "400-DRYWALL",
    "PLM": "500-PLUMBING",
    "ELC": "600-ELECTRICAL",
    "GNL": "700-GENERAL",
    "PNT": "800-PAINT",
    "FNC": "900-FENCING",
    "FLR": "1000-FLOORING",
    "INS": "1100-INSULATION",
    "WND": "1200-WINDOWS",
}

CSV_COLUMNS = ["Cost Code", "Title", "Quantity", "Unit", "Unit Cost"]


class BuildertrendAdapter(BaseCRMAdapter):
    """Generates Buildertrend-compatible CSV assembly import files."""

    def _map_cost_code(self, category: str) -> str:
        """Map an Xactimate category to a Buildertrend Cost Code.

        Falls back to a generic code with the raw category prefix for
        unmapped categories so no data is silently dropped.
        """
        return CATEGORY_TO_COST_CODE.get(
            category.upper(), f"9999-{category.upper()}"
        )

    def format_output(self, calculated_data: dict) -> str:
        """Convert Node 3 → 4 payload into Buildertrend CSV string.

        Args:
            calculated_data: Dict conforming to NODE_3_TO_4_SCHEMA.

        Returns:
            CSV text ready for file export.
        """
        header_info = calculated_data.get("header", {})
        job_id = header_info.get("estimate_number", "UNKNOWN")
        items = calculated_data.get("procurement_items", [])

        # Deduplicate before formatting
        items = deduplicate(items, job_id)

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        for item in items:
            writer.writerow(
                {
                    "Cost Code": self._map_cost_code(item.get("category", "")),
                    "Title": item.get("description", ""),
                    "Quantity": item.get("physical_qty", 0),
                    "Unit": item.get("physical_unit", ""),
                    "Unit Cost": item.get("unit_cost", 0.0),
                }
            )

        return buf.getvalue()

    def export(self, formatted_data: str, output_path: Path) -> Path:
        """Write Buildertrend CSV to disk.

        Args:
            formatted_data: CSV text from format_output().
            output_path: Destination file path.

        Returns:
            Path to the written file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted_data, encoding="utf-8")
        return output_path

    def validate_output(self, formatted_data: str) -> bool:
        """Validate exported CSV has correct columns and at least one row."""
        reader = csv.DictReader(io.StringIO(formatted_data))
        if set(reader.fieldnames or []) != set(CSV_COLUMNS):
            return False
        rows = list(reader)
        return len(rows) > 0
