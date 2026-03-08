"""
Credit Handler — TASK_B5

Routes negative quantities (insurance supplement credits/deductions)
to a separate data path (CONST_003).

Design by Contract:
  Invariant: Negative quantities → transaction_type: 'credit_return', never errors.
             Zero quantities → excluded from both paths.
"""

import logging

logger = logging.getLogger(__name__)


def handle_credits(line_items: list[dict]) -> dict:
    """Separate credit/return items from standard procurement items.

    Positive quantities → procurement_items (normal material order)
    Negative quantities → credit_items (flagged as credit_return)
    Zero quantities → excluded with warning

    Args:
        line_items: Extracted line items with 'quantity' field.

    Returns:
        dict with keys:
            - procurement_items: list (positive quantities)
            - credit_items: list (negative quantities, flagged as credit_return)
    """
    procurement_items = []
    credit_items = []

    for i, item in enumerate(line_items):
        quantity = item.get("quantity", 0)

        if quantity > 0:
            procurement_items.append(item)
        elif quantity < 0:
            credit_item = {
                **item,
                "transaction_type": "credit_return",
                "original_quantity": quantity,
                "quantity": abs(quantity),  # Store as positive for CRM
            }
            credit_items.append(credit_item)
            logger.info(
                "Credit routed: item %d (%s) qty=%s → credit_return",
                i,
                item.get("category", "?"),
                quantity,
            )
        else:
            logger.warning(
                "Zero-quantity item excluded: item %d (%s) — '%s'",
                i,
                item.get("category", "?"),
                item.get("description", ""),
            )

    logger.info(
        "Credit handling: %d procurement, %d credits, %d zero-excluded",
        len(procurement_items),
        len(credit_items),
        len(line_items) - len(procurement_items) - len(credit_items),
    )

    return {
        "procurement_items": procurement_items,
        "credit_items": credit_items,
    }
