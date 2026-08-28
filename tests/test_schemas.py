import pytest
from pydantic import ValidationError

from cloudsec_rag.schemas import Chunk, Document, EvalQuestion, EvalRunResult, RetrievedChunk


def test_document_schema_validation():
    document = Document(
        doc_id="doc1",
        title="title",
        source_path="file.md",
        text="content",
        source_type="official",
        source_url="https://example.com/doc",
        is_official=True,
    )
    assert document.doc_id == "doc1"
    assert document.title == "title"
    assert document.is_official is True


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



@pytest.mark.parametrize("score", [float("nan"), float("inf"), float("-inf")])
def test_retrieved_chunk_rejects_nonfinite_scores(score: float):
    with pytest.raises(ValidationError):
        RetrievedChunk(
            chunk_id="doc1-0",
            doc_id="doc1",
            title="title",
            source_path="file.md",
            chunk_index=0,
            text="content",
            score=score,
        )

def test_eval_question_schema_missing_fields_raises():
    with pytest.raises(ValueError):
        EvalQuestion(id="q1", question="x", expected_doc_ids=None)


def test_eval_question_schema_supports_avoided_doc_ids():
    question = EvalQuestion(
        id="q1",
        question="x",
        expected_doc_ids=["doc1"],
        avoided_doc_ids=["doc2"],
    )

    assert question.avoided_doc_ids == ["doc2"]


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("retrieval_recall_at_k", -0.1),
        ("retrieval_recall_at_k", 1.1),
        ("retrieval_recall_at_k", float("nan")),
        ("average_faithfulness_score", 1.1),
        ("average_latency_ms", -1),
        ("average_latency_ms", float("inf")),
        ("estimated_cost_usd", -0.01),
        ("estimated_cost_usd", float("nan")),
    ],
)
def test_eval_run_result_rejects_invalid_metrics(
    field_name: str,
    invalid_value: float,
):
    payload = {
        "run_id": "run-test",
        "timestamp": "2026-08-25T00:00:00Z",
        "config": {},
        "retrieval_recall_at_k": 1.0,
        "average_faithfulness_score": 1.0,
        "average_latency_ms": 100.0,
        "estimated_cost_usd": 0.01,
        "per_question_results": [],
    }
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        EvalRunResult(**payload)
