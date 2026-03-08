"""
Ontology Engine CLI — Entry point for pipeline execution.

Usage:
    python -m ontology_engine run <input_pdf> --crm buildertrend [--output-dir ./out]
    python -m ontology_engine hitl list
    python -m ontology_engine hitl approve <queue_id>
    python -m ontology_engine hitl reject <queue_id> --notes "reason"
"""

import argparse
import json
import logging
import sys
from pathlib import Path


def _setup_logging(verbose: bool = False) -> None:
    """Configure logging for CLI output."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute the pipeline."""
    from ontology_engine.pipeline import run_pipeline, PipelineError

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir) if args.output_dir else None

    try:
        result = run_pipeline(
            input_path=input_path,
            target_crm=args.crm,
            output_dir=output_dir,
        )
    except PipelineError as e:
        print(f"Pipeline error: {e}", file=sys.stderr)
        return 1

    # Print summary
    meta = result["metadata"]
    print(f"\n{'='*60}")
    print(f"  Ontology Engine — Pipeline Complete")
    print(f"{'='*60}")
    print(f"  Input:       {meta['input_file']}")
    print(f"  Target CRM:  {meta['target_crm']}")
    print(f"  Output:      {result['output_path']}")
    print(f"  Duration:    {meta.get('duration_seconds', '?')}s")
    print(f"  Pages:       {meta.get('page_count', '?')}")
    print(f"  Line Items:  {meta.get('line_item_count', '?')}")
    print(f"  HITL Items:  {len(result['hitl_items'])}")
    print(f"{'='*60}\n")

    if result["hitl_items"]:
        print("⚠  Items queued for human review:")
        for item in result["hitl_items"]:
            print(f"   - [{item['reason']}] Queue ID: {item['queue_id']}")
        print(f"\nRun: python -m ontology_engine hitl list")

    return 0


def _cmd_hitl_list(args: argparse.Namespace) -> int:
    """List pending HITL review items."""
    from ontology_engine.hitl.review_queue import ReviewQueue

    queue = ReviewQueue()
    pending = queue.list_pending()

    if not pending:
        print("No pending HITL items.")
        return 0

    print(f"\n{'='*60}")
    print(f"  HITL Review Queue — {len(pending)} pending")
    print(f"{'='*60}")
    for entry in pending:
        print(f"\n  Queue ID:   {entry['queue_id']}")
        print(f"  Reason:     {entry['reason']}")
        print(f"  Created:    {entry['created_at']}")
        print(f"  Items:      {len(entry.get('queued_items', []))}")
        if entry.get("source_file"):
            print(f"  Source:     {entry['source_file']}")
    print()

    return 0


def _cmd_hitl_approve(args: argparse.Namespace) -> int:
    """Approve a HITL review item."""
    from ontology_engine.hitl.review_queue import ReviewQueue

    queue = ReviewQueue()
    try:
        entry = queue.approve(args.queue_id, reviewer_notes=args.notes or "")
        print(f"✓ Approved: {entry['queue_id']}")
        return 0
    except FileNotFoundError:
        print(f"Error: Queue entry not found: {args.queue_id}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _cmd_hitl_reject(args: argparse.Namespace) -> int:
    """Reject a HITL review item."""
    from ontology_engine.hitl.review_queue import ReviewQueue

    queue = ReviewQueue()
    try:
        entry = queue.reject(args.queue_id, reviewer_notes=args.notes or "")
        print(f"✗ Rejected: {entry['queue_id']}")
        return 0
    except FileNotFoundError:
        print(f"Error: Queue entry not found: {args.queue_id}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _cmd_hitl_show(args: argparse.Namespace) -> int:
    """Show details of a specific HITL queue entry."""
    from ontology_engine.hitl.review_queue import ReviewQueue

    queue = ReviewQueue()
    try:
        entry = queue.get(args.queue_id)
        print(json.dumps(entry, indent=2, default=str))
        return 0
    except FileNotFoundError:
        print(f"Error: Queue entry not found: {args.queue_id}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ontology_engine",
        description="Ontology Engine — Universal Analog-to-Digital Translation",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── run command ─────────────────────────────────────────────────────
    run_parser = subparsers.add_parser("run", help="Run the pipeline on a PDF")
    run_parser.add_argument("input", help="Path to input PDF or image file")
    run_parser.add_argument(
        "--crm",
        required=True,
        choices=["buildertrend", "jobnimbus", "acculynx"],
        help="Target CRM system",
    )
    run_parser.add_argument(
        "--output-dir", help="Output directory (defaults to input file's directory)"
    )

    # ── hitl command ────────────────────────────────────────────────────
    hitl_parser = subparsers.add_parser("hitl", help="Manage HITL review queue")
    hitl_subparsers = hitl_parser.add_subparsers(dest="hitl_command")

    hitl_subparsers.add_parser("list", help="List pending review items")

    approve_parser = hitl_subparsers.add_parser(
        "approve", help="Approve a review item"
    )
    approve_parser.add_argument("queue_id", help="Queue entry UUID")
    approve_parser.add_argument("--notes", help="Reviewer notes")

    reject_parser = hitl_subparsers.add_parser(
        "reject", help="Reject a review item"
    )
    reject_parser.add_argument("queue_id", help="Queue entry UUID")
    reject_parser.add_argument("--notes", help="Reason for rejection")

    show_parser = hitl_subparsers.add_parser(
        "show", help="Show details of a queue entry"
    )
    show_parser.add_argument("queue_id", help="Queue entry UUID")

    args = parser.parse_args(argv)
    _setup_logging(args.verbose)

    if args.command == "run":
        return _cmd_run(args)
    elif args.command == "hitl":
        if args.hitl_command == "list":
            return _cmd_hitl_list(args)
        elif args.hitl_command == "approve":
            return _cmd_hitl_approve(args)
        elif args.hitl_command == "reject":
            return _cmd_hitl_reject(args)
        elif args.hitl_command == "show":
            return _cmd_hitl_show(args)
        else:
            hitl_parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
