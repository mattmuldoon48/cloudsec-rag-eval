import csv
import json

from markdown_it import MarkdownIt

from cloudsec_rag.export_report import export_report, summarize_report


def sample_report() -> dict:
    return {
        "run_id": "run-1",
        "timestamp": "2026-05-24T22:33:18Z",
        "config": {
            "experiment_name": "baseline",
            "top_k": 3,
            "chunk_size": 700,
            "chunk_overlap": 100,
        },
        "retrieval_recall_at_k": 1.0,
        "average_faithfulness_score": 0.9,
        "average_latency_ms": 250.0,
        "estimated_cost_usd": 0.001,
        "per_question_results": [
            {
                "question_id": "q1",
                "question": "What helps least privilege?",
                "expected_doc_ids": ["iam"],
                "avoided_doc_ids": [],
                "retrieved_doc_ids": ["iam", "logs"],
                "avoided_doc_ids_found": [],
                "avoided_doc_ids_pass": True,
                "recall_at_k": 1.0,
                "latency_ms": 100.0,
                "answer_latency_ms": 400.0,
                "answer_eval": {
                    "faithfulness_score": 0.9,
                    "has_citations": True,
                    "citation_coverage": 1.0,
                    "missing_expected_points": [],
                },
            }
        ],
    }


def test_summarize_report_counts_questions_and_metrics():
    summary = summarize_report(sample_report())

    assert summary["experiment_name"] == "baseline"
    assert summary["question_count"] == 1
    assert summary["failed_retrieval_count"] == 0
    assert summary["average_faithfulness_score"] == 0.9


def test_export_preserves_multiline_markdown_cells_and_original_csv_values(tmp_path):
    report = sample_report()
    question_id = "q\\|1\r\ncontinued"
    missing_point = "grant|deny\nreview access"
    report["per_question_results"][0]["question_id"] = question_id
    report["per_question_results"][0]["answer_eval"]["missing_expected_points"] = [missing_point]
    report_path = tmp_path / "run.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    markdown_path, csv_path = export_report(report_path, tmp_path / "summaries")

    tokens = MarkdownIt("commonmark").enable("table").parse(
        markdown_path.read_text(encoding="utf-8")
    )
    assert sum(token.type == "tr_open" for token in tokens) == 2
    assert sum(token.type == "td_open" for token in tokens) == 5
    cells = [token for token in tokens if token.type == "inline"][-5:]
    cell_text = [
        "".join(child.content for child in cell.children if child.type == "text")
        for cell in cells
    ]
    assert cell_text == ["q\\|1continued", "1.0", "0.9", "yes", "grant|denyreview access"]
    with csv_path.open(encoding="utf-8", newline="") as handle:
        row, = csv.DictReader(handle)
    assert row["question_id"] == question_id
    assert row["missing_expected_points"] == missing_point


def test_export_report_writes_markdown_and_csv(tmp_path):
    report_path = tmp_path / "run.json"
    report_path.write_text(
        """{
          "run_id": "run-1",
          "timestamp": "2026-05-24T22:33:18Z",
          "config": {"experiment_name": "baseline", "top_k": 3, "chunk_size": 700, "chunk_overlap": 100},
          "retrieval_recall_at_k": 1.0,
          "average_faithfulness_score": 0.9,
          "average_latency_ms": 250.0,
          "estimated_cost_usd": 0.001,
          "per_question_results": [
            {
              "question_id": "q1",
              "question": "What helps least privilege?",
              "expected_doc_ids": ["iam"],
              "avoided_doc_ids": [],
              "retrieved_doc_ids": ["iam"],
              "avoided_doc_ids_found": [],
              "avoided_doc_ids_pass": true,
              "recall_at_k": 1.0,
              "latency_ms": 100.0,
              "answer_latency_ms": 400.0,
              "answer_eval": {
                "faithfulness_score": 0.9,
                "has_citations": true,
                "citation_coverage": 1.0,
                "missing_expected_points": []
              }
            }
          ]
        }""",
        encoding="utf-8",
    )

    markdown_path, csv_path = export_report(report_path, tmp_path / "summaries")

    assert markdown_path.exists()
    assert csv_path.exists()
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["question_id"] == "q1"
    assert "avoided_doc_ids_pass" in rows[0]
