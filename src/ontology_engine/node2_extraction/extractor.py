"""
Semantic Extractor — TASK_B2

Orchestrates LLM calls for structured data extraction from Xactimate text.
Validates output against the rigid extraction schema.

Design by Contract:
  Precondition:  Input must be PII-redacted text chunks (pii_redacted=True).
  Postcondition: Output conforms to NODE_2_TO_3_SCHEMA.
  Invariant:     LLM NEVER calculates — raw extraction only.
"""

import json
import logging

import jsonschema

from .prompt import (
    EXTRACTION_OUTPUT_SCHEMA,
    EXTRACTION_SYSTEM_PROMPT,
    EXTRACTION_USER_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Raised when LLM extraction fails or produces invalid output."""
    pass


def extract_estimate(text_chunks: list[dict], provider: str = "openai") -> dict:
    """Extract structured Xactimate data from PII-redacted text chunks.

    Concatenates chunk text, sends to LLM with rigid system prompt,
    and validates the response against EXTRACTION_OUTPUT_SCHEMA.

    Args:
        text_chunks: List of chunk dicts with 'chunk_text' keys.
        provider: LLM provider name (for future multi-provider support).

    Returns:
        dict conforming to NODE_2_TO_3_SCHEMA (header, line_items, totals).

    Raises:
        ExtractionError: If LLM output fails schema validation.
    """
    # Concatenate all chunks into a single text block
    full_text = "\n".join(chunk["chunk_text"] for chunk in text_chunks)

    # Build the user prompt
    user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(estimate_text=full_text)

    # Call the LLM (provider-agnostic stub — actual API wiring is deferred)
    raw_response = _call_llm(
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        provider=provider,
    )

    # Parse and validate
    extraction = _parse_llm_response(raw_response)
    _validate_extraction(extraction)

    logger.info(
        "Extraction complete: %d line items, estimate #%s",
        len(extraction.get("line_items", [])),
        extraction.get("header", {}).get("estimate_number", "unknown"),
    )

    return extraction


def _call_llm(system_prompt: str, user_prompt: str, provider: str) -> str:
    """Call LLM provider for extraction.

    This is a provider-agnostic stub. Actual API integration (OpenAI,
    Anthropic, Google) will be wired in a separate task.

    Returns: Raw string response from LLM.
    """
    # NOTE: This stub exists so the extraction pipeline can be fully tested
    # with mocked LLM responses. The actual provider wiring happens at
    # integration time and depends on config.py settings.
    raise NotImplementedError(
        f"LLM provider '{provider}' not yet wired. "
        "Mock this function for testing."
    )


def _parse_llm_response(raw_response: str) -> dict:
    """Parse raw LLM response string into a dict.

    Handles common LLM output quirks:
    - Strips markdown code fences (```json ... ```)
    - Handles leading/trailing whitespace

    Raises:
        ExtractionError: If response is not valid JSON.
    """
    cleaned = raw_response.strip()

    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ExtractionError(f"LLM returned invalid JSON: {e}") from e


def _validate_extraction(data: dict) -> None:
    """Validate extracted data against the rigid schema.

    Raises:
        ExtractionError: If data does not conform to schema.
    """
    try:
        jsonschema.validate(instance=data, schema=EXTRACTION_OUTPUT_SCHEMA)
    except jsonschema.ValidationError as e:
        raise ExtractionError(
            f"Extraction output failed schema validation: {e.message}"
        ) from e
