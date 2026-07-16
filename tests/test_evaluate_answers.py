import json

import pytest

from cloudsec_rag.evaluate_answers import (
    _parse_faithfulness_judgment,
    answer_has_citations,
    citation_coverage,
    missing_expected_points,
)
from cloudsec_rag.schemas import GeneratedAnswer, RetrievedChunk


_VALID_JUDGMENT = {
    "faithfulness_score": 0.625,
    "is_faithful": True,
    "unsupported_claims": ["A specific unsupported claim."],
    "rationale": "The remaining claims are supported.",
}


def _assert_conservative_invalid_judgment(raw_judgment: str) -> None:
    assert _parse_faithfulness_judgment(raw_judgment) == {
        "faithfulness_score": 0.0,
        "is_faithful": False,
        "unsupported_claims": ["Judge did not return valid JSON."],
        "rationale": raw_judgment.strip(),
    }


def test_faithfulness_judgment_preserves_valid_payload():
    raw_judgment = json.dumps(_VALID_JUDGMENT)

    assert _parse_faithfulness_judgment(raw_judgment) == _VALID_JUDGMENT


@pytest.mark.parametrize(
    "raw_judgment",
    [
        pytest.param("not JSON", id="invalid-json"),
        pytest.param("[]", id="top-level-array"),
        pytest.param("null", id="top-level-null"),
    ],
)
def test_faithfulness_judgment_rejects_non_object_output(raw_judgment):
    _assert_conservative_invalid_judgment(raw_judgment)


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {**_VALID_JUDGMENT, "faithfulness_score": "0.625"},
            id="string-score",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "faithfulness_score": True},
            id="boolean-score",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "faithfulness_score": -0.1},
            id="score-below-zero",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "faithfulness_score": 1.1},
            id="score-above-one",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "faithfulness_score": float("nan")},
            id="nan-score",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "faithfulness_score": float("inf")},
            id="infinite-score",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "is_faithful": 1},
            id="integer-boolean",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "unsupported_claims": "unsupported"},
            id="string-claims",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "unsupported_claims": [1]},
            id="non-string-claim",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "rationale": False},
            id="boolean-rationale",
        ),
        pytest.param(
            {**_VALID_JUDGMENT, "unexpected": "field"},
            id="extra-field",
        ),
    ],
)
def test_faithfulness_judgment_rejects_invalid_field_values(payload):
    raw_judgment = json.dumps(payload)

    _assert_conservative_invalid_judgment(raw_judgment)


@pytest.mark.parametrize("missing_field", list(_VALID_JUDGMENT))
def test_faithfulness_judgment_rejects_missing_fields(missing_field):
    payload = dict(_VALID_JUDGMENT)
    payload.pop(missing_field)
    raw_judgment = json.dumps(payload)

    _assert_conservative_invalid_judgment(raw_judgment)


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


def test_citation_coverage_scores_mixed_valid_and_out_of_range_citations():
    answer = GeneratedAnswer(
        question_id="q1",
        question="What helps least privilege?",
        answer="Use fine-grained policies [1]. Review unused access [3].",
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
    assert citation_coverage(answer) == 0.5


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
