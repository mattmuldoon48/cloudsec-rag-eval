import json

import pytest

from cloudsec_rag.compare_runs import check_regression, compare_run_files


_MISSING = object()


def test_compare_runs_includes_recall_faithfulness_and_latency(tmp_path):
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    left.write_text(
        json.dumps(
            {
                "retrieval_recall_at_k": 0.8,
                "average_faithfulness_score": 0.7,
                "average_latency_ms": 100.0,
            }
        ),
        encoding="utf-8",
    )
    right.write_text(
        json.dumps(
            {
                "retrieval_recall_at_k": 1.0,
                "average_faithfulness_score": 0.9,
                "average_latency_ms": 125.5,
            }
        ),
        encoding="utf-8",
    )

    diff = compare_run_files(left, right)

    assert diff["delta"]["recall_diff"] == 0.2
    assert diff["delta"]["faithfulness_diff"] == 0.2
    assert diff["delta"]["latency_diff_ms"] == 25.5


@pytest.mark.parametrize(
    ("side", "field", "invalid_value"),
    [
        pytest.param("left", "retrieval_recall_at_k", _MISSING, id="missing"),
        pytest.param("right", "average_faithfulness_score", None, id="null"),
        pytest.param("left", "average_latency_ms", "100", id="nonnumeric"),
        pytest.param("right", "retrieval_recall_at_k", True, id="boolean"),
        pytest.param("left", "average_faithfulness_score", float("nan"), id="nan"),
        pytest.param("right", "average_latency_ms", float("inf"), id="infinity"),
    ],
)
def test_compare_runs_rejects_invalid_required_metrics(
    tmp_path, side, field, invalid_value
):
    reports = {
        "left": {
            "retrieval_recall_at_k": 0.8,
            "average_faithfulness_score": 0.7,
            "average_latency_ms": 100.0,
        },
        "right": {
            "retrieval_recall_at_k": 1.0,
            "average_faithfulness_score": 0.9,
            "average_latency_ms": 125.5,
        },
    }
    if invalid_value is _MISSING:
        del reports[side][field]
    else:
        reports[side][field] = invalid_value

    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    left.write_text(json.dumps(reports["left"]), encoding="utf-8")
    right.write_text(json.dumps(reports["right"]), encoding="utf-8")

    with pytest.raises(ValueError) as error:
        compare_run_files(left, right)

    path = left if side == "left" else right
    assert str(error.value) == (
        f"{side} report {str(path)!r} has invalid field {field!r}; "
        "expected a finite real number"
    )


def test_regression_gate_passes_when_metrics_stay_within_thresholds():
    diff = {
        "delta": {
            "recall_diff": 0.0,
            "faithfulness_diff": -0.005,
            "latency_diff_ms": 250.0,
        }
    }

    result = check_regression(diff)

    assert result["passed"] is True
    assert result["failures"] == []


def test_regression_gate_fails_on_quality_or_latency_regression():
    diff = {
        "delta": {
            "recall_diff": -0.2,
            "faithfulness_diff": -0.15,
            "latency_diff_ms": 2500.0,
        }
    }

    result = check_regression(diff)

    assert result["passed"] is False
    assert len(result["failures"]) == 3
