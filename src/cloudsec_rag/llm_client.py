from __future__ import annotations

from typing import List

from openai import OpenAI

from .config import Settings


class LLMClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for embedding and generation calls")
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def embed_texts(self, texts: List[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        response = self.client.responses.create(
            model=self.settings.openai_generation_model,
            input=prompt,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        return getattr(response, "output_text", None) or str(response)
