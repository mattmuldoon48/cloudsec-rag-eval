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


def load_index(index_dir: Path) -> tuple[List[Chunk], np.ndarray, dict]:
    chunks = load_chunks(index_dir)
    embeddings = load_embeddings(index_dir)
    config_path = index_dir / "index_config.json"
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    return chunks, embeddings, config
