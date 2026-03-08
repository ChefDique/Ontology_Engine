"""
O&P Stripper — TASK_B4

Strips Overhead & Profit (O&P) margins from Xactimate totals
before CRM injection to prevent double-taxation (CONST_002).

Design by Contract:
  Invariant: O&P NEVER applied twice. Node 3 strips O&P;
             CRM applies its own independently.
"""


def strip_overhead_and_profit(totals: dict, line_items: list[dict]) -> dict:
    """Remove O&P from Xactimate financial totals.

    Xactimate typically applies 10% Overhead + 10% Profit.
    These must be stripped before pushing to CRM.

    Returns:
        dict with keys:
            - adjusted_totals: dict (O&P removed)
            - stripped_overhead: float
            - stripped_profit: float
            - stripped_tax: float
    """
    raise NotImplementedError("TASK_B4: O&P stripping logic")
