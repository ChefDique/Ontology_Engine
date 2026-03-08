"""
Review Queue — CONST_005

Holds low-confidence or F9-flagged items for human approval
before they proceed to Node 4 output.

Design by Contract:
  Invariant: NEVER auto-POST to CRM. Human must explicitly approve.
"""


def queue_for_review(items: list[dict], reason: str) -> dict:
    """Add items to the HITL review queue.

    Returns:
        dict with keys:
            - queued_items: list
            - queue_id: str
            - reason: str ('f9_override' | 'low_confidence' | 'negative_quantity')
    """
    raise NotImplementedError("CONST_005: HITL review queue")
