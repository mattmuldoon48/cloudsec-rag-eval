from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def summarize_report(report: dict[str, Any]) -> dict[str, Any]:
    config = report.get("config", {})
    per_question_results = report.get("per_question_results", [])
    failed_retrievals = [
        item for item in per_question_results if float(item.get("recall_at_k") or 0.0) < 1.0
    ]
    missing_answer_points = sum(
        len((item.get("answer_eval") or {}).get("missing_expected_points") or [])
        for item in per_question_results
    )

    return {
        "run_id": report.get("run_id", ""),
        "timestamp": report.get("timestamp", ""),
        "experiment_name": config.get("experiment_name", "default"),
        "top_k": config.get("top_k", ""),
        "chunk_size": config.get("chunk_size", ""),
        "chunk_overlap": config.get("chunk_overlap", ""),
        "retrieval_recall_at_k": report.get("retrieval_recall_at_k", 0.0),
        "average_faithfulness_score": report.get("average_faithfulness_score", 0.0),
        "average_latency_ms": report.get("average_latency_ms", 0.0),
        "estimated_cost_usd": report.get("estimated_cost_usd", 0.0),
        "question_count": len(per_question_results),
        "failed_retrieval_count": len(failed_retrievals),
        "missing_expected_point_count": missing_answer_points,
    }


def per_question_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in report.get("per_question_results", []):
        answer_eval = item.get("answer_eval") or {}
        rows.append(
            {
                "question_id": item.get("question_id", ""),
                "question": item.get("question", ""),
                "recall_at_k": item.get("recall_at_k", 0.0),
                "faithfulness_score": answer_eval.get("faithfulness_score", ""),
                "has_citations": answer_eval.get("has_citations", ""),
                "citation_coverage": answer_eval.get("citation_coverage", ""),
                "latency_ms": item.get("latency_ms", 0.0),
                "answer_latency_ms": item.get("answer_latency_ms", 0.0),
                "expected_doc_ids": ", ".join(item.get("expected_doc_ids", [])),
                "avoided_doc_ids": ", ".join(item.get("avoided_doc_ids", [])),
                "retrieved_doc_ids": ", ".join(item.get("retrieved_doc_ids", [])),
                "avoided_doc_ids_found": ", ".join(item.get("avoided_doc_ids_found", [])),
                "avoided_doc_ids_pass": item.get("avoided_doc_ids_pass", ""),
                "missing_expected_points": "; ".join(answer_eval.get("missing_expected_points") or []),
            }
        )
    return rows


def markdown_summary(report: dict[str, Any]) -> str:
    summary = summarize_report(report)
    rows = per_question_rows(report)
    lines = [
        f"# RAG Evaluation Report: {summary['experiment_name']}",
        "",
        "## Summary",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp: `{summary['timestamp']}`",
        f"- Retrieval recall@k: `{summary['retrieval_recall_at_k']}`",
        f"- Average faithfulness score: `{summary['average_faithfulness_score']}`",
        f"- Average latency: `{summary['average_latency_ms']} ms`",
        f"- Estimated cost: `${summary['estimated_cost_usd']}`",
        f"- Questions: `{summary['question_count']}`",
        f"- Failed retrievals: `{summary['failed_retrieval_count']}`",
        f"- Missing expected answer points: `{summary['missing_expected_point_count']}`",
        "",
        "## Configuration",
        "",
        f"- Top-k: `{summary['top_k']}`",
        f"- Chunk size: `{summary['chunk_size']}`",
        f"- Chunk overlap: `{summary['chunk_overlap']}`",
        "",
        "## Per-Question Results",
        "",
        "| ID | Recall@k | Faithfulness | Citations | Missing Points |",
        "| --- | ---: | ---: | --- | --- |",
    ]

    for row in rows:
        citation_status = "yes" if row["has_citations"] else "no"
        missing_points = row["missing_expected_points"] or "none"
        lines.append(
            f"| {row['question_id']} | {row['recall_at_k']} | {row['faithfulness_score']} | "
            f"{citation_status} | {missing_points} |"
        )

    lines.append("")
    return "\n".join(lines)


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_summary(report), encoding="utf-8")


def write_csv_report(report: dict[str, Any], output_path: Path) -> None:
    rows = per_question_rows(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "question_id",
        "question",
        "recall_at_k",
        "faithfulness_score",
        "has_citations",
        "citation_coverage",
        "latency_ms",
        "answer_latency_ms",
        "expected_doc_ids",
        "avoided_doc_ids",
        "retrieved_doc_ids",
        "avoided_doc_ids_found",
        "avoided_doc_ids_pass",
        "missing_expected_points",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_report(report_path: Path, output_dir: Path) -> tuple[Path, Path]:
    report = load_report(report_path)
    stem = report_path.stem
    markdown_path = output_dir / f"{stem}_summary.md"
    csv_path = output_dir / f"{stem}_questions.csv"
    write_markdown_report(report, markdown_path)
    write_csv_report(report, csv_path)
    return markdown_path, csv_path
