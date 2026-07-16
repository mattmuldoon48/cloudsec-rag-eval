from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import numpy as np

from .schemas import Chunk


def save_index(chunks: Iterable[Chunk], embeddings: np.ndarray, config: dict, index_dir: Path) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    chunks_path = index_dir / "chunks.jsonl"
    embeddings_path = index_dir / "embeddings.npy"
    config_path = index_dir / "index_config.json"

    with chunks_path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(chunk.model_dump_json() + "\n")

    np.save(embeddings_path, embeddings)

    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)


def load_chunks(index_dir: Path) -> List[Chunk]:
    chunks_path = index_dir / "chunks.jsonl"
    chunks: list[Chunk] = []
    with chunks_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            chunks.append(Chunk.model_validate_json(line))
    return chunks


def load_embeddings(index_dir: Path) -> np.ndarray:
    embeddings_path = index_dir / "embeddings.npy"
    return np.load(embeddings_path)


def _validate_index_artifacts(index_dir: Path, chunks: List[Chunk], embeddings: np.ndarray) -> None:
    if not chunks:
        raise ValueError(
            f"Invalid index artifacts in {index_dir}: chunks.jsonl contains 0 chunks"
        )

    if (
        embeddings.ndim != 2
        or embeddings.size == 0
        or not np.issubdtype(embeddings.dtype, np.number)
    ):
        raise ValueError(
            f"Invalid index artifacts in {index_dir}: embeddings.npy must be a nonempty 2-D "
            f"numeric array; observed shape={embeddings.shape}, dtype={embeddings.dtype}"
        )

    if embeddings.shape[0] != len(chunks):
        raise ValueError(
            f"Invalid index artifacts in {index_dir}: embeddings.npy row count "
            f"{embeddings.shape[0]} does not match chunks.jsonl count {len(chunks)} "
            f"(observed shape={embeddings.shape})"
        )


def load_index(index_dir: Path) -> tuple[List[Chunk], np.ndarray, dict]:
    chunks = load_chunks(index_dir)
    embeddings = load_embeddings(index_dir)
    _validate_index_artifacts(index_dir, chunks, embeddings)
    config_path = index_dir / "index_config.json"
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    return chunks, embeddings, config
