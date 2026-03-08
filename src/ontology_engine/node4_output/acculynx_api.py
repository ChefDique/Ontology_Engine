"""AccuLynx REST API Adapter — TASK_G3. OAuth 2.0 + API V2."""

from pathlib import Path
from .base_adapter import BaseCRMAdapter


class AccuLynxAdapter(BaseCRMAdapter):
    """AccuLynx REST API V2 adapter. NOTE: Material Order POST is partner-only."""

    def format_output(self, calculated_data: dict) -> dict:
        raise NotImplementedError("TASK_G3: Requires partner API access research")

    def export(self, formatted_data: dict, output_path: Path) -> Path:
        raise NotImplementedError("TASK_G3")

    def validate_output(self, formatted_data: dict) -> bool:
        raise NotImplementedError("TASK_G3")
