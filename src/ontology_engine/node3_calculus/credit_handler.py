"""
Credit Handler — TASK_B5

Routes negative quantities (insurance supplement credits/deductions)
to a separate data path (CONST_003).

Design by Contract:
  Invariant: Negative quantities → transaction_type: 'credit_return', never errors.
"""


def handle_credits(line_items: list[dict]) -> dict:
    """Separate credit/return items from standard procurement items.

    Returns:
        dict with keys:
            - procurement_items: list (positive quantities)
            - credit_items: list (negative quantities, flagged as credit_return)
    """
    raise NotImplementedError("TASK_B5: Negative quantity routing")
