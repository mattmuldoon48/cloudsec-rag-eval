import pytest

from cloudsec_rag.metrics import average_latency_ms, estimate_cost_usd, recall_at_k


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


def test_average_latency_returns_zero_without_samples():
    assert average_latency_ms([]) == 0.0


def test_average_latency_converts_seconds_to_milliseconds():
    assert average_latency_ms([0.1, 0.2, 0.3]) == pytest.approx(200.0)


def test_estimate_cost_rounds_embedding_and_generation_costs():
    assert estimate_cost_usd(num_embeddings=25, num_generation_tokens=1234) == 0.002478