from cloudsec_rag.evaluate_answers import (
    answer_has_citations,
    citation_coverage,
    missing_expected_points,
)
from cloudsec_rag.schemas import GeneratedAnswer, RetrievedChunk


def test_answer_citation_checks_use_answer_text():
    answer = GeneratedAnswer(
        question_id="q1",
        question="What helps least privilege?",
        answer="Use fine-grained policies [1]. Review unused access [2].",
        citations=[],
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="doc1-0",
                doc_id="doc1",
                title="Doc 1",
                source_path="doc1.md",
                chunk_index=0,
                text="Use fine-grained policies.",
                score=0.9,
            ),
            RetrievedChunk(
                chunk_id="doc2-0",
                doc_id="doc2",
                title="Doc 2",
                source_path="doc2.md",
                chunk_index=0,
                text="Review unused access.",
                score=0.8,
            ),
        ],
    )

    assert answer_has_citations(answer)
    assert citation_coverage(answer) == 1.0


def test_citation_coverage_rejects_out_of_range_citations():
    answer = GeneratedAnswer(
        question_id="q1",
        question="What helps least privilege?",
        answer="Use fine-grained policies [2].",
        citations=[],
        retrieved_chunks=[
            RetrievedChunk(
                chunk_id="doc1-0",
                doc_id="doc1",
                title="Doc 1",
                source_path="doc1.md",
                chunk_index=0,
                text="Use fine-grained policies.",
                score=0.9,
            ),
        ],
    )

    assert answer_has_citations(answer)
    assert citation_coverage(answer) == 0.0


def test_answer_without_citations_has_zero_citation_coverage():
    answer = GeneratedAnswer(
        question_id="q1",
        question="What helps least privilege?",
        answer="Use fine-grained policies.",
        citations=[],
        retrieved_chunks=[],
    )

    assert not answer_has_citations(answer)
    assert citation_coverage(answer) == 0.0


def test_missing_expected_points_reports_absent_points():
    missing = missing_expected_points(
        "Use fine-grained policies and temporary credentials.",
        ["fine-grained policies", "remove inactive access keys"],
    )

    assert missing == ["remove inactive access keys"]


def test_expected_point_matching_allows_close_wording():
    missing = missing_expected_points(
        "Inactive keys should be disabled or removed, and logs should be searchable.",
        ["remove inactive access keys", "searchable log storage"],
    )

    assert missing == []
