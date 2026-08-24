import pytest
from pydantic import ValidationError

from cloudsec_rag.chunk import chunk_documents, chunk_text
from cloudsec_rag.schemas import Chunk, Document


def test_chunk_text_creates_non_empty_chunks():
    text = "A" * 1500
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=100)
    assert len(chunks) > 0
    assert all(chunk for chunk in chunks)


def test_chunk_overlap_works():
    text = "0123456789" * 20
    chunks = chunk_text(text, chunk_size=30, chunk_overlap=10)
    assert len(chunks) > 1
    assert chunks[0].endswith("0123456789")
    assert chunks[1].startswith("0123456789")


def test_chunk_documents_preserves_metadata():
    document = Document(doc_id="doc1", title="Test Doc", source_path="path.md", text="Hello world")
    chunks = chunk_documents([document], chunk_size=50, chunk_overlap=10)
    assert chunks[0].doc_id == "doc1"
    assert chunks[0].title == "Test Doc"
    assert chunks[0].source_path == "path.md"


def test_chunk_rejects_negative_index():
    with pytest.raises(ValidationError):
        Chunk(
            chunk_id="doc--1",
            doc_id="doc",
            title="Title",
            source_path="doc.md",
            chunk_index=-1,
            text="chunk",
        )
