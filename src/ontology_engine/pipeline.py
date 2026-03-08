"""
Pipeline Orchestrator — Chains Node 1 → Node 2 → Node 3 → Node 4.

Design by Contract: Each node's output is validated against the inter-node
JSON schema before being passed to the next node. If validation fails,
the pipeline halts and routes to the HITL review queue.
"""

import logging
import time
from pathlib import Path

import jsonschema

from ontology_engine.config import CONFIDENCE_THRESHOLD
from ontology_engine.contracts.schemas import (
    NODE_1_TO_2_SCHEMA,
    NODE_2_TO_3_SCHEMA,
    NODE_3_TO_4_SCHEMA,
)

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Raised when the pipeline encounters an unrecoverable error."""

    pass


class ContractViolationError(PipelineError):
    """Raised when inter-node contract validation fails."""

    def __init__(self, source_node: str, target_node: str, message: str):
        self.source_node = source_node
        self.target_node = target_node
        super().__init__(
            f"Contract violation ({source_node}→{target_node}): {message}"
        )


def _validate_contract(data: dict, schema: dict, source: str, target: str) -> None:
    """Validate data against an inter-node JSON schema.

    Raises:
        ContractViolationError: If data does not conform to the schema.
    """
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        raise ContractViolationError(source, target, e.message) from e


def _build_hitl_flags(node3_output: dict, confidence: float) -> list[dict]:
    """Extract items requiring human review.

    HITL flags are generated for:
    - F9 override notes (has_override_note=True in original extraction)
    - Low extraction confidence (below CONFIDENCE_THRESHOLD)
    - Credit/return items (negative quantities routed to credit_items)
    """
    flags = []

    # Flag credit items
    for item in node3_output.get("credit_items", []):
        flags.append({
            "type": "credit_return",
            "item": item,
            "reason": "Negative quantity routed as credit/return",
        })

    # Flag low confidence
    if confidence < CONFIDENCE_THRESHOLD:
        flags.append({
            "type": "low_confidence",
            "confidence": confidence,
            "threshold": CONFIDENCE_THRESHOLD,
            "reason": f"Extraction confidence {confidence:.2f} below threshold {CONFIDENCE_THRESHOLD}",
        })

    return flags


def _get_adapter(target_crm: str):
    """Get the CRM adapter for the target system.

    Args:
        target_crm: One of 'buildertrend', 'jobnimbus', 'acculynx'.

    Returns:
        An instance of the appropriate BaseCRMAdapter subclass.

    Raises:
        PipelineError: If target_crm is not recognized.
    """
    target_crm = target_crm.lower().strip()

    if target_crm == "buildertrend":
        from ontology_engine.node4_output.buildertrend_csv import BuildertrendAdapter
        return BuildertrendAdapter()
    elif target_crm == "jobnimbus":
        from ontology_engine.node4_output.jobnimbus_qbo import JobNimbusAdapter
        return JobNimbusAdapter()
    elif target_crm == "acculynx":
        from ontology_engine.node4_output.acculynx_api import AccuLynxAdapter
        return AccuLynxAdapter()
    else:
        raise PipelineError(
            f"Unknown target CRM: '{target_crm}'. "
            f"Supported: buildertrend, jobnimbus, acculynx"
        )


def run_pipeline(input_path: Path, target_crm: str, output_dir: Path | None = None) -> dict:
    """Execute the full Ontology Engine pipeline.

    Pipeline flow:
        Node 1 (Ingestion) → contract → Node 2 (Extraction)
        → contract → Node 3 (Calculus) → contract → Node 4 (Output)

    At each boundary, data is validated against the inter-node JSON schema.
    Items flagged for human review are collected but do NOT block the pipeline —
    they are returned alongside the output for HITL processing.

    Args:
        input_path: Path to input PDF or image file.
        target_crm: Target CRM identifier ('buildertrend', 'jobnimbus', 'acculynx').
        output_dir: Directory for output files. Defaults to input_path's parent.

    Returns:
        dict with keys:
            - success: bool
            - output_path: Path to generated output file (CSV or JSON)
            - hitl_items: list of items flagged for human review
            - metadata: pipeline execution metadata
    """
    from ontology_engine.node1_ingestion import ingest
    from ontology_engine.node2_extraction.extractor import extract_estimate
    from ontology_engine.node3_calculus.roofer_math import calculate_material_quantities
    from ontology_engine.node3_calculus.oop_stripper import strip_overhead_and_profit
    from ontology_engine.node3_calculus.credit_handler import handle_credits

    input_path = Path(input_path)
    if output_dir is None:
        output_dir = input_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "input_file": str(input_path),
        "target_crm": target_crm,
        "start_time": time.time(),
        "nodes_completed": [],
    }

    # ── Node 1: Ingestion ──────────────────────────────────────────────
    logger.info("Node 1: Ingesting %s", input_path.name)
    node1_output = ingest(input_path)
    # ingest() already validates against NODE_1_TO_2_SCHEMA internally,
    # but we validate again at the boundary for defense-in-depth.
    _validate_contract(node1_output, NODE_1_TO_2_SCHEMA, "Node1", "Node2")
    metadata["nodes_completed"].append("node1_ingestion")
    metadata["extraction_method"] = node1_output["method"]
    metadata["page_count"] = node1_output["page_count"]
    extraction_confidence = node1_output["confidence"]
    logger.info(
        "Node 1 complete: method=%s, pages=%d, confidence=%.2f",
        node1_output["method"],
        node1_output["page_count"],
        extraction_confidence,
    )

    # ── Node 2: Semantic Extraction ────────────────────────────────────
    logger.info("Node 2: Extracting structured data via LLM")
    node2_output = extract_estimate(node1_output["chunks"])
    _validate_contract(node2_output, NODE_2_TO_3_SCHEMA, "Node2", "Node3")
    metadata["nodes_completed"].append("node2_extraction")
    metadata["line_item_count"] = len(node2_output.get("line_items", []))
    logger.info(
        "Node 2 complete: %d line items extracted",
        metadata["line_item_count"],
    )

    # ── Node 3: Deterministic Calculus ─────────────────────────────────
    logger.info("Node 3: Calculating material quantities + O&P stripping")

    # 3a: Material quantity conversion (Xactimate units → physical)
    procurement_items = calculate_material_quantities(
        node2_output["line_items"]
    )

    # 3b: O&P stripping (CONST_002)
    oop_result = strip_overhead_and_profit(
        node2_output["totals"],
        node2_output["line_items"],
    )

    # 3c: Credit handling (CONST_003)
    credit_result = handle_credits(procurement_items)

    # Build Node 3 output conforming to NODE_3_TO_4_SCHEMA
    node3_output = {
        "header": node2_output.get("header", {}),
        "procurement_items": credit_result["procurement_items"],
        "credit_items": credit_result["credit_items"],
        "adjusted_totals": oop_result["adjusted_totals"],
        "hitl_flags": [],  # Populated below
    }

    # Build HITL flags
    hitl_flags = _build_hitl_flags(node3_output, extraction_confidence)
    node3_output["hitl_flags"] = hitl_flags

    _validate_contract(node3_output, NODE_3_TO_4_SCHEMA, "Node3", "Node4")
    metadata["nodes_completed"].append("node3_calculus")
    metadata["procurement_count"] = len(credit_result["procurement_items"])
    metadata["credit_count"] = len(credit_result["credit_items"])
    logger.info(
        "Node 3 complete: %d procurement, %d credits, %d HITL flags",
        metadata["procurement_count"],
        metadata["credit_count"],
        len(hitl_flags),
    )

    # ── Node 4: Output Routing ─────────────────────────────────────────
    logger.info("Node 4: Routing to %s", target_crm)
    adapter = _get_adapter(target_crm)

    formatted = adapter.format_output(node3_output)

    # Determine output filename
    estimate_num = node3_output.get("header", {}).get("estimate_number", "output")
    ext = ".csv" if target_crm == "buildertrend" else ".json"
    output_path = output_dir / f"{estimate_num}_{target_crm}{ext}"

    export_path = adapter.export(formatted, output_path)
    is_valid = adapter.validate_output(formatted)

    metadata["nodes_completed"].append("node4_output")
    metadata["output_valid"] = is_valid
    metadata["end_time"] = time.time()
    metadata["duration_seconds"] = round(
        metadata["end_time"] - metadata["start_time"], 2
    )

    logger.info(
        "Pipeline complete: %s → %s (%.1fs, valid=%s)",
        input_path.name,
        export_path,
        metadata["duration_seconds"],
        is_valid,
    )

    # ── Queue HITL items if any ────────────────────────────────────────
    hitl_items = []
    if hitl_flags:
        from ontology_engine.hitl.review_queue import queue_for_review
        for flag in hitl_flags:
            queued = queue_for_review([flag], reason=flag["type"])
            hitl_items.append(queued)
        logger.info("HITL: %d items queued for human review", len(hitl_items))

    return {
        "success": True,
        "output_path": str(export_path),
        "hitl_items": hitl_items,
        "metadata": metadata,
    }
