from __future__ import annotations

import json
import math
from numbers import Real
from pathlib import Path
from typing import Any


def _validated_metrics(data: Any, side: str, path: Path) -> dict[str, Real]:
    metrics: dict[str, Real] = {}
    for field in (
        "retrieval_recall_at_k",
        "average_faithfulness_score",
        "average_latency_ms",
    ):
        value = data.get(field) if isinstance(data, dict) else None
        if (
            isinstance(value, bool)
            or not isinstance(value, Real)
            or (isinstance(value, float) and not math.isfinite(value))
        ):
            raise ValueError(
                f"{side} report {str(path)!r} has invalid field {field!r}; "
                "expected a finite real number"
            )
        metrics[field] = value
    return metrics


def compare_run_files(left: Path, right: Path) -> dict:
    with left.open("r", encoding="utf-8") as handle:
        left_data = json.load(handle)
    with right.open("r", encoding="utf-8") as handle:
        right_data = json.load(handle)

    left_metrics = _validated_metrics(left_data, "left", left)
    right_metrics = _validated_metrics(right_data, "right", right)

    return {
        "left": {
            "path": str(left),
            "retrieval_recall_at_k": left_metrics["retrieval_recall_at_k"],
            "average_faithfulness_score": left_metrics["average_faithfulness_score"],
            "average_latency_ms": left_metrics["average_latency_ms"],
        },
        "right": {
            "path": str(right),
            "retrieval_recall_at_k": right_metrics["retrieval_recall_at_k"],
            "average_faithfulness_score": right_metrics["average_faithfulness_score"],
            "average_latency_ms": right_metrics["average_latency_ms"],
        },
        "delta": {
            "recall_diff": round(
                right_metrics["retrieval_recall_at_k"]
                - left_metrics["retrieval_recall_at_k"],
                4,
            ),
            "faithfulness_diff": round(
                right_metrics["average_faithfulness_score"]
                - left_metrics["average_faithfulness_score"],
                4,
            ),
            "latency_diff_ms": round(
                right_metrics["average_latency_ms"]
                - left_metrics["average_latency_ms"],
                2,
            ),
        },
    }


def check_regression(
    diff: dict[str, Any],
    min_recall_delta: float = -0.01,
    min_faithfulness_delta: float = -0.01,
    max_latency_increase_ms: float = 1000.0,
) -> dict[str, Any]:
    recall_diff = float(diff["delta"].get("recall_diff") or 0.0)
    faithfulness_diff = float(diff["delta"].get("faithfulness_diff") or 0.0)
    latency_diff_ms = float(diff["delta"].get("latency_diff_ms") or 0.0)

    failures: list[str] = []
    if recall_diff < min_recall_delta:
        failures.append(
            f"retrieval recall regressed by {recall_diff}; allowed minimum delta is {min_recall_delta}"
        )
    if faithfulness_diff < min_faithfulness_delta:
        failures.append(
            f"faithfulness regressed by {faithfulness_diff}; allowed minimum delta is {min_faithfulness_delta}"
        )
    if latency_diff_ms > max_latency_increase_ms:
        failures.append(
            f"latency increased by {latency_diff_ms} ms; allowed maximum increase is {max_latency_increase_ms} ms"
        )

    return {
        "passed": not failures,
        "failures": failures,
        "thresholds": {
            "min_recall_delta": min_recall_delta,
            "min_faithfulness_delta": min_faithfulness_delta,
            "max_latency_increase_ms": max_latency_increase_ms,
        },
    }
