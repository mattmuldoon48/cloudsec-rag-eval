import _bootstrap  # noqa: F401

import argparse
import re
from pathlib import Path

from cloudsec_rag.config import load_settings
from cloudsec_rag.evaluate_retrieval import evaluate_retrieval, save_eval_report


def safe_filename_part(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-") or "default"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run retrieval and answer evaluation.")
    parser.add_argument("--config", type=Path, default=None, help="Optional experiment config JSON file")
    args = parser.parse_args()

    settings = load_settings(args.config)
    report = evaluate_retrieval(settings)
    experiment_name = safe_filename_part(settings.experiment_name)
    output_file = settings.run_reports_dir / f"run_{experiment_name}_{report.timestamp.replace(':', '-')}_{report.run_id}.json"
    save_eval_report(report, output_file)
    print(f"Saved evaluation report to {output_file}")


if __name__ == "__main__":
    main()
