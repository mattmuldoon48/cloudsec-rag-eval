import json
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

import cloudsec_rag.evaluate_retrieval as evaluation
from cloudsec_rag.chunk import chunk_text
from cloudsec_rag.config import Settings
from cloudsec_rag.index_store import save_index
from cloudsec_rag.llm_client import LLMClient
from cloudsec_rag.run_eval import run_evaluation
from cloudsec_rag.schemas import Chunk


@pytest.mark.parametrize(
    ("index_config", "expected_dimensions"),
    [
        ({"chunk_size": 300, "chunk_overlap": 50, "top_k": 1}, (300, 50)),
        ({}, (None, None)),
    ],
    ids=["stored-build-settings", "unknown-build-settings"],
)
def test_saved_report_describes_loaded_chunks_not_runtime_chunk_settings(
    tmp_path: Path, monkeypatch, index_config, expected_dimensions
):
    texts = chunk_text("A" * 650, chunk_size=300, chunk_overlap=50)
    chunks = [
        Chunk(
            chunk_id=f"doc-{index}", doc_id="doc", title="Offline evidence",
            source_path="doc.md", chunk_index=index, text=text,
        )
        for index, text in enumerate(texts)
    ]
    save_index(
        chunks, np.array([[1.0, 0.0], [0.8, 0.2], [0.0, 1.0]]),
        index_config, tmp_path / "index",
    )
    questions = tmp_path / "questions.jsonl"
    questions.write_text(
        json.dumps({"id": "q1", "question": "What control?", "expected_doc_ids": ["doc"]}) + "\n",
        encoding="utf-8",
    )
    answer_prompt = tmp_path / "answer.txt"
    answer_prompt.write_text("{question}\n{evidence}", encoding="utf-8")
    judge_prompt = tmp_path / "judge.txt"
    judge_prompt.write_text("{question}\n{answer}\n{evidence}", encoding="utf-8")
    settings = Settings(
        _env_file=None, chunk_size=700, chunk_overlap=100, top_k=2,
        indexes_dir=tmp_path / "index", eval_set_path=questions,
        answer_prompt_path=answer_prompt, faithfulness_judge_prompt_path=judge_prompt,
        run_reports_dir=tmp_path / "runs",
    )
    client = Mock(spec=LLMClient)
    client.embed_texts.return_value = [[1.0, 0.0]]
    client.generate_text.side_effect = [
        "Control evidence [1] [2].",
        json.dumps({
            "faithfulness_score": 1.0, "is_faithful": True,
            "unsupported_claims": [], "rationale": "Offline fixture",
        }),
    ]
    monkeypatch.setattr(evaluation, "LLMClient", lambda settings: client)

    run_evaluation(settings)

    saved_path, = settings.run_reports_dir.glob("*.json")
    saved = json.loads(saved_path.read_text(encoding="utf-8"))
    assert (saved["config"]["chunk_size"], saved["config"]["chunk_overlap"]) == expected_dimensions
    assert saved["config"]["top_k"] == 2
    assert saved["per_question_results"][0]["retrieved_doc_ids"] == ["doc", "doc"]
