from cloudsec_rag.metrics import recall_at_k


def test_retrieval_recall_metric_matches_expected_docs():
    retrieved_doc_ids = ["aws_iam_best_practices", "aws_logging_monitoring"]
    expected_doc_ids = ["aws_iam_best_practices", "incident_response_basics"]

    assert recall_at_k(retrieved_doc_ids, expected_doc_ids) == 0.5
