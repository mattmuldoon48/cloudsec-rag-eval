import json

import numpy as np
import pytest

from cloudsec_rag.index_store import load_index, save_index
from cloudsec_rag.schemas import Chunk


def _chunk(index: int) -> Chunk:
    return Chunk(
        chunk_id=f"doc-{index}",
        doc_id="doc",
        title="Title",
        source_path="doc.md",
        chunk_index=index,
        text=f"chunk {index}",
    )


def _save_artifacts(index_dir, chunks, embeddings) -> dict:
    config = {"embedding_model": "test-model", "dimensions": 2}
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "chunks.jsonl").write_text(
        "".join(chunk.model_dump_json() + "\n" for chunk in chunks),
        encoding="utf-8",
    )
    np.save(index_dir / "embeddings.npy", embeddings)
    (index_dir / "index_config.json").write_text(json.dumps(config), encoding="utf-8")
    return config


def test_load_index_returns_valid_artifacts_unchanged(tmp_path):
    index_dir = tmp_path / "index"
    chunks = [_chunk(0), _chunk(1)]
    embeddings = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
    config = {"embedding_model": "test-model", "dimensions": 2}
    save_index(iter(chunks), embeddings, config, index_dir)

    loaded_chunks, loaded_embeddings, loaded_config = load_index(index_dir)

    assert loaded_chunks == chunks
    np.testing.assert_array_equal(loaded_embeddings, embeddings)
    assert loaded_embeddings.dtype == embeddings.dtype
    assert loaded_config == config


@pytest.mark.parametrize("existing_index", [False, True])
def test_invalid_rebuild_preserves_index_artifacts(tmp_path, existing_index):
    index_dir = tmp_path / "index"
    chunks = [_chunk(0), _chunk(1)]
    embeddings = np.eye(2, dtype=np.float32)
    original_config = {"embedding_model": "original-model"}
    if existing_index:
        save_index(chunks, embeddings, original_config, index_dir)
        original_files = {path.name: path.read_bytes() for path in index_dir.iterdir()}

    with pytest.raises(ValueError):
        save_index(iter(chunks), np.ones((1, 2)), {"embedding_model": "replacement"}, index_dir)

    if existing_index:
        assert {path.name: path.read_bytes() for path in index_dir.iterdir()} == original_files
        loaded_chunks, loaded_embeddings, loaded_config = load_index(index_dir)
        assert loaded_chunks == chunks
        np.testing.assert_array_equal(loaded_embeddings, embeddings)
        assert loaded_config == original_config
    else:
        assert not index_dir.exists()


def test_load_index_rejects_duplicate_chunk_ids(tmp_path):
    index_dir = tmp_path / "index"
    chunks = [_chunk(0), _chunk(0)]
    _save_artifacts(index_dir, chunks, np.ones((2, 2)))

    with pytest.raises(ValueError) as exc_info:
        load_index(index_dir)

    message = str(exc_info.value)
    assert str(index_dir) in message
    assert "duplicate chunk IDs: doc-0" in message


@pytest.mark.parametrize("embedding_rows", [1, 3])
def test_load_index_rejects_embedding_row_count_mismatch(tmp_path, embedding_rows):
    index_dir = tmp_path / "index"
    _save_artifacts(index_dir, [_chunk(0), _chunk(1)], np.ones((embedding_rows, 2)))

    with pytest.raises(ValueError) as exc_info:
        load_index(index_dir)

    message = str(exc_info.value)
    assert str(index_dir) in message
    assert "embeddings.npy row count" in message
    assert f"{embedding_rows} does not match chunks.jsonl count 2" in message
    assert f"observed shape=({embedding_rows}, 2)" in message


def test_load_index_rejects_empty_chunks(tmp_path):
    index_dir = tmp_path / "index"
    _save_artifacts(index_dir, [], np.ones((1, 2)))

    with pytest.raises(ValueError) as exc_info:
        load_index(index_dir)

    message = str(exc_info.value)
    assert str(index_dir) in message
    assert "chunks.jsonl contains 0 chunks" in message


def test_load_index_rejects_empty_embeddings(tmp_path):
    index_dir = tmp_path / "index"
    _save_artifacts(index_dir, [_chunk(0)], np.empty((0, 2)))

    with pytest.raises(ValueError) as exc_info:
        load_index(index_dir)

    message = str(exc_info.value)
    assert str(index_dir) in message
    assert "embeddings.npy must be a nonempty 2-D numeric array" in message
    assert "observed shape=(0, 2)" in message


def test_load_index_rejects_non_2d_embeddings(tmp_path):
    index_dir = tmp_path / "index"
    _save_artifacts(index_dir, [_chunk(0), _chunk(1)], np.ones(2))

    with pytest.raises(ValueError) as exc_info:
        load_index(index_dir)

    message = str(exc_info.value)
    assert str(index_dir) in message
    assert "embeddings.npy must be a nonempty 2-D numeric array" in message
    assert "observed shape=(2,)" in message


def test_load_index_rejects_non_numeric_embeddings(tmp_path):
    index_dir = tmp_path / "index"
    _save_artifacts(index_dir, [_chunk(0)], np.array([["not-a-number"]]))

    with pytest.raises(ValueError) as exc_info:
        load_index(index_dir)

    message = str(exc_info.value)
    assert str(index_dir) in message
    assert "embeddings.npy must be a nonempty 2-D numeric array" in message
    assert "dtype=<U12" in message


@pytest.mark.parametrize("invalid_value", [float("nan"), float("inf"), float("-inf")])
def test_load_index_rejects_non_finite_embeddings(tmp_path, invalid_value):
    index_dir = tmp_path / "index"
    _save_artifacts(
        index_dir,
        [_chunk(0)],
        np.array([[invalid_value, 0.1]], dtype=np.float32),
    )

    with pytest.raises(ValueError) as exc_info:
        load_index(index_dir)

    message = str(exc_info.value)
    assert str(index_dir) in message
    assert "embeddings.npy must contain only finite values" in message
