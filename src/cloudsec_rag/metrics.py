from __future__ import annotations

from typing import Iterable, List


def recall_at_k(retrieved_doc_ids: Iterable[str], expected_doc_ids: Iterable[str]) -> float:
    expected_set = set(expected_doc_ids)
    if not expected_set:
        return 0.0
    retrieved_set = set(retrieved_doc_ids)
    matched = expected_set.intersection(retrieved_set)
    return len(matched) / len(expected_set)


def average_latency_ms(latencies: Iterable[float]) -> float:
    latencies = list(latencies)
    if not latencies:
        return 0.0
    return sum(latencies) / len(latencies) * 1000.0


def estimate_cost_usd(num_embeddings: int, num_generation_tokens: int) -> float:
    embedding_cost_per_1000 = 0.0004
    generation_cost_per_1000 = 0.002
    return round(
        num_embeddings * embedding_cost_per_1000 / 1000.0
        + num_generation_tokens * generation_cost_per_1000 / 1000.0,
        6,
    )
