"""JobNimbus QBO Bridge CSV Generator — TASK_G2. QuickBooks Online Products & Services import."""

from pathlib import Path
from .base_adapter import BaseCRMAdapter


class JobNimbusQBOAdapter(BaseCRMAdapter):
    """Generates QBO-compatible CSV for backdoor import into JobNimbus."""

    def format_output(self, calculated_data: dict) -> str:
        raise NotImplementedError("TASK_G2")

    def export(self, formatted_data: str, output_path: Path) -> Path:
        raise NotImplementedError("TASK_G2")

    def validate_output(self, formatted_data: str) -> bool:
        raise NotImplementedError("TASK_G2")
