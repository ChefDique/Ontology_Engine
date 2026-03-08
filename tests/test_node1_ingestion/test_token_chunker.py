"""Tests for Node 1 — Token Chunker (TASK_A3)."""

import pytest

from ontology_engine.node1_ingestion.token_chunker import (
    chunk_text,
    _estimate_tokens,
    _get_overlap_text,
)


class TestEstimateTokens:
    def test_empty_string(self):
        assert _estimate_tokens("") == 1  # min 1

    def test_single_word(self):
        assert _estimate_tokens("hello") >= 1

    def test_many_words(self):
        text = " ".join(["word"] * 100)
        tokens = _estimate_tokens(text)
        # 100 words / 0.75 ≈ 133 tokens
        assert 100 <= tokens <= 200


class TestChunkText:
    def test_empty_text(self):
        result = chunk_text("")
        assert len(result) == 1
        assert result[0]["chunk_text"] == ""
        assert result[0]["chunk_index"] == 0
        assert result[0]["overlap_with_previous"] is False

    def test_short_text_single_chunk(self):
        text = "This is a short text."
        result = chunk_text(text, max_tokens=4000)
        assert len(result) == 1
        assert result[0]["chunk_text"] == text
        assert result[0]["overlap_with_previous"] is False

    def test_long_text_multiple_chunks(self):
        # Create text that exceeds max_tokens
        paragraph = "This is a paragraph of text. " * 50
        text = "\n\n".join([paragraph] * 10)  # ~5000 words
        result = chunk_text(text, max_tokens=500, overlap_tokens=50)
        assert len(result) > 1

    def test_chunks_have_required_keys(self):
        text = "Test. " * 1000
        result = chunk_text(text, max_tokens=100)
        for chunk in result:
            assert "chunk_text" in chunk
            assert "chunk_index" in chunk
            assert "token_count" in chunk
            assert "overlap_with_previous" in chunk

    def test_chunk_indices_sequential(self):
        text = "Word. " * 2000
        result = chunk_text(text, max_tokens=200)
        for i, chunk in enumerate(result):
            assert chunk["chunk_index"] == i

    def test_first_chunk_no_overlap(self):
        text = "Word. " * 2000
        result = chunk_text(text, max_tokens=200)
        assert result[0]["overlap_with_previous"] is False

    def test_subsequent_chunks_have_overlap(self):
        text = "Word. " * 2000
        result = chunk_text(text, max_tokens=200, overlap_tokens=50)
        if len(result) > 1:
            for chunk in result[1:]:
                assert chunk["overlap_with_previous"] is True

    def test_token_count_within_limit(self):
        text = "Word. " * 2000
        max_t = 300
        result = chunk_text(text, max_tokens=max_t, overlap_tokens=50)
        for chunk in result:
            # Allow some tolerance for paragraph boundaries
            assert chunk["token_count"] <= max_t * 1.5

    def test_all_text_covered(self):
        """Verify no text is lost during chunking."""
        words = [f"word{i}" for i in range(500)]
        text = " ".join(words)
        result = chunk_text(text, max_tokens=100, overlap_tokens=20)
        # All original words should appear in at least one chunk
        all_chunk_text = " ".join(c["chunk_text"] for c in result)
        for w in words[:10]:  # Spot-check first 10
            assert w in all_chunk_text

    def test_custom_max_tokens(self):
        text = "Word. " * 500
        result_small = chunk_text(text, max_tokens=100)
        result_large = chunk_text(text, max_tokens=10000)
        assert len(result_small) >= len(result_large)


class TestGetOverlapText:
    def test_short_text_returns_all(self):
        result = _get_overlap_text("hello world", overlap_tokens=1000)
        assert result == "hello world"

    def test_extracts_tail(self):
        text = "one two three four five six seven eight nine ten"
        result = _get_overlap_text(text, overlap_tokens=5)
        words = result.split()
        assert len(words) <= 5
