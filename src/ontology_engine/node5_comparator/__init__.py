"""
Node 5 — Estimate Comparator (Gap Detection)

Compares two Node 3 outputs (adjuster estimate vs contractor estimate)
to identify financial gaps: missing line items, quantity discrepancies,
O&P recovery opportunities, and depreciation audit findings.

Architecture:
    Both PDFs → Nodes 1-3 independently → Node 5 (Comparator) → Node 6 (Report)
"""

from .comparator import compare_estimates

__all__ = ["compare_estimates"]
