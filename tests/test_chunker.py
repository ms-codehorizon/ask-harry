import pytest

from ask_harry.retrieval.chunker import chunk_text


def test_returns_empty_list_for_blank_text():
    assert chunk_text("   \n\t") == []


def test_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("hello world", chunk_size=5, overlap=5)


def test_rejects_non_string_input():
    with pytest.raises(TypeError):
        chunk_text(None)


def test_extends_chunk_until_word_boundary():
    text = "abcdefghij"

    chunks = chunk_text(
        text,
        chunk_size=6,
        overlap=2,
        min_chunk_size=1,
        respect_newlines=False,
    )

    assert chunks == ["abcdefghij", "efghij", "ij"]


def test_respects_newlines_when_expanding_chunk_boundaries():
    text = "def alpha():\n    return 1\n\ndef beta():\n    return 2\n"

    chunks = chunk_text(
        text,
        chunk_size=18,
        overlap=4,
        min_chunk_size=1,
        respect_newlines=True,
    )

    assert len(chunks) >= 2
    assert chunks[0].startswith("def alpha():")
    assert "return 1" in chunks[0]
