"""Buildertrend CSV Generator — TASK_G1. Assembly import format."""

from pathlib import Path
from .base_adapter import BaseCRMAdapter


class BuildertrendAdapter(BaseCRMAdapter):
    """Generates Buildertrend-compatible CSV assembly import files."""

    def format_output(self, calculated_data: dict) -> str:
        raise NotImplementedError("TASK_G1")

    def export(self, formatted_data: str, output_path: Path) -> Path:
        raise NotImplementedError("TASK_G1")

    def validate_output(self, formatted_data: str) -> bool:
        raise NotImplementedError("TASK_G1")
