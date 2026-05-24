from __future__ import annotations

import json
from pathlib import Path


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
