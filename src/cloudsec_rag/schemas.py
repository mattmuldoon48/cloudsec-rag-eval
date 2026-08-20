from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator


class Document(BaseModel):
    doc_id: str
    title: str
    source_path: str
    text: str
    source_type: str = "sample"
    source_url: str | None = None
    is_official: bool = False
    notes: str | None = None


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    source_path: str
    chunk_index: int
    text: str
    source_type: str = "sample"
    source_url: str | None = None
    is_official: bool = False
    notes: str | None = None


class RetrievedChunk(Chunk):
    score: float


class EvalQuestion(BaseModel):
    id: str
    question: str
    expected_doc_ids: List[str] = Field(min_length=1)
    expected_answer_points: List[str] = Field(default_factory=list)
    avoided_doc_ids: List[str] = Field(default_factory=list)

    @field_validator("id", "question")
    def required_text_must_not_be_blank(cls, value: str, info):
        if not value.strip():
            raise ValueError(f"{info.field_name} must not be blank")
        return value

    @field_validator("expected_doc_ids", "avoided_doc_ids")
    def document_ids_must_not_be_blank(cls, value: List[str], info):
        if any(not doc_id.strip() for doc_id in value):
            raise ValueError(f"{info.field_name} entries must not be blank")
        return value

    @model_validator(mode="after")
    def expected_and_avoided_documents_must_not_overlap(self) -> "EvalQuestion":
        overlap = sorted(set(self.expected_doc_ids) & set(self.avoided_doc_ids))
        if overlap:
            raise ValueError(
                "expected_doc_ids and avoided_doc_ids must not overlap: "
                + ", ".join(overlap)
            )
        return self


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
