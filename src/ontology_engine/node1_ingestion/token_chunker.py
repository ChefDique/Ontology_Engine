"""
Token Chunker — TASK_A3

Breaks large documents into overlapping chunks to prevent
LLM context window overflow and 'lost in the middle' issues.

Uses a word-based approximation (1 token ≈ 0.75 words) for fast
tokenization without requiring a specific tokenizer library.

Design by Contract:
  Precondition:  Input is PII-redacted text from pii_sanitizer
  Postcondition: Output is a list of text chunks, each within LLM token limits
"""

import re

# Approximation: 1 token ≈ 0.75 words (conservative for English text)
_WORDS_PER_TOKEN = 0.75


def _estimate_tokens(text: str) -> int:
    """Estimate token count from text using word-based heuristic."""
    words = len(text.split())
    return max(1, int(words / _WORDS_PER_TOKEN))


def _split_on_boundaries(text: str) -> list[str]:
    """Split text on natural boundaries (paragraphs, then sentences)."""
    # Split on double newlines first (paragraph boundaries)
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def chunk_text(
    text: str,
    max_tokens: int = 4000,
    overlap_tokens: int = 200,
) -> list[dict]:
    """Split text into overlapping chunks for LLM processing.

    Strategy:
      1. If text fits in a single chunk, return it directly
      2. Split on paragraph boundaries
      3. Greedily accumulate paragraphs into chunks up to max_tokens
      4. Each new chunk starts with overlap_tokens from the end of the previous
         chunk to maintain continuity across boundaries

    Args:
        text: PII-redacted text to chunk
        max_tokens: Maximum tokens per chunk (default 4000)
        overlap_tokens: Tokens of overlap between consecutive chunks (default 200)

    Returns:
        list of dicts, each with:
            - chunk_text: str
            - chunk_index: int (0-based)
            - token_count: int
            - overlap_with_previous: bool
    """
    if not text or not text.strip():
        return [{
            "chunk_text": "",
            "chunk_index": 0,
            "token_count": 0,
            "overlap_with_previous": False,
        }]

    total_tokens = _estimate_tokens(text)
    if total_tokens <= max_tokens:
        return [{
            "chunk_text": text,
            "chunk_index": 0,
            "token_count": total_tokens,
            "overlap_with_previous": False,
        }]

    paragraphs = _split_on_boundaries(text)
    chunks: list[dict] = []
    current_paragraphs: list[str] = []
    current_tokens = 0
    chunk_index = 0

    for para in paragraphs:
        para_tokens = _estimate_tokens(para)

        # If a single paragraph exceeds max_tokens, split it by sentences
        if para_tokens > max_tokens:
            # Flush current buffer first
            if current_paragraphs:
                chunk_text_str = "\n\n".join(current_paragraphs)
                chunks.append({
                    "chunk_text": chunk_text_str,
                    "chunk_index": chunk_index,
                    "token_count": _estimate_tokens(chunk_text_str),
                    "overlap_with_previous": chunk_index > 0,
                })
                chunk_index += 1
                current_paragraphs = []
                current_tokens = 0

            # Split oversized paragraph by sentences
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sent in sentences:
                sent_tokens = _estimate_tokens(sent)
                if current_tokens + sent_tokens > max_tokens and current_paragraphs:
                    chunk_text_str = " ".join(current_paragraphs)
                    chunks.append({
                        "chunk_text": chunk_text_str,
                        "chunk_index": chunk_index,
                        "token_count": _estimate_tokens(chunk_text_str),
                        "overlap_with_previous": chunk_index > 0,
                    })
                    chunk_index += 1
                    # Overlap: take last portion
                    overlap_text = _get_overlap_text(chunk_text_str, overlap_tokens)
                    current_paragraphs = [overlap_text] if overlap_text else []
                    current_tokens = _estimate_tokens(overlap_text) if overlap_text else 0

                current_paragraphs.append(sent)
                current_tokens += sent_tokens
            continue

        # Normal case: accumulate paragraphs
        if current_tokens + para_tokens > max_tokens and current_paragraphs:
            chunk_text_str = "\n\n".join(current_paragraphs)
            chunks.append({
                "chunk_text": chunk_text_str,
                "chunk_index": chunk_index,
                "token_count": _estimate_tokens(chunk_text_str),
                "overlap_with_previous": chunk_index > 0,
            })
            chunk_index += 1

            # Overlap: start new chunk with tail of previous
            overlap_text = _get_overlap_text(chunk_text_str, overlap_tokens)
            current_paragraphs = [overlap_text] if overlap_text else []
            current_tokens = _estimate_tokens(overlap_text) if overlap_text else 0

        current_paragraphs.append(para)
        current_tokens += para_tokens

    # Flush remaining
    if current_paragraphs:
        chunk_text_str = "\n\n".join(current_paragraphs)
        chunks.append({
            "chunk_text": chunk_text_str,
            "chunk_index": chunk_index,
            "token_count": _estimate_tokens(chunk_text_str),
            "overlap_with_previous": chunk_index > 0,
        })

    return chunks


def _get_overlap_text(text: str, overlap_tokens: int) -> str:
    """Extract the last `overlap_tokens` worth of text for chunk overlap."""
    words = text.split()
    overlap_words = int(overlap_tokens * _WORDS_PER_TOKEN)
    if overlap_words >= len(words):
        return text
    return " ".join(words[-overlap_words:])
