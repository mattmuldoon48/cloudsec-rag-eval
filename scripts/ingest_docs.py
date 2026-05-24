import _bootstrap  # noqa: F401

from cloudsec_rag.config import Settings
from cloudsec_rag.ingest import ingest_raw_docs


def main() -> None:
    settings = Settings()
    documents = ingest_raw_docs(settings)
    print(f"Ingested {len(documents)} raw documents into {settings.processed_dir}")


if __name__ == "__main__":
    main()
