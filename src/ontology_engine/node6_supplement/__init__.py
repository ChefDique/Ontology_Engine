"""
Node 6 — Supplement Report Generator

Transforms Node 5's structured gap report into a human-readable
supplement narrative suitable for submission to insurance carriers.

Architecture:
    Node 5 (Gap Report) → Node 6 (Supplement Report) → Node 4 (Output Routing)

Components:
    - report_generator: Main orchestrator — delegates to formatters
    - narrative_formatter: Converts gap categories to prose narratives
    - dollar_summarizer: Aggregates financial impact per category and total
"""

from .report_generator import generate_supplement_report

__all__ = ["generate_supplement_report"]
