import argparse
from pathlib import Path

import _bootstrap  # noqa: F401

from cloudsec_rag.config import load_settings
from cloudsec_rag.generate import generate_answer
from cloudsec_rag.index_store import load_index
from cloudsec_rag.llm_client import LLMClient
from cloudsec_rag.retrieve import retrieve_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a question against the cloud security index.")
    parser.add_argument("question", type=str, help="Question to ask the RAG system")
    parser.add_argument("--config", type=Path, default=None, help="Optional experiment config JSON file")
    args = parser.parse_args()

    settings = load_settings(args.config)
    chunks, embeddings, _ = load_index(settings.indexes_dir)
    llm_client = LLMClient(settings)
    retrieved_chunks = retrieve_chunks(args.question, chunks, embeddings, llm_client, top_k=settings.top_k)

    answer = generate_answer(
        question_id="cli",
        question=args.question,
        retrieved_chunks=retrieved_chunks,
        llm_client=llm_client,
        prompt_path=settings.answer_prompt_path,
    )

    print("\n=== Answer ===")
    print(answer.answer)
    print("\n=== Sources ===")
    for idx, chunk in enumerate(answer.retrieved_chunks, start=1):
        print(f"[{idx}] {chunk.source_path} (score={chunk.score:.3f})")


if __name__ == "__main__":
    main()
