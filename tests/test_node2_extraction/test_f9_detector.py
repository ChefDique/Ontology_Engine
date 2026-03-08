"""Tests for F9 Note Detector — TASK_B6."""

from ontology_engine.node2_extraction.f9_detector import detect_f9_overrides


class TestDetectF9Overrides:
    def test_no_overrides(self):
        items = [
            {"category": "RFG", "description": "Shingles", "has_override_note": False, "f9_note_text": None},
        ]
        assert detect_f9_overrides(items) == []

    def test_flag_set_detected(self):
        items = [
            {"category": "RFG", "description": "Shingles", "has_override_note": True, "f9_note_text": "F9: adjusted"},
        ]
        flags = detect_f9_overrides(items)
        assert len(flags) == 1
        assert flags[0]["resolution"] == "pending"
        assert flags[0]["category"] == "RFG"

    def test_pattern_in_text_without_flag(self):
        """F9 pattern in note text should be detected even without has_override_note."""
        items = [
            {"category": "GUT", "description": "Gutters", "has_override_note": False,
             "f9_note_text": "Price adjusted per local market"},
        ]
        flags = detect_f9_overrides(items)
        assert len(flags) == 1

    def test_multiple_flags(self):
        items = [
            {"category": "RFG", "description": "Shingles", "has_override_note": True, "f9_note_text": "F9 note"},
            {"category": "SID", "description": "Siding", "has_override_note": False, "f9_note_text": None},
            {"category": "GUT", "description": "Gutters", "has_override_note": True, "f9_note_text": "Override"},
        ]
        flags = detect_f9_overrides(items)
        assert len(flags) == 2
        assert flags[0]["item_index"] == 0
        assert flags[1]["item_index"] == 2

    def test_never_auto_resolves(self):
        """CONST_004: resolution must always be 'pending'."""
        items = [
            {"category": "RFG", "description": "X", "has_override_note": True, "f9_note_text": "F9"},
        ]
        flags = detect_f9_overrides(items)
        for flag in flags:
            assert flag["resolution"] == "pending"

    def test_empty_items(self):
        assert detect_f9_overrides([]) == []

    def test_missing_fields_handled(self):
        """Items without override fields should not crash."""
        items = [{"category": "RFG", "description": "Shingles"}]
        flags = detect_f9_overrides(items)
        assert flags == []
