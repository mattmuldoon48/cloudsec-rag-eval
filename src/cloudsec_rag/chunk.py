from __future__ import annotations

from typing import Iterable, List

from .schemas import Chunk, Document


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    text = text.strip()

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - chunk_overlap, 0)

    return chunks


def chunk_documents(documents: Iterable[Document], chunk_size: int, chunk_overlap: int) -> List[Chunk]:
    chunks: list[Chunk] = []

    for document in documents:
        text_chunks = chunk_text(document.text, chunk_size, chunk_overlap)
        for index, chunk_text_content in enumerate(text_chunks):
            chunks.append(
                Chunk(
                    chunk_id=f"{document.doc_id}-{index}",
                    doc_id=document.doc_id,
                    title=document.title,
                    source_path=document.source_path,
                    chunk_index=index,
                    text=chunk_text_content,
                    source_type=document.source_type,
                    source_url=document.source_url,
                    is_official=document.is_official,
                    notes=document.notes,
                )
            )

    return chunks
