"""
Deduplication Logic — TASK_G4

Appends unique identifiers to prevent CRM import errors.
JobNimbus throws fatal errors on duplicate Display Names.

Design by Contract:
  Precondition:  records is a list of dicts; job_id is a non-empty string.
  Postcondition: Every returned record has a 'unique_id' key with a
                 value that is unique within the batch.
"""

from datetime import datetime, timezone


def deduplicate(
    records: list[dict],
    job_id: str,
    *,
    timestamp: str | None = None,
) -> list[dict]:
    """Append unique identifiers to prevent CRM deduplication errors.

    Strategy: Each record gets a unique_id composed of
        job_id + compact_timestamp + index

    This guarantees uniqueness *within* a single export run AND across
    repeated runs for the same job.

    Args:
        records:   List of procurement item dicts from Node 3.
        job_id:    Xactimate estimate number (or other job identifier).
        timestamp: Optional ISO-format timestamp override (for testing).
                   Defaults to current UTC time.

    Returns:
        Shallow-copied list of dicts, each with a 'unique_id' key added.
    """
    if not job_id:
        raise ValueError("job_id must be non-empty for deduplication")

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    deduped: list[dict] = []
    seen_ids: set[str] = set()

    for idx, record in enumerate(records):
        new_record = {**record}  # shallow copy to avoid mutating input
        uid = f"{job_id}-{timestamp}-{idx:04d}"

        # Defensive: should never happen, but guarantee uniqueness
        if uid in seen_ids:
            uid = f"{uid}-dup"
        seen_ids.add(uid)

        new_record["unique_id"] = uid
        deduped.append(new_record)

    return deduped
