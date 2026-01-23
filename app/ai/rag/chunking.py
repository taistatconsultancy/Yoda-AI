from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    text: str


def chunk_text(text: str, *, source_id: str, chunk_size: int = 1500, overlap: int = 200) -> List[TextChunk]:
    """
    Simple character-based chunking with overlap.
    This avoids tokenizers but still keeps chunks reasonably sized.
    """
    t = (text or "").strip()
    if not t:
        return []

    chunks: List[TextChunk] = []
    start = 0
    i = 0
    while start < len(t):
        end = min(len(t), start + chunk_size)
        chunk = t[start:end].strip()
        if chunk:
            chunks.append(TextChunk(chunk_id=f"{source_id}:{i}", text=chunk))
            i += 1
        if end >= len(t):
            break
        start = max(0, end - overlap)
    return chunks

