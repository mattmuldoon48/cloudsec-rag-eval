from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Document(BaseModel):
    doc_id: str
    title: str
    source_path: str
    text: str


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    source_path: str
    chunk_index: int
    text: str


class RetrievedChunk(Chunk):
    score: float


class EvalQuestion(BaseModel):
    id: str
    question: str
    expected_doc_ids: List[str]
    expected_answer_points: List[str] = Field(default_factory=list)


class GeneratedAnswer(BaseModel):
    question_id: str
    question: str
    answer: str
    citations: List[str]
    retrieved_chunks: List[RetrievedChunk]


class EvalRunResult(BaseModel):
    run_id: str
    timestamp: str
    config: dict
    retrieval_recall_at_k: float
    average_faithfulness_score: float = 0.0
    average_latency_ms: float
    estimated_cost_usd: float
    per_question_results: List[dict]
