# Breaks files into small pieces for embeddings.
# Large files must be broken into chunks before embeddings.

from typing import List

from ask_harry.config.settings import Config

config = Config()


def chunk_text(
    text: str,
    chunk_size: int = config.chunk_size,
    overlap: int = config.chunk_overlap,
    min_chunk_size: int = 50,
    respect_newlines: bool = True,
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text (str): Input text to split
        chunk_size (int): Maximum size of each chunk
        overlap (int): Number of characters to overlap between chunks
        min_chunk_size (int): Minimum size of chunk to keep
        respect_newlines (bool): Extend chunks to nearest newline (better for code)

    Returns:
        List[str]: List of text chunks
    """

    # Input validation
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")

    if overlap < 0:
        raise ValueError("overlap must be >= 0")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    if min_chunk_size < 0:
        raise ValueError("min_chunk_size must be >= 0")

    # normalize
    text = text.replace("\r\n", "\n")
    chunks: List[str] = []
    step = chunk_size - overlap
    text_length = len(text)

    for start in range(0, text_length, step):
        end = start + chunk_size

        newline_pos = text.rfind("\n", 0, start)
        if newline_pos != -1:
            start = newline_pos + 1

        if end < text_length:
            while end < text_length and not text[end].isspace():
                end += 1

        # extend to nearest newline (helps code structure)
        if respect_newlines and end < text_length:
            newline_pos = text.find("\n", end)
            if newline_pos != -1:
                end = newline_pos

        chunk = text[start:end]
        # Clean chunk
        chunk = chunk.strip()

        # Skip tiny chunks
        if len(chunk) < min_chunk_size:
            continue

        chunks.append(chunk)

    return chunks


"""
def chunk_text(text, chunk_size=300, overlap=50):    
    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

    return chunks
"""
