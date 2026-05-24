from __future__ import annotations

from typing import List

import numpy as np
from sklearn.neighbors import NearestNeighbors

from .llm_client import LLMClient
from .schemas import Chunk, RetrievedChunk


def build_retriever(embeddings: np.ndarray, n_neighbors: int = 3) -> NearestNeighbors:
    if embeddings.size == 0:
        raise ValueError("Embeddings matrix is empty")

    retriever = NearestNeighbors(
        n_neighbors=min(n_neighbors, len(embeddings)),
        metric="cosine",
        algorithm="brute",
        n_jobs=-1,
    )
    retriever.fit(embeddings)
    return retriever


def retrieve_chunks(
    query: str,
    chunks: List[Chunk],
    embeddings: np.ndarray,
    llm_client: LLMClient,
    top_k: int = 3,
) -> List[RetrievedChunk]:
    if embeddings.size == 0:
        return []

    query_embedding = np.asarray(llm_client.embed_texts([query]), dtype=np.float32)
    retriever = build_retriever(embeddings, n_neighbors=top_k)
    distances, indices = retriever.kneighbors(query_embedding)
    results: list[RetrievedChunk] = []

    for score, idx in zip(distances[0], indices[0]):
        chunk = chunks[int(idx)]
        results.append(
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                title=chunk.title,
                source_path=chunk.source_path,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                source_type=chunk.source_type,
                source_url=chunk.source_url,
                is_official=chunk.is_official,
                notes=chunk.notes,
                score=float(1.0 - score),
            )
        )

    return results
