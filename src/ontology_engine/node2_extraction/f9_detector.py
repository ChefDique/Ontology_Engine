"""
F9 Note Detector — TASK_B6

Detects Xactimate F9 override notes that modify standard line item values.
Flags but NEVER auto-resolves — routes to HITL gate (CONST_004).

Design by Contract:
  Invariant: F9 collisions are FLAGGED, never auto-resolved.
"""


def detect_f9_overrides(line_items: list[dict]) -> list[dict]:
    """Flag line items with F9 override notes.

    Returns: list of flagged items with has_override_note=True
    """
    raise NotImplementedError("TASK_B6: F9 note collision detection")
