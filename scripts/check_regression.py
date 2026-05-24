import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from cloudsec_rag.compare_runs import check_regression, compare_run_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail if an eval run regresses beyond configured thresholds.")
    parser.add_argument("baseline", type=Path, help="Baseline run JSON file")
    parser.add_argument("candidate", type=Path, help="Candidate run JSON file")
    parser.add_argument("--min-recall-delta", type=float, default=-0.01)
    parser.add_argument("--min-faithfulness-delta", type=float, default=-0.01)
    parser.add_argument("--max-latency-increase-ms", type=float, default=1000.0)
    args = parser.parse_args()

    diff = compare_run_files(args.baseline, args.candidate)
    gate = check_regression(
        diff,
        min_recall_delta=args.min_recall_delta,
        min_faithfulness_delta=args.min_faithfulness_delta,
        max_latency_increase_ms=args.max_latency_increase_ms,
    )

    print("Regression gate")
    print(f"  recall_diff: {diff['delta']['recall_diff']}")
    print(f"  faithfulness_diff: {diff['delta']['faithfulness_diff']}")
    print(f"  latency_diff_ms: {diff['delta']['latency_diff_ms']}")

    if gate["passed"]:
        print("PASS")
        raise SystemExit(0)

    print("FAIL")
    for failure in gate["failures"]:
        print(f"  - {failure}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
