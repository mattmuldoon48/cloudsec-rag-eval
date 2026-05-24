import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from cloudsec_rag.compare_runs import compare_run_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two evaluation run JSON files.")
    parser.add_argument("left", type=Path, help="First run JSON file")
    parser.add_argument("right", type=Path, help="Second run JSON file")
    args = parser.parse_args()

    diff = compare_run_files(args.left, args.right)
    print("Comparison")
    print(f"Left: {diff['left']['path']}")
    print(f"  recall@k: {diff['left']['retrieval_recall_at_k']}")
    print(f"  faithfulness: {diff['left']['average_faithfulness_score']}")
    print(f"  latency_ms: {diff['left']['average_latency_ms']}")
    print(f"Right: {diff['right']['path']}")
    print(f"  recall@k: {diff['right']['retrieval_recall_at_k']}")
    print(f"  faithfulness: {diff['right']['average_faithfulness_score']}")
    print(f"  latency_ms: {diff['right']['average_latency_ms']}")
    print("Delta")
    print(f"  recall_diff: {diff['delta']['recall_diff']}")
    print(f"  faithfulness_diff: {diff['delta']['faithfulness_diff']}")
    print(f"  latency_diff_ms: {diff['delta']['latency_diff_ms']}")


if __name__ == "__main__":
    main()
