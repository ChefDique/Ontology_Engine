"""
Semantic Extractor — TASK_B2

Orchestrates LLM calls for structured data extraction from Xactimate text.
"""


def extract_estimate(text_chunks: list[dict], provider: str = "openai") -> dict:
    """Extract structured Xactimate data from PII-redacted text chunks.

    Returns: dict conforming to the extraction JSON schema (see prompt.py)
    """
    raise NotImplementedError("TASK_B2: Semantic extraction orchestrator")
