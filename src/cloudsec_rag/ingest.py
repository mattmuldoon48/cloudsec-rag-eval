from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .chunk import chunk_documents
from .config import Settings
from .schemas import Chunk, Document


def load_raw_documents(raw_dir: Path) -> List[Document]:
    raw_dir = raw_dir.expanduser()
    documents: list[Document] = []

    source_paths = sorted(raw_dir.glob("*.md")) + sorted(raw_dir.glob("*.txt"))
    for path in source_paths:
        if path.name.lower() == "readme.md":
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        doc_id = path.stem
        title = text.splitlines()[0].strip("# ") if text else doc_id
        documents.append(
            Document(
                doc_id=doc_id,
                title=title,
                source_path=str(path),
                text=text,
            )
        )

    return documents


def save_jsonl(records: Iterable[Document | Chunk], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(record.model_dump_json() + "\n")


def ingest_raw_docs(settings: Settings | None = None) -> list[Document]:
    settings = settings or Settings()
    documents = load_raw_documents(settings.raw_docs_dir)
    save_jsonl(documents, settings.processed_dir / "docs.jsonl")

    chunks = chunk_documents(documents, settings.chunk_size, settings.chunk_overlap)
    save_jsonl(chunks, settings.processed_dir / "chunks.jsonl")

    return documents
