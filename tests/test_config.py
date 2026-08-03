import pytest
from pydantic import ValidationError

from cloudsec_rag.config import load_settings


def test_load_settings_applies_experiment_config(tmp_path):
    config_path = tmp_path / "experiment.json"
    config_path.write_text(
        """
        {
          "experiment_name": "tiny_chunks",
          "chunk_size": 300,
          "chunk_overlap": 50,
          "top_k": 2,
          "indexes_dir": "data/indexes/tiny_chunks"
        }
        """,
        encoding="utf-8",
    )

    settings = load_settings(config_path)

    assert settings.experiment_name == "tiny_chunks"
    assert settings.chunk_size == 300
    assert settings.chunk_overlap == 50
    assert settings.top_k == 2
    assert str(settings.indexes_dir) == "data/indexes/tiny_chunks"


@pytest.mark.parametrize("top_k", [0, -1])
def test_load_settings_rejects_non_positive_top_k(tmp_path, top_k):
    config_path = tmp_path / "experiment.json"
    config_path.write_text(f'{{"top_k": {top_k}}}', encoding="utf-8")

    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        load_settings(config_path)


def test_load_settings_rejects_unknown_experiment_fields(tmp_path):
    config_path = tmp_path / "experiment.json"
    config_path.write_text('{"topk": 7}', encoding="utf-8")

    with pytest.raises(ValidationError, match="topk"):
        load_settings(config_path)


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [(0, 0), (100, -1)],
)
def test_load_settings_rejects_invalid_chunk_dimensions(
    tmp_path,
    chunk_size,
    chunk_overlap,
):
    config_path = tmp_path / "experiment.json"
    config_path.write_text(
        f'{{"chunk_size": {chunk_size}, "chunk_overlap": {chunk_overlap}}}',
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_settings(config_path)


@pytest.mark.parametrize("chunk_overlap", [100, 101])
def test_load_settings_rejects_overlap_not_smaller_than_chunk_size(
    tmp_path,
    chunk_overlap,
):
    config_path = tmp_path / "experiment.json"
    config_path.write_text(
        f'{{"chunk_size": 100, "chunk_overlap": {chunk_overlap}}}',
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="must be smaller than"):
        load_settings(config_path)
