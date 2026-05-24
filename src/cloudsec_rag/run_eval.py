from __future__ import annotations

import json
from pathlib import Path

from .config import Settings
from .evaluate_retrieval import EvalRunResult, evaluate_retrieval, save_eval_report


def run_evaluation(settings: Settings | None = None) -> EvalRunResult:
    settings = settings or Settings()
    result = evaluate_retrieval(settings)
    output_path = settings.run_reports_dir / f"run_{result.timestamp.replace(':', '-')}_{result.run_id}.json"
    save_eval_report(result, output_path)
    return result


def load_report(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
