from __future__ import annotations

import json
import re
from typing import List

from .generate import build_evidence_section
from .llm_client import LLMClient
from .schemas import EvalQuestion, GeneratedAnswer


def summarize_answer_sources(answer: GeneratedAnswer) -> List[str]:
    return [chunk.source_path for chunk in answer.retrieved_chunks]


def answer_has_citations(answer: GeneratedAnswer) -> bool:
    return bool(extract_citation_numbers(answer.answer))


def extract_citation_numbers(answer_text: str) -> set[int]:
    return {int(match) for match in re.findall(r"\[(\d+)\]", answer_text)}


def citation_coverage(answer: GeneratedAnswer) -> float:
    cited_numbers = extract_citation_numbers(answer.answer)
    if not cited_numbers:
        return 0.0
    valid_numbers = {index for index in range(1, len(answer.retrieved_chunks) + 1)}
    valid_citations = cited_numbers.intersection(valid_numbers)
    return round(len(valid_citations) / len(cited_numbers), 4)


def missing_expected_points(answer_text: str, expected_points: list[str]) -> list[str]:
    answer_terms = _keyword_set(answer_text)
    return [
        point
        for point in expected_points
        if not _point_is_covered(point, answer_terms)
    ]


def _keyword_set(text: str) -> set[str]:
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "be",
        "for",
        "from",
        "in",
        "is",
        "of",
        "or",
        "should",
        "the",
        "to",
        "with",
    }
    terms = re.findall(r"[a-z0-9]+", text.lower())
    return {_stem(term) for term in terms if term not in stopwords}


def _stem(term: str) -> str:
    for suffix in ("ing", "ed"):
        if len(term) > len(suffix) + 3 and term.endswith(suffix):
            return term[: -len(suffix)]
    if len(term) >= 4 and term.endswith("s") and not term.endswith("ss"):
        return term[:-1]
    return term


def _point_is_covered(point: str, answer_terms: set[str]) -> bool:
    point_terms = _keyword_set(point)
    if not point_terms:
        return True
    overlap = point_terms.intersection(answer_terms)
    return len(overlap) / len(point_terms) >= 0.5


def _extract_json_object(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def judge_faithfulness(
    question: str,
    answer: GeneratedAnswer,
    llm_client: LLMClient,
    judge_prompt_template: str,
) -> dict:
    prompt = judge_prompt_template.format(
        question=question,
        answer=answer.answer,
        evidence=build_evidence_section(answer.retrieved_chunks),
    )
    raw_judgment = llm_client.generate_text(prompt, max_tokens=300, temperature=0.0)

    try:
        parsed = _extract_json_object(raw_judgment)
    except json.JSONDecodeError:
        return {
            "faithfulness_score": 0.0,
            "is_faithful": False,
            "unsupported_claims": ["Judge did not return valid JSON."],
            "rationale": raw_judgment.strip(),
        }

    score = float(parsed.get("faithfulness_score", 0.0))
    return {
        "faithfulness_score": max(0.0, min(score, 1.0)),
        "is_faithful": bool(parsed.get("is_faithful", False)),
        "unsupported_claims": list(parsed.get("unsupported_claims", [])),
        "rationale": str(parsed.get("rationale", "")),
    }


def evaluate_generated_answer(
    question: EvalQuestion,
    answer: GeneratedAnswer,
    llm_client: LLMClient,
    judge_prompt_template: str,
) -> dict:
    judgment = judge_faithfulness(
        question=question.question,
        answer=answer,
        llm_client=llm_client,
        judge_prompt_template=judge_prompt_template,
    )
    missing_points = missing_expected_points(answer.answer, question.expected_answer_points)

    return {
        **judgment,
        "has_citations": answer_has_citations(answer),
        "citation_coverage": citation_coverage(answer),
        "missing_expected_points": missing_points,
    }
