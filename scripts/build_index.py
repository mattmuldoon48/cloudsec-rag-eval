import _bootstrap  # noqa: F401

import argparse
from pathlib import Path

from cloudsec_rag.chunk import chunk_documents
from cloudsec_rag.config import load_settings
from cloudsec_rag.embed import embed_chunks
from cloudsec_rag.index_store import save_index
from cloudsec_rag.ingest import ingest_raw_docs, load_raw_documents
from cloudsec_rag.llm_client import LLMClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local vector index for a RAG experiment.")
    parser.add_argument("--config", type=Path, default=None, help="Optional experiment config JSON file")
    args = parser.parse_args()

    settings = load_settings(args.config)
    print("Running ingestion to produce processed docs and chunks...")
    ingest_raw_docs(settings)

    llm_client = LLMClient(settings)
    docs = load_raw_documents(settings.raw_docs_dir, settings.doc_manifest_path)
    chunk_list = chunk_documents(docs, settings.chunk_size, settings.chunk_overlap)

    print(f"Embedding {len(chunk_list)} chunks...")
    embeddings = embed_chunks(chunk_list, llm_client)
    save_index(
        chunk_list,
        embeddings,
        {
            "experiment_name": settings.experiment_name,
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "top_k": settings.top_k,
            "embedding_model": settings.openai_embedding_model,
            "generation_model": settings.openai_generation_model,
        },
        settings.indexes_dir,
    )
    print(f"Saved index artifacts for '{settings.experiment_name}' to {settings.indexes_dir}")


if __name__ == "__main__":
    main()
