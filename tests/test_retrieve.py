from unittest.mock import Mock

import numpy as np
import pytest

from cloudsec_rag.llm_client import LLMClient
from cloudsec_rag.retrieve import retrieve_chunks
from cloudsec_rag.schemas import Chunk


def test_top_k_larger_than_index_returns_all_chunks_in_similarity_order():
    chunks = [
        Chunk(
            chunk_id=name,
            doc_id=name,
            title=name,
            source_path=f"{name}.md",
            chunk_index=0,
            text=name,
        )
        for name in ["orthogonal", "aligned", "opposite"]
    ]
    embeddings = np.array([[0, 1], [1, 0], [-1, 0]], dtype=np.float32)
    client = Mock(spec=LLMClient)
    client.embed_texts.return_value = [[1, 0]]

    results = retrieve_chunks("query", chunks, embeddings, client, top_k=5)

    assert [result.chunk_id for result in results] == ["aligned", "orthogonal", "opposite"]
    assert [result.score for result in results] == pytest.approx([1.0, 0.0, -1.0])


def test_empty_index_returns_no_results_with_unavailable_embedding_provider():
    client = Mock(spec=LLMClient)
    client.embed_texts.side_effect = RuntimeError("Embedding provider unavailable")

    results = retrieve_chunks("query", [], np.empty((0, 2)), client)

    assert results == []
