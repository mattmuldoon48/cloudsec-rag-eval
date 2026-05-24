from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def compare_run_files(left: Path, right: Path) -> dict:
    with left.open("r", encoding="utf-8") as handle:
        left_data = json.load(handle)
    with right.open("r", encoding="utf-8") as handle:
        right_data = json.load(handle)

    return {
        "left": {
            "path": str(left),
            "retrieval_recall_at_k": left_data.get("retrieval_recall_at_k"),
            "average_faithfulness_score": left_data.get("average_faithfulness_score"),
            "average_latency_ms": left_data.get("average_latency_ms"),
        },
        "right": {
            "path": str(right),
            "retrieval_recall_at_k": right_data.get("retrieval_recall_at_k"),
            "average_faithfulness_score": right_data.get("average_faithfulness_score"),
            "average_latency_ms": right_data.get("average_latency_ms"),
        },
        "delta": {
            "recall_diff": round((right_data.get("retrieval_recall_at_k") or 0) - (left_data.get("retrieval_recall_at_k") or 0), 4),
            "faithfulness_diff": round((right_data.get("average_faithfulness_score") or 0) - (left_data.get("average_faithfulness_score") or 0), 4),
            "latency_diff_ms": round((right_data.get("average_latency_ms") or 0) - (left_data.get("average_latency_ms") or 0), 2),
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
