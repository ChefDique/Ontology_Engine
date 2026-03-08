"""
F9 Note Detector — TASK_B6

Detects Xactimate F9 override notes that modify standard line item values.
Flags but NEVER auto-resolves — routes to HITL gate (CONST_004).

Design by Contract:
  Invariant: F9 collisions are FLAGGED, never auto-resolved.
             Items with has_override_note=True get a hitl_flag entry.
"""

import logging

logger = logging.getLogger(__name__)

# F9 note patterns that indicate price overrides
F9_OVERRIDE_PATTERNS = [
    "f9",
    "override",
    "price adjusted",
    "manual adjustment",
    "user modified",
    "locked price",
]


def detect_f9_overrides(line_items: list[dict]) -> list[dict]:
    """Flag line items with F9 override notes.

    Scans each line item for has_override_note=True and/or F9 patterns
    in f9_note_text. Returns a list of HITL flag entries — one per
    flagged item — for inclusion in the output payload.

    NEVER auto-resolves conflicts. Human review is MANDATORY.

    Args:
        line_items: Extracted line items from Node 2.

    Returns:
        list of hitl_flag dicts, each containing:
            - item_index: int (position in line_items)
            - category: str (Xactimate category code)
            - description: str
            - reason: str (why flagged)
            - f9_note_text: str | None
            - resolution: "pending" (always — never auto-resolved)
    """
    flags = []

    for i, item in enumerate(line_items):
        override_detected = item.get("has_override_note", False)
        note_text = item.get("f9_note_text")

        # Also check note text for F9 patterns even if flag not set
        if note_text and not override_detected:
            note_lower = note_text.lower()
            if any(pattern in note_lower for pattern in F9_OVERRIDE_PATTERNS):
                override_detected = True

        if override_detected:
            flag = {
                "item_index": i,
                "category": item.get("category", "UNKNOWN"),
                "description": item.get("description", ""),
                "reason": "F9 override note detected — requires human review",
                "f9_note_text": note_text,
                "resolution": "pending",
            }
            flags.append(flag)
            logger.warning(
                "F9 override flagged: item %d (%s) — %s",
                i,
                item.get("category", "?"),
                note_text or "has_override_note=True",
            )

    if flags:
        logger.info(
            "F9 detection complete: %d items flagged for HITL review",
            len(flags),
        )

    return flags
