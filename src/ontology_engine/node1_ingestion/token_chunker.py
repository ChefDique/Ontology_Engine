"""
Token Chunker — TASK_A3

Breaks large documents into overlapping chunks to prevent
LLM context window overflow and 'lost in the middle' issues.

Design by Contract:
  Precondition:  Input is PII-redacted text from pii_sanitizer
  Postcondition: Output is a list of text chunks, each within LLM token limits
"""


def chunk_text(text: str, max_tokens: int = 4000, overlap_tokens: int = 200) -> list[dict]:
    """Split text into overlapping chunks for LLM processing.

    Returns:
        list of dicts, each with:
            - chunk_text: str
            - chunk_index: int
            - token_count: int
            - overlap_with_previous: bool
    """
    raise NotImplementedError("TASK_A3: Token chunking strategy")
