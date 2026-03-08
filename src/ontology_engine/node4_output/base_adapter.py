"""
Base Adapter — Abstract interface for CRM output adapters.

All CRM adapters (Buildertrend, JobNimbus, AccuLynx) implement this interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseCRMAdapter(ABC):
    """Abstract base class for CRM output adapters."""

    @abstractmethod
    def format_output(self, calculated_data: dict) -> dict | str:
        """Format calculated data for the target CRM.

        Returns: CRM-specific payload (dict for API, str for CSV)
        """
        ...

    @abstractmethod
    def export(self, formatted_data: dict | str, output_path: Path) -> Path:
        """Export formatted data to a file.

        Returns: Path to the exported file.
        """
        ...

    @abstractmethod
    def validate_output(self, formatted_data: dict | str) -> bool:
        """Validate that output matches target CRM's expected format."""
        ...
