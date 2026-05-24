import pytest

from cloudsec_rag.schemas import Chunk, Document, EvalQuestion


def test_document_schema_validation():
    document = Document(doc_id="doc1", title="title", source_path="file.md", text="content")
    assert document.doc_id == "doc1"
    assert document.title == "title"


def test_chunk_schema_validation():
    chunk = Chunk(
        chunk_id="doc1-0",
        doc_id="doc1",
        title="title",
        source_path="file.md",
        chunk_index=0,
        text="content",
    )
    assert chunk.chunk_id == "doc1-0"


def test_eval_question_schema_missing_fields_raises():
    with pytest.raises(ValueError):
        EvalQuestion(id="q1", question="x", expected_doc_ids=None)
