"""
TASK_J1 — Supplement Report Output Schema

Defines the JSON Schema for the Node 6 output: a structured supplement report
that is both machine-parseable and human-readable.

Input:  NODE_5_OUTPUT_SCHEMA (gap report from comparator)
Output: NODE_6_REPORT_SCHEMA (supplement report for carrier submission)
"""

# Schema: Node 6 Output — Supplement Report
NODE_6_REPORT_SCHEMA = {
    "type": "object",
    "required": [
        "report_metadata",
        "executive_summary",
        "category_narratives",
        "financial_summary",
        "op_narrative",
        "depreciation_narrative",
        "recommended_actions",
    ],
    "properties": {
        "report_metadata": {
            "type": "object",
            "required": ["report_type", "generated_at", "source_gap_report_id"],
            "properties": {
                "report_type": {
                    "type": "string",
                    "const": "supplement_report",
                },
                "generated_at": {"type": "string", "format": "date-time"},
                "source_gap_report_id": {
                    "type": ["string", "null"],
                    "description": "Reference to the Node 5 gap report",
                },
                "claim_number": {"type": ["string", "null"]},
                "estimate_number": {"type": ["string", "null"]},
                "carrier": {"type": ["string", "null"]},
            },
        },
        "executive_summary": {
            "type": "object",
            "required": [
                "total_recovery_estimate",
                "adjuster_rcv",
                "contractor_rcv",
                "total_delta",
                "gap_count",
                "narrative",
            ],
            "properties": {
                "total_recovery_estimate": {
                    "type": "number",
                    "description": "Total projected recovery (line items + O&P + depreciation)",
                },
                "adjuster_rcv": {"type": "number"},
                "contractor_rcv": {"type": "number"},
                "total_delta": {"type": "number"},
                "gap_count": {"type": "integer", "minimum": 0},
                "narrative": {
                    "type": "string",
                    "description": "Human-readable executive summary paragraph",
                },
            },
        },
        "category_narratives": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "gap_count", "total_impact", "narrative"],
                "properties": {
                    "category": {"type": "string"},
                    "category_label": {
                        "type": "string",
                        "description": "Human-readable category name",
                    },
                    "gap_count": {"type": "integer", "minimum": 0},
                    "total_impact": {"type": "number"},
                    "gaps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "gap_type": {"type": "string"},
                                "description": {"type": "string"},
                                "impact": {"type": ["number", "null"]},
                                "detail": {"type": "string"},
                            },
                        },
                    },
                    "narrative": {
                        "type": "string",
                        "description": "Human-readable narrative for this category",
                    },
                },
            },
        },
        "financial_summary": {
            "type": "object",
            "required": [
                "line_item_recovery",
                "op_recovery",
                "depreciation_recovery",
                "total_recovery",
                "by_category",
            ],
            "properties": {
                "line_item_recovery": {
                    "type": "number",
                    "description": "Total recovery from line item gaps (missing + qty + price)",
                },
                "op_recovery": {
                    "type": "number",
                    "description": "Recovery from O&P correction",
                },
                "depreciation_recovery": {
                    "type": "number",
                    "description": "Recovery from depreciation audit findings",
                },
                "total_recovery": {
                    "type": "number",
                    "description": "Sum of all recovery categories",
                },
                "by_category": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["category", "category_label", "amount"],
                        "properties": {
                            "category": {"type": "string"},
                            "category_label": {"type": "string"},
                            "amount": {"type": "number"},
                            "pct_of_total": {"type": "number"},
                        },
                    },
                },
            },
        },
        "op_narrative": {
            "type": "object",
            "required": ["applicable", "narrative"],
            "properties": {
                "applicable": {"type": "boolean"},
                "trade_count": {"type": "integer"},
                "trades": {"type": "array", "items": {"type": "string"}},
                "recovery_amount": {"type": "number"},
                "narrative": {"type": "string"},
            },
        },
        "depreciation_narrative": {
            "type": "object",
            "required": ["has_findings", "narrative"],
            "properties": {
                "has_findings": {"type": "boolean"},
                "finding_count": {"type": "integer"},
                "total_recoverable": {"type": "number"},
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "depreciation_pct": {"type": "number"},
                            "flag_reason": {"type": "string"},
                            "recoverable": {"type": ["number", "null"]},
                        },
                    },
                },
                "narrative": {"type": "string"},
            },
        },
        "recommended_actions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["priority", "action", "expected_recovery"],
                "properties": {
                    "priority": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "1 = highest priority",
                    },
                    "action": {"type": "string"},
                    "category": {"type": "string"},
                    "expected_recovery": {"type": "number"},
                    "rationale": {"type": "string"},
                },
            },
        },
    },
}
