"""
Inter-Node JSON Schemas — Design by Contract

These schemas define the data contracts between pipeline nodes.
Every node's output MUST validate against the next node's input schema
before data flows forward.

This is the communication layer between parallel workstream agents.
"""

# Schema: Node 1 → Node 2 (Ingestion output → Extraction input)
NODE_1_TO_2_SCHEMA = {
    "type": "object",
    "required": ["text", "method", "confidence", "page_count", "pii_redacted"],
    "properties": {
        "text": {"type": "string", "minLength": 1},
        "method": {"type": "string", "enum": ["native", "ocr"]},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "page_count": {"type": "integer", "minimum": 1},
        "pii_redacted": {"type": "boolean", "const": True},
        "chunks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["chunk_text", "chunk_index", "token_count"],
                "properties": {
                    "chunk_text": {"type": "string"},
                    "chunk_index": {"type": "integer"},
                    "token_count": {"type": "integer"},
                },
            },
        },
    },
}

# Schema: Node 2 → Node 3 (Extraction output → Calculus input)
NODE_2_TO_3_SCHEMA = {
    "type": "object",
    "required": ["header", "line_items", "totals"],
    "properties": {
        "header": {
            "type": "object",
            "properties": {
                "estimate_number": {"type": "string"},
                "claim_number": {"type": ["string", "null"]},
                "carrier": {"type": ["string", "null"]},
                "loss_date": {"type": ["string", "null"]},
            },
        },
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "description", "quantity", "unit_of_measure"],
                "properties": {
                    "category": {"type": "string"},
                    "selector": {"type": "string"},
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_of_measure": {"type": "string"},
                    "unit_price": {"type": "number"},
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

# Schema: Node 3 → Node 4 (Calculus output → Output Routing input)
NODE_3_TO_4_SCHEMA = {
    "type": "object",
    "required": ["header", "procurement_items", "adjusted_totals"],
    "properties": {
        "header": {"type": "object"},
        "procurement_items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "description", "physical_qty", "physical_unit", "trade"],
                "properties": {
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                    "physical_qty": {"type": "integer", "minimum": 1},
                    "physical_unit": {"type": "string"},
                    "trade": {"type": "string"},
                    "unit_cost": {"type": "number"},
                },
            },
        },
        "credit_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "transaction_type": {"type": "string", "const": "credit_return"},
                },
            },
        },
        "adjusted_totals": {
            "type": "object",
            "description": "Totals with O&P stripped",
        },
        "hitl_flags": {
            "type": "array",
            "description": "Items requiring human review (F9 overrides, low confidence)",
        },
    },
}

# Schema: Node 5 Input (Two Node 3 outputs → Comparator)
NODE_5_INPUT_SCHEMA = {
    "type": "object",
    "required": ["adjuster_estimate", "contractor_estimate"],
    "properties": {
        "adjuster_estimate": {
            "$ref": "#/$defs/node3_output",
            "description": "Insurance adjuster's estimate (processed through Nodes 1-3)",
        },
        "contractor_estimate": {
            "$ref": "#/$defs/node3_output",
            "description": "Contractor's estimate (processed through Nodes 1-3)",
        },
    },
    "$defs": {
        "node3_output": {
            "type": "object",
            "required": ["header", "procurement_items", "adjusted_totals"],
            "properties": {
                "header": {"type": "object"},
                "procurement_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["category", "description", "physical_qty", "physical_unit", "trade"],
                        "properties": {
                            "category": {"type": "string"},
                            "description": {"type": "string"},
                            "physical_qty": {"type": "number"},
                            "physical_unit": {"type": "string"},
                            "trade": {"type": "string"},
                            "unit_cost": {"type": "number"},
                        },
                    },
                },
                "credit_items": {"type": "array"},
                "adjusted_totals": {
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
                "hitl_flags": {"type": "array"},
            },
        },
    },
}

# Schema: Node 5 → Node 6 (Gap Report → Supplement Report)
NODE_5_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["summary", "line_item_gaps", "op_analysis", "depreciation_findings"],
    "properties": {
        "summary": {
            "type": "object",
            "required": ["adjuster_rcv", "contractor_rcv", "total_delta", "gap_count"],
            "properties": {
                "adjuster_rcv": {"type": "number"},
                "contractor_rcv": {"type": "number"},
                "total_delta": {"type": "number"},
                "gap_count": {"type": "integer", "minimum": 0},
                "adjuster_line_count": {"type": "integer"},
                "contractor_line_count": {"type": "integer"},
            },
        },
        "line_item_gaps": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["gap_type", "description"],
                "properties": {
                    "gap_type": {
                        "type": "string",
                        "enum": ["missing_item", "quantity_delta", "pricing_delta"],
                    },
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                    "contractor_qty": {"type": ["number", "null"]},
                    "adjuster_qty": {"type": ["number", "null"]},
                    "quantity_delta": {"type": ["number", "null"]},
                    "quantity_delta_pct": {"type": ["number", "null"]},
                    "contractor_total": {"type": ["number", "null"]},
                    "adjuster_total": {"type": ["number", "null"]},
                    "pricing_delta": {"type": ["number", "null"]},
                    "trade": {"type": "string"},
                },
            },
        },
        "op_analysis": {
            "type": "object",
            "required": ["trade_count", "op_warranted", "adjuster_op_applied", "contractor_op_applied"],
            "properties": {
                "trade_count": {"type": "integer", "minimum": 0},
                "op_warranted": {"type": "boolean"},
                "adjuster_op_applied": {
                    "type": "object",
                    "properties": {
                        "overhead": {"type": "number"},
                        "profit": {"type": "number"},
                    },
                },
                "contractor_op_applied": {
                    "type": "object",
                    "properties": {
                        "overhead": {"type": "number"},
                        "profit": {"type": "number"},
                    },
                },
                "op_recovery_amount": {"type": "number"},
                "trades_detected": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        },
        "depreciation_findings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description", "depreciation_pct"],
                "properties": {
                    "category": {"type": "string"},
                    "description": {"type": "string"},
                    "depreciation_pct": {"type": "number"},
                    "flagged": {"type": "boolean"},
                    "flag_reason": {"type": "string"},
                    "recoverable_amount": {"type": ["number", "null"]},
                },
            },
        },
    },
}
