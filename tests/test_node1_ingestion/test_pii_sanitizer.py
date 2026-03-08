"""Tests for Node 1 — PII Sanitizer (TASK_A2)."""

import pytest

from ontology_engine.node1_ingestion.pii_sanitizer import redact_pii, _regex_redact


# ---------- Core redaction tests ----------

class TestRedactPII:
    def test_empty_string(self):
        result = redact_pii("")
        assert result["redacted_text"] == ""
        assert result["pii_count"] == 0
        assert result["pii_found"] == []

    def test_whitespace_only(self):
        result = redact_pii("   \n\t  ")
        assert result["pii_count"] == 0

    def test_no_pii_text_unchanged(self):
        text = "Remove and replace comp shingles - 32.33 SQ at $185.50"
        result = redact_pii(text)
        assert result["pii_count"] == 0
        assert result["redacted_text"] == text

    def test_ssn_redacted(self):
        text = "Policyholder SSN: 123-45-6789"
        result = redact_pii(text)
        assert "123-45-6789" not in result["redacted_text"]
        assert result["pii_count"] >= 1

    def test_email_redacted(self):
        text = "Contact: john.doe@example.com for questions"
        result = redact_pii(text)
        assert "john.doe@example.com" not in result["redacted_text"]
        assert result["pii_count"] >= 1

    def test_phone_redacted(self):
        text = "Call us at (808) 555-1234 for claims"
        result = redact_pii(text)
        assert "555-1234" not in result["redacted_text"]
        assert result["pii_count"] >= 1

    def test_policy_number_redacted(self):
        text = "Policy: POL-12345678 effective 2026-01-01"
        result = redact_pii(text)
        assert "POL-12345678" not in result["redacted_text"]
        assert result["pii_count"] >= 1

    def test_multiple_pii_types_redacted(self):
        text = (
            "Insured: John Smith, SSN 123-45-6789, "
            "Policy POL-99887766, email john@example.com"
        )
        result = redact_pii(text)
        assert "123-45-6789" not in result["redacted_text"]
        assert "john@example.com" not in result["redacted_text"]
        assert "POL-99887766" not in result["redacted_text"]
        assert result["pii_count"] >= 3

    def test_output_structure(self):
        result = redact_pii("Test text with SSN 123-45-6789")
        assert "redacted_text" in result
        assert "pii_found" in result
        assert "pii_count" in result
        assert isinstance(result["pii_found"], list)
        assert isinstance(result["pii_count"], int)

    def test_pii_found_entries_have_type(self):
        result = redact_pii("SSN: 123-45-6789")
        if result["pii_count"] > 0:
            for entry in result["pii_found"]:
                assert "type" in entry


# ---------- Regex fallback tests ----------

class TestRegexRedact:
    def test_ssn_pattern(self):
        redacted, findings = _regex_redact("SSN is 123-45-6789 here")
        assert "123-45-6789" not in redacted
        assert any(f["type"] == "SSN" for f in findings)

    def test_email_pattern(self):
        redacted, findings = _regex_redact("Email: test@domain.com")
        assert "test@domain.com" not in redacted
        assert any(f["type"] == "EMAIL_ADDRESS" for f in findings)

    def test_phone_pattern(self):
        redacted, findings = _regex_redact("Phone: 808-555-0100")
        assert "808-555-0100" not in redacted
        assert any(f["type"] == "PHONE_NUMBER" for f in findings)

    def test_claim_number_pattern(self):
        redacted, findings = _regex_redact("Claim: 2026-ABC-12345678")
        assert "2026-ABC-12345678" not in redacted
        assert any(f["type"] == "CLAIM_NUMBER" for f in findings)

    def test_no_false_positives_on_xactimate_data(self):
        """Ensure construction-specific numbers aren't flagged as PII."""
        text = "32.33 SQ shingles at $185.50/SQ = $5,997.22 RCV"
        redacted, findings = _regex_redact(text)
        # Construction quantities and prices should NOT be redacted
        assert "32.33" in redacted
        assert "$185.50" in redacted


# ---------- CONST_001 enforcement ----------

class TestConst001:
    """Verify CONST_001: ZERO PII in output — no exceptions."""

    def test_ssn_never_leaks(self):
        text = "Multiple SSNs: 123-45-6789, 987-65-4321, 111-22-3333"
        result = redact_pii(text)
        assert "123-45-6789" not in result["redacted_text"]
        assert "987-65-4321" not in result["redacted_text"]
        assert "111-22-3333" not in result["redacted_text"]

    def test_mixed_pii_in_estimate_context(self):
        text = """
        Xactimate Estimate #XM-2026-001
        Insured: Jane Doe
        Address: 123 Aloha St, Honolulu HI 96815
        Phone: (808) 555-9876
        SSN: 999-88-7777
        Policy: HO-12345678

        Line Items:
        RFG - Remove & replace comp shingles - 32.33 SQ - $185.50
        """
        result = redact_pii(text)
        # PII must be gone
        assert "999-88-7777" not in result["redacted_text"]
        assert "(808) 555-9876" not in result["redacted_text"]
        assert "HO-12345678" not in result["redacted_text"]
        # Construction data must survive
        assert "32.33" in result["redacted_text"]
        assert "185.50" in result["redacted_text"]
