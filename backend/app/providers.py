from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, question: str, context: str) -> str:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    """Bag-of-words style embeddings so offline tests retrieve by shared terms."""

    @staticmethod
    def _token_bucket(token: str) -> int:
        digest = hashlib.md5(token.encode(), usedforsecurity=False).hexdigest()
        return int(digest, 16) % 64

    def _vectorize(self, text: str) -> list[float]:
        tokens = re.findall(r"[a-z0-9']+", text.lower())
        values = [0.0] * 64
        for token in tokens:
            values[self._token_bucket(token)] += 1.0
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vectorize(text) for text in texts]


class MockLLMProvider(LLMProvider):
    def generate(self, question: str, context: str) -> str:
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", context) if s.strip()]
        if not sentences:
            return "I don't have enough information in the provided sources to answer that."
        answer = ". ".join(sentences[:2])
        if not answer.endswith("."):
            answer += "."
        return f"Based on the retrieved documents: {answer}"


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


class OpenAILLMProvider(LLMProvider):
    SYSTEM_PROMPT = (
        "Answer only using the provided context. If the answer is not in the context, "
        "reply exactly: I don't have enough information in the provided sources to answer that."
    )

    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, question: str, context: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                },
            ],
            temperature=0,
        )
        return response.choices[0].message.content or ""
