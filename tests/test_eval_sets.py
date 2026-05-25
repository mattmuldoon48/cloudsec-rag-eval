from pathlib import Path

from cloudsec_rag.evaluate_retrieval import load_eval_questions


def test_official_notes_eval_set_has_25_valid_questions():
    eval_path = Path("data/eval_sets/cloudsec_official_notes_eval_v1.jsonl")

    questions = load_eval_questions(eval_path)

    assert len(questions) == 25
    assert {question.id for question in questions}
    assert any(len(question.expected_doc_ids) > 1 for question in questions)
    assert any(question.avoided_doc_ids for question in questions)
