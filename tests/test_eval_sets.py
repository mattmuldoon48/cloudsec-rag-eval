from pathlib import Path

import pytest
from pydantic import ValidationError

from cloudsec_rag.evaluate_retrieval import load_eval_questions


def test_official_notes_eval_set_has_25_valid_questions():
    eval_path = Path("data/eval_sets/cloudsec_official_notes_eval_v1.jsonl")

    questions = load_eval_questions(eval_path)

    assert len(questions) == 25
    assert {question.id for question in questions}
    assert any(len(question.expected_doc_ids) > 1 for question in questions)
    assert any(question.avoided_doc_ids for question in questions)


def test_empty_and_whitespace_only_eval_sets_are_rejected(tmp_path):
    empty_path = tmp_path / "empty.jsonl"
    empty_path.write_text("", encoding="utf-8")
    whitespace_path = tmp_path / "whitespace.jsonl"
    whitespace_path.write_text("  \n\t\n", encoding="utf-8")

    for eval_path in (empty_path, whitespace_path):
        with pytest.raises(ValueError, match="no nonblank questions") as exc_info:
            load_eval_questions(eval_path)

        assert str(eval_path) in str(exc_info.value)


def test_duplicate_eval_question_ids_are_rejected(tmp_path):
    eval_path = tmp_path / "duplicates.jsonl"
    row = '{"id":"duplicate","question":"What?","expected_doc_ids":["doc"]}'
    eval_path.write_text(f"{row}\n{row}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate eval question ID 'duplicate'") as exc_info:
        load_eval_questions(eval_path)

    assert "line 2" in str(exc_info.value)
    assert str(eval_path) in str(exc_info.value)


def test_eval_questions_require_expected_documents(tmp_path):
    eval_path = tmp_path / "missing_expected_docs.jsonl"
    eval_path.write_text(
        '{"id":"q1","question":"What?","expected_doc_ids":[]}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="expected_doc_ids"):
        load_eval_questions(eval_path)


@pytest.mark.parametrize(
    ("row", "message"),
    [
        (
            '{"id":" ","question":"What?","expected_doc_ids":["doc"]}',
            "id must not be blank",
        ),
        (
            '{"id":"q1","question":" ","expected_doc_ids":["doc"]}',
            "question must not be blank",
        ),
        (
            '{"id":"q1","question":"What?","expected_doc_ids":[" "]}',
            "expected_doc_ids entries must not be blank",
        ),
        (
            (
                '{"id":"q1","question":"What?","expected_doc_ids":["doc"],'
                '"avoided_doc_ids":[" "]}'
            ),
            "avoided_doc_ids entries must not be blank",
        ),
    ],
)
def test_eval_questions_reject_blank_required_text(
    tmp_path,
    row: str,
    message: str,
):
    eval_path = tmp_path / "blank_fields.jsonl"
    eval_path.write_text(row + "\n", encoding="utf-8")

    with pytest.raises(ValidationError, match=message):
        load_eval_questions(eval_path)


def test_expected_and_avoided_documents_must_not_overlap(tmp_path):
    eval_path = tmp_path / "contradictory_docs.jsonl"
    eval_path.write_text(
        (
            '{"id":"q1","question":"What?","expected_doc_ids":["doc"],'
            '"avoided_doc_ids":["doc"]}\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="must not overlap"):
        load_eval_questions(eval_path)
