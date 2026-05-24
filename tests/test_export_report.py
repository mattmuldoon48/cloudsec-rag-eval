import csv

from cloudsec_rag.export_report import export_report, markdown_summary, summarize_report


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
                "retrieved_doc_ids": ["iam", "logs"],
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


def test_markdown_summary_includes_key_sections():
    markdown = markdown_summary(sample_report())

    assert "# RAG Evaluation Report: baseline" in markdown
    assert "## Per-Question Results" in markdown
    assert "| q1 | 1.0 | 0.9 | yes | none |" in markdown


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
              "retrieved_doc_ids": ["iam"],
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
