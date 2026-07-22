from pathlib import Path

import pytest

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
