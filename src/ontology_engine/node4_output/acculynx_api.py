"""AccuLynx REST API Adapter — TASK_G3. OAuth 2.0 + API V2.

RESEARCH FINDINGS (TASK_G3):
─────────────────────────────
The AccuLynx public REST API V2 supports:
  ✓ Leads, Contacts, Jobs, Appointments, Notes, Webhooks
  ✗ Material Order POST — **partner-only / private API**

Strategy:
  1. format_output() builds an AccuLynx-compatible JSON payload.
  2. Since Material Order POST requires partner access, export()
     falls back to generating a CSV for manual upload.
  3. When partner API keys become available, swap export() to use
     the real API endpoint without changing the format_output() contract.
"""

import csv
import io
import json
from pathlib import Path

from .base_adapter import BaseCRMAdapter
from .dedup import deduplicate


class AccuLynxAdapter(BaseCRMAdapter):
    """AccuLynx REST API V2 adapter.

    NOTE: Material Order POST is partner-only.
    Current implementation produces a CSV fallback for manual upload.
    """

    ACCULYNX_CSV_COLUMNS = [
        "Item Name",
        "Category",
        "Quantity",
        "Unit",
        "Unit Cost",
        "Total",
        "Trade",
    ]

    def format_output(self, calculated_data: dict) -> dict:
        """Convert Node 3 → 4 payload into AccuLynx-structured dict.

        The dict mirrors what the Material Order POST endpoint would
        accept, so when partner access is granted, no upstream changes
        are needed.

        Args:
            calculated_data: Dict conforming to NODE_3_TO_4_SCHEMA.

        Returns:
            AccuLynx-structured dict payload.
        """
        header_info = calculated_data.get("header", {})
        job_id = header_info.get("estimate_number", "UNKNOWN")
        items = calculated_data.get("procurement_items", [])

        items = deduplicate(items, job_id)

        material_lines = []
        for item in items:
            qty = item.get("physical_qty", 0)
            unit_cost = item.get("unit_cost", 0.0)

            material_lines.append(
                {
                    "item_name": item.get("description", ""),
                    "category": item.get("category", ""),
                    "quantity": qty,
                    "unit": item.get("physical_unit", ""),
                    "unit_cost": round(unit_cost, 2),
                    "total": round(qty * unit_cost, 2),
                    "trade": item.get("trade", ""),
                    "unique_id": item.get("unique_id", ""),
                }
            )

        return {
            "job_reference": job_id,
            "claim_number": header_info.get("claim_number"),
            "material_order": {
                "items": material_lines,
                "item_count": len(material_lines),
            },
            "_meta": {
                "api_method": "POST /api/v2/material-orders",
                "api_status": "partner_only — CSV fallback active",
            },
        }

    def export(self, formatted_data: dict, output_path: Path) -> Path:
        """Export AccuLynx data as both JSON payload and CSV fallback.

        Creates two files at output_path:
          - {stem}.json  — the API payload (for future partner use)
          - {stem}.csv   — the CSV fallback for manual upload

        Args:
            formatted_data: Dict from format_output().
            output_path: Base destination path.

        Returns:
            Path to the CSV fallback file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON payload (for reference / future API use)
        json_path = output_path.with_suffix(".json")
        json_path.write_text(
            json.dumps(formatted_data, indent=2), encoding="utf-8"
        )

        # Write CSV fallback for manual upload
        csv_path = output_path.with_suffix(".csv")
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=self.ACCULYNX_CSV_COLUMNS)
        writer.writeheader()

        for item in formatted_data.get("material_order", {}).get("items", []):
            writer.writerow(
                {
                    "Item Name": item.get("item_name", ""),
                    "Category": item.get("category", ""),
                    "Quantity": item.get("quantity", 0),
                    "Unit": item.get("unit", ""),
                    "Unit Cost": item.get("unit_cost", 0.0),
                    "Total": item.get("total", 0.0),
                    "Trade": item.get("trade", ""),
                }
            )

        csv_path.write_text(buf.getvalue(), encoding="utf-8")
        return csv_path

    def validate_output(self, formatted_data: dict) -> bool:
        """Validate the AccuLynx payload structure."""
        if not isinstance(formatted_data, dict):
            return False
        if "material_order" not in formatted_data:
            return False

        order = formatted_data["material_order"]
        items = order.get("items", [])
        if not items:
            return False

        # Verify each item has required fields
        required = {"item_name", "category", "quantity", "unit"}
        for item in items:
            if not required.issubset(item.keys()):
                return False

        return True
