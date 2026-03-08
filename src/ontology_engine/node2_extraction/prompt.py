"""
LLM System Prompt — TASK_B1 + TASK_B2

The system instruction for semantic extraction. The LLM ingests PII-redacted
Xactimate text and outputs a rigid JSON schema.

Design by Contract:
  Invariant: LLM NEVER performs arithmetic. LLM NEVER invents data not in source.
"""

# ─── TASK_B1: Rigid JSON Extraction Schema ───────────────────────────────────

# Valid Xactimate category codes the LLM should map to
VALID_CATEGORY_CODES = [
    "RFG", "SID", "DRY", "PLM", "ELC", "FLR", "PNT", "GUT",
    "WDW", "DOR", "INS", "CLN", "DEM", "FNC", "CAB", "CNT",
    "APL", "HVC", "LND", "MSN", "FRM", "CON",
]

# Valid units of measure from Xactimate
VALID_UNITS = ["SQ", "LF", "SF", "EA", "CF", "SY", "HR", "DAY"]

# The JSON schema the LLM must produce — used for validation
EXTRACTION_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["header", "line_items", "totals"],
    "properties": {
        "header": {
            "type": "object",
            "required": ["estimate_number"],
            "properties": {
                "estimate_number": {"type": "string", "minLength": 1},
                "claim_number": {"type": ["string", "null"]},
                "carrier": {"type": ["string", "null"]},
                "property_address": {"type": "string", "const": "REDACTED"},
                "loss_date": {"type": ["string", "null"]},
            },
        },
        "line_items": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": [
                    "category", "description", "quantity",
                    "unit_of_measure",
                ],
                "properties": {
                    "category": {"type": "string", "enum": VALID_CATEGORY_CODES},
                    "selector": {"type": "string"},
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_of_measure": {"type": "string", "enum": VALID_UNITS},
                    "unit_price": {"type": "number", "minimum": 0},
                    "total": {"type": "number"},
                    "has_override_note": {"type": "boolean"},
                    "f9_note_text": {"type": ["string", "null"]},
                },
            },
        },
        "totals": {
            "type": "object",
            "properties": {
                "rcv": {"type": "number"},
                "depreciation": {"type": "number"},
                "acv": {"type": "number"},
                "overhead": {"type": "number"},
                "profit": {"type": "number"},
                "tax": {"type": "number"},
                "net_claim": {"type": "number"},
            },
        },
    },
}

# ─── TASK_B2: LLM System Prompt ──────────────────────────────────────────────

EXTRACTION_SYSTEM_PROMPT = """\
You are a data extraction agent for Xactimate insurance estimates.

RULES:
1. Extract ONLY data that exists in the source text. NEVER invent values.
2. NEVER perform any mathematical calculations. Extract raw values only.
3. Map each line item to its Xactimate category code (RFG, SID, DRY, etc.).
4. Flag any line item with an F9 override note as has_override_note: true.
5. Output MUST conform to the JSON schema provided.
6. If property_address is present, replace with "REDACTED" (PII contract).
7. Use null for any field you cannot confidently extract.
8. Preserve exact numerical values from source — do NOT round or recalculate.

VALID CATEGORY CODES: {codes}

VALID UNITS: {units}

OUTPUT FORMAT:
{{
    "header": {{
        "estimate_number": "string",
        "claim_number": "string | null",
        "carrier": "string | null",
        "property_address": "REDACTED",
        "loss_date": "YYYY-MM-DD | null"
    }},
    "line_items": [
        {{
            "category": "RFG | SID | DRY | ...",
            "selector": "string",
            "description": "string",
            "quantity": float,
            "unit_of_measure": "SQ | LF | SF | EA | ...",
            "unit_price": float,
            "total": float,
            "has_override_note": bool,
            "f9_note_text": "string | null"
        }}
    ],
    "totals": {{
        "rcv": float,
        "depreciation": float,
        "acv": float,
        "overhead": float,
        "profit": float,
        "tax": float,
        "net_claim": float
    }}
}}
""".format(codes=", ".join(VALID_CATEGORY_CODES), units=", ".join(VALID_UNITS))

EXTRACTION_USER_PROMPT_TEMPLATE = """\
Extract structured data from the following Xactimate estimate text.
Return ONLY valid JSON conforming to the schema above. No commentary.

--- BEGIN ESTIMATE TEXT ---
{estimate_text}
--- END ESTIMATE TEXT ---
"""
