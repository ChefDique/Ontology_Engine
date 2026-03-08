"""JobNimbus QBO Bridge CSV Generator — TASK_G2.

QuickBooks Online Products & Services import format.
JobNimbus lacks native product import; the backdoor path is a QBO CSV.

CRITICAL: Display Name duplicates cause FATAL errors in JobNimbus.
Every record gets a unique identifier via dedup module.
"""

import csv
import io
from pathlib import Path

from .base_adapter import BaseCRMAdapter
from .dedup import deduplicate

# QBO Products & Services CSV columns.
QBO_COLUMNS = [
    "Display Name",
    "Type",
    "Description",
    "Price",
    "Cost",
    "Qty on Hand",
    "Income Account",
]

# Map trade names → QBO Income Account names.
TRADE_TO_ACCOUNT: dict[str, str] = {
    "roofing": "Roofing Income",
    "siding": "Siding Income",
    "gutters": "Gutters Income",
    "general": "General Income",
    "electrical": "Electrical Income",
    "plumbing": "Plumbing Income",
    "painting": "Painting Income",
    "flooring": "Flooring Income",
    "insulation": "Insulation Income",
    "drywall": "Drywall Income",
    "windows": "Windows Income",
}


class JobNimbusQBOAdapter(BaseCRMAdapter):
    """Generates QBO-compatible CSV for backdoor import into JobNimbus."""

    def _build_display_name(self, item: dict) -> str:
        """Build a display name from description + unique_id (set by dedup)."""
        desc = item.get("description", "Item")
        uid = item.get("unique_id", "")
        if uid:
            return f"{desc} [{uid}]"
        return desc

    def format_output(self, calculated_data: dict) -> str:
        """Convert Node 3 → 4 payload into QBO Products & Services CSV.

        Args:
            calculated_data: Dict conforming to NODE_3_TO_4_SCHEMA.

        Returns:
            CSV text ready for file export.
        """
        header_info = calculated_data.get("header", {})
        job_id = header_info.get("estimate_number", "UNKNOWN")
        items = calculated_data.get("procurement_items", [])

        # Dedup is CRITICAL here — JN fatals on duplicate Display Names
        items = deduplicate(items, job_id)

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=QBO_COLUMNS)
        writer.writeheader()

        for item in items:
            trade = item.get("trade", "general").lower()
            unit_cost = item.get("unit_cost", 0.0)
            qty = item.get("physical_qty", 0)

            writer.writerow(
                {
                    "Display Name": self._build_display_name(item),
                    "Type": "Inventory",
                    "Description": item.get("description", ""),
                    "Price": round(unit_cost * qty, 2),
                    "Cost": round(unit_cost, 2),
                    "Qty on Hand": qty,
                    "Income Account": TRADE_TO_ACCOUNT.get(
                        trade, "Miscellaneous Income"
                    ),
                }
            )

        return buf.getvalue()

    def export(self, formatted_data: str, output_path: Path) -> Path:
        """Write QBO CSV to disk.

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
        """Validate QBO CSV has correct columns and unique Display Names."""
        reader = csv.DictReader(io.StringIO(formatted_data))
        if set(reader.fieldnames or []) != set(QBO_COLUMNS):
            return False

        display_names: set[str] = set()
        for row in reader:
            name = row.get("Display Name", "")
            if name in display_names:
                return False  # Duplicate → would cause JN fatal error
            display_names.add(name)

        return len(display_names) > 0
