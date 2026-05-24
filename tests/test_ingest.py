from cloudsec_rag.ingest import load_raw_documents


def test_load_raw_documents_applies_manifest_metadata(tmp_path):
    raw_dir = tmp_path / "raw_docs"
    raw_dir.mkdir()
    doc_path = raw_dir / "sample.md"
    doc_path.write_text("# Original Title\n\nBody", encoding="utf-8")
    manifest_path = tmp_path / "doc_manifest.json"
    manifest_path.write_text(
        """
        {
          "documents": [
            {
              "doc_id": "sample",
              "title": "Manifest Title",
              "source_type": "official",
              "source_url": "https://example.com/sample",
              "is_official": true,
              "notes": "Test metadata"
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    documents = load_raw_documents(raw_dir, manifest_path)

    assert len(documents) == 1
    assert documents[0].title == "Manifest Title"
    assert documents[0].source_type == "official"
    assert documents[0].source_url == "https://example.com/sample"
    assert documents[0].is_official is True
    assert documents[0].notes == "Test metadata"


def test_load_raw_documents_skips_readme(tmp_path):
    raw_dir = tmp_path / "raw_docs"
    raw_dir.mkdir()
    (raw_dir / "README.md").write_text("# Instructions", encoding="utf-8")
    (raw_dir / "doc.md").write_text("# Doc\n\nBody", encoding="utf-8")

    documents = load_raw_documents(raw_dir)

    assert [document.doc_id for document in documents] == ["doc"]
