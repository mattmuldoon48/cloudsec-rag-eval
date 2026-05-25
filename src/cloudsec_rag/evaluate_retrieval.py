from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import List

from .config import Settings
from .evaluate_answers import evaluate_generated_answer
from .generate import generate_answer
from .index_store import load_index
from .llm_client import LLMClient
from .metrics import average_latency_ms, estimate_cost_usd, recall_at_k
from .retrieve import retrieve_chunks
from .schemas import EvalQuestion, EvalRunResult


def load_eval_questions(eval_path: Path) -> List[EvalQuestion]:
    questions: list[EvalQuestion] = []
    with eval_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            questions.append(EvalQuestion.model_validate_json(line))
    return questions


def evaluate_retrieval(settings: Settings | None = None) -> EvalRunResult:
    settings = settings or Settings()
    chunks, embeddings, config = load_index(settings.indexes_dir)
    llm_client = LLMClient(settings)
    questions = load_eval_questions(settings.eval_set_path)
    judge_prompt_template = settings.faithfulness_judge_prompt_path.read_text(encoding="utf-8")

    per_question_results: list[dict] = []
    latencies: list[float] = []
    answer_latencies: list[float] = []
    faithfulness_scores: list[float] = []
    approximate_token_count = 0

    for question in questions:
        start = time.perf_counter()
        retrieved_chunks = retrieve_chunks(
            question.question,
            chunks,
            embeddings,
            llm_client,
            top_k=settings.top_k,
        )
        duration = time.perf_counter() - start
        latencies.append(duration)

        retrieved_doc_ids = [chunk.doc_id for chunk in retrieved_chunks]
        question_recall = recall_at_k(retrieved_doc_ids, question.expected_doc_ids)
        avoided_doc_ids_found = sorted(set(retrieved_doc_ids).intersection(question.avoided_doc_ids))

        answer_start = time.perf_counter()
        generated_answer = generate_answer(
            question_id=question.id,
            question=question.question,
            retrieved_chunks=retrieved_chunks,
            llm_client=llm_client,
            prompt_path=settings.answer_prompt_path,
        )
        answer_eval = evaluate_generated_answer(
            question=question,
            answer=generated_answer,
            llm_client=llm_client,
            judge_prompt_template=judge_prompt_template,
        )
        answer_duration = time.perf_counter() - answer_start
        answer_latencies.append(answer_duration)
        faithfulness_scores.append(answer_eval["faithfulness_score"])
        approximate_token_count += (
            len(question.question)
            + len(generated_answer.answer)
            + sum(len(chunk.text) for chunk in retrieved_chunks)
        ) // 4

        per_question_results.append(
            {
                "question_id": question.id,
                "question": question.question,
                "expected_doc_ids": question.expected_doc_ids,
                "avoided_doc_ids": question.avoided_doc_ids,
                "retrieved_doc_ids": retrieved_doc_ids,
                "recall_at_k": question_recall,
                "avoided_doc_ids_found": avoided_doc_ids_found,
                "avoided_doc_ids_pass": not avoided_doc_ids_found,
                "latency_ms": round(duration * 1000.0, 2),
                "answer_latency_ms": round(answer_duration * 1000.0, 2),
                "answer": generated_answer.answer,
                "answer_eval": answer_eval,
            }
        )

    run_id = str(uuid.uuid4())
    average_latency = average_latency_ms(latencies + answer_latencies)
    estimated_cost = estimate_cost_usd(
        num_embeddings=len(questions),
        num_generation_tokens=approximate_token_count,
    )

    return EvalRunResult(
        run_id=run_id,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        config={
            "experiment_name": settings.experiment_name,
            "top_k": settings.top_k,
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "embedding_model": settings.openai_embedding_model,
            "generation_model": settings.openai_generation_model,
            "answer_prompt": str(settings.answer_prompt_path),
            "faithfulness_judge_prompt": str(settings.faithfulness_judge_prompt_path),
        },
        retrieval_recall_at_k=round(sum(item["recall_at_k"] for item in per_question_results) / max(len(per_question_results), 1), 4),
        average_faithfulness_score=round(sum(faithfulness_scores) / max(len(faithfulness_scores), 1), 4),
        average_latency_ms=round(average_latency, 2),
        estimated_cost_usd=estimated_cost,
        per_question_results=per_question_results,
    )


def save_eval_report(report: EvalRunResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(report.model_dump_json(indent=2))
