"""
Semantic Extractor — TASK_B2 + TASK_G2/G4

Orchestrates LLM calls for structured data extraction from Xactimate text.
Validates output against the rigid extraction schema.

Design by Contract:
  Precondition:  Input must be PII-redacted text chunks (pii_redacted=True).
  Postcondition: Output conforms to NODE_2_TO_3_SCHEMA.
  Invariant:     LLM NEVER calculates — raw extraction only.
"""

import json
import logging
import time

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


class LLMProviderError(Exception):
    """Raised when the LLM provider returns a non-retryable error."""
    pass


class LLMRateLimitError(Exception):
    """Raised when the LLM provider rate-limits the request."""
    pass


def extract_estimate(text_chunks: list[dict], provider: str | None = None) -> dict:
    """Extract structured Xactimate data from PII-redacted text chunks.

    Concatenates chunk text, sends to LLM with rigid system prompt,
    and validates the response against EXTRACTION_OUTPUT_SCHEMA.

    Args:
        text_chunks: List of chunk dicts with 'chunk_text' keys.
        provider: LLM provider name. Defaults to config.LLM_PROVIDER.

    Returns:
        dict conforming to NODE_2_TO_3_SCHEMA (header, line_items, totals).

    Raises:
        ExtractionError: If LLM output fails schema validation.
        LLMProviderError: If the LLM provider returns a fatal error.
    """
    if provider is None:
        try:
            from ..config import LLM_PROVIDER
            provider = LLM_PROVIDER
        except ImportError:
            provider = "gemini"

    # Concatenate all chunks into a single text block
    full_text = "\n".join(chunk["chunk_text"] for chunk in text_chunks)

    # Build the user prompt
    user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(estimate_text=full_text)

    # Call the LLM with retries
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
    """Call LLM provider for extraction with retry logic.

    Dispatches to the appropriate provider backend. Currently supports:
    - 'gemini': Google Gemini Flash via google-generativeai SDK

    Returns: Raw string response from LLM.

    Raises:
        LLMProviderError: On fatal (non-retryable) errors.
        ExtractionError: If all retries exhausted.
    """
    if provider == "gemini":
        return _call_gemini(system_prompt, user_prompt)
    else:
        raise NotImplementedError(
            f"LLM provider '{provider}' not yet wired. "
            "Supported providers: gemini"
        )


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    """Call Google Gemini Flash for extraction with retries.

    Uses the google-generativeai SDK. Handles:
    - Rate limiting (429) with exponential backoff
    - Token overflow detection
    - Safety filter blocks
    - Network/transient errors with retries

    Returns: Raw text response from Gemini.

    Raises:
        LLMProviderError: On API key missing, safety block, or other fatal errors.
        ExtractionError: If all retries exhausted.
    """
    try:
        from ..config import (
            GEMINI_MAX_OUTPUT_TOKENS,
            GEMINI_MAX_RETRIES,
            GEMINI_MODEL,
            GEMINI_RETRY_DELAY,
            GEMINI_TEMPERATURE,
            GOOGLE_API_KEY,
        )
    except ImportError:
        import os
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
        GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
        GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "8192"))
        GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
        GEMINI_RETRY_DELAY = float(os.getenv("GEMINI_RETRY_DELAY", "1.0"))

    if not GOOGLE_API_KEY:
        raise LLMProviderError(
            "GOOGLE_API_KEY not set. Add it to .env or environment variables."
        )

    try:
        import google.generativeai as genai
    except ImportError as e:
        raise LLMProviderError(
            "google-generativeai package not installed. "
            "Run: pip install google-generativeai>=0.5.0"
        ) from e

    # Configure the SDK
    genai.configure(api_key=GOOGLE_API_KEY)

    # Create the model with generation config
    generation_config = genai.GenerationConfig(
        temperature=GEMINI_TEMPERATURE,
        max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
        response_mime_type="application/json",
    )

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system_prompt,
        generation_config=generation_config,
    )

    last_error = None
    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        try:
            logger.info(
                "Gemini API call attempt %d/%d (model=%s)",
                attempt,
                GEMINI_MAX_RETRIES,
                GEMINI_MODEL,
            )

            response = model.generate_content(user_prompt)

            # Check for blocked responses (safety filters)
            if not response.candidates:
                raise LLMProviderError(
                    "Gemini returned no candidates. Response may have been "
                    "blocked by safety filters."
                )

            candidate = response.candidates[0]

            # Check finish reason
            finish_reason = candidate.finish_reason
            # finish_reason enum: STOP=1, MAX_TOKENS=2, SAFETY=3, RECITATION=4
            if hasattr(finish_reason, 'name'):
                reason_name = finish_reason.name
            else:
                reason_name = str(finish_reason)

            if reason_name == "SAFETY":
                raise LLMProviderError(
                    "Gemini blocked the response due to safety filters. "
                    "The input text may contain content flagged by Google's "
                    "safety settings."
                )

            if reason_name == "MAX_TOKENS":
                logger.warning(
                    "Gemini response truncated (MAX_TOKENS). "
                    "Consider increasing GEMINI_MAX_OUTPUT_TOKENS or "
                    "reducing input chunk size."
                )
                # Still try to use the partial response — it might be valid JSON
                # The validation step will catch incomplete output

            text = response.text
            if not text or not text.strip():
                raise ExtractionError("Gemini returned empty response text.")

            logger.info(
                "Gemini response received: %d chars, finish_reason=%s",
                len(text),
                reason_name,
            )
            return text

        except LLMProviderError:
            # Fatal — don't retry
            raise

        except ExtractionError:
            # Response was empty — retry
            last_error = ExtractionError("Gemini returned empty response.")
            logger.warning("Empty response on attempt %d, retrying...", attempt)

        except Exception as e:
            error_str = str(e).lower()
            last_error = e

            # Rate limit — backoff and retry
            if "429" in str(e) or "resource exhausted" in error_str:
                delay = GEMINI_RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "Rate limited (attempt %d/%d). Retrying in %.1fs...",
                    attempt,
                    GEMINI_MAX_RETRIES,
                    delay,
                )
                time.sleep(delay)
                continue

            # Transient / network errors — retry
            if any(kw in error_str for kw in [
                "deadline", "timeout", "unavailable", "connection",
                "internal", "503", "500",
            ]):
                delay = GEMINI_RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "Transient error on attempt %d/%d: %s. Retrying in %.1fs...",
                    attempt,
                    GEMINI_MAX_RETRIES,
                    e,
                    delay,
                )
                time.sleep(delay)
                continue

            # Unknown error — treat as fatal
            raise LLMProviderError(
                f"Gemini API error (non-retryable): {e}"
            ) from e

    # All retries exhausted
    raise ExtractionError(
        f"Gemini extraction failed after {GEMINI_MAX_RETRIES} attempts. "
        f"Last error: {last_error}"
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
