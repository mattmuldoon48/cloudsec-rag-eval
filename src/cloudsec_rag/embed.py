from __future__ import annotations

import numpy as np
from typing import Iterable, List

from .llm_client import LLMClient
from .schemas import Chunk


def embed_chunks(chunks: Iterable[Chunk], llm_client: LLMClient) -> np.ndarray:
    texts = [chunk.text for chunk in chunks]
    embeddings = llm_client.embed_texts(texts)
    return np.asarray(embeddings, dtype=np.float32)
