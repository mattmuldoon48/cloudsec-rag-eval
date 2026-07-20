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
