from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ExperimentConfig(BaseModel):
    experiment_name: str = "default"
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    top_k: int | None = None
    indexes_dir: Path | None = None
    eval_set_path: Path | None = None
    answer_prompt_path: Path | None = None
    faithfulness_judge_prompt_path: Path | None = None


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_generation_model: str = Field(
        default="gpt-4.1-mini",
        validation_alias="OPENAI_GENERATION_MODEL",
    )
    experiment_name: str = "default"
    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k: int = 3
    raw_docs_dir: Path = Path("data/raw_docs")
    doc_manifest_path: Path = Path("data/doc_manifest.json")
    processed_dir: Path = Path("data/processed")
    indexes_dir: Path = Path("data/indexes")
    eval_set_path: Path = Path("data/eval_sets/cloudsec_eval_v1.jsonl")
    answer_prompt_path: Path = Path("prompts/answer_v1.txt")
    faithfulness_judge_prompt_path: Path = Path("prompts/faithfulness_judge_v1.txt")
    run_reports_dir: Path = Path("reports/runs")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        arbitrary_types_allowed=True,
        extra="ignore",
    )


def load_experiment_config(config_path: Path) -> ExperimentConfig:
    with config_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return ExperimentConfig.model_validate(data)


def load_settings(config_path: Path | None = None) -> Settings:
    settings = Settings()
    if config_path is None:
        return settings

    experiment_config = load_experiment_config(config_path)
    updates = experiment_config.model_dump(exclude_none=True)
    merged = settings.model_dump()
    merged.update(updates)
    return Settings.model_validate(merged)
