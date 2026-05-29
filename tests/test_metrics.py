from cloudsec_rag.metrics import recall_at_k


def test_retrieval_recall_metric_matches_expected_docs():
    retrieved_doc_ids = ["aws_iam_best_practices", "aws_logging_monitoring"]
    expected_doc_ids = ["aws_iam_best_practices", "incident_response_basics"]

    assert recall_at_k(retrieved_doc_ids, expected_doc_ids) == 0.5


def test_retrieval_recall_ignores_duplicate_retrieved_docs():
    retrieved_doc_ids = ["iam", "iam", "logs"]
    expected_doc_ids = ["iam", "logs"]

    assert recall_at_k(retrieved_doc_ids, expected_doc_ids) == 1.0


def test_retrieval_recall_returns_zero_without_expected_docs():
    assert recall_at_k(["iam"], []) == 0.0