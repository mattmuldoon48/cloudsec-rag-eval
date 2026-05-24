from __future__ import annotations

from pathlib import Path
from typing import List

from .llm_client import LLMClient
from .schemas import GeneratedAnswer, RetrievedChunk


def build_evidence_section(retrieved_chunks: List[RetrievedChunk]) -> str:
    lines: list[str] = []
    for index, chunk in enumerate(retrieved_chunks, start=1):
        lines.append(
            f"[{index}] {chunk.title} | {chunk.source_path}\n{chunk.text}"
        )
    return "\n\n".join(lines)


def load_prompt_template(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8")


def generate_answer(
    question_id: str,
    question: str,
    retrieved_chunks: List[RetrievedChunk],
    llm_client: LLMClient,
    prompt_path: Path,
) -> GeneratedAnswer:
    prompt_template = load_prompt_template(prompt_path)
    evidence_section = build_evidence_section(retrieved_chunks)
    prompt = prompt_template.format(question=question, evidence=evidence_section)
    answer_text = llm_client.generate_text(prompt)
    citations = [f"[{i}]" for i in range(1, len(retrieved_chunks) + 1)]

    return GeneratedAnswer(
        question_id=question_id,
        question=question,
        answer=answer_text.strip(),
        citations=citations,
        retrieved_chunks=retrieved_chunks,
    )
