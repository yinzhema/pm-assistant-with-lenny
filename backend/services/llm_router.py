"""
Tiered LLM router — selects model based on task complexity.

FRONTIER_MODEL (env): used for expensive/complex tasks
  - Full artifact synthesis after Q&A collection
  - PRD → agent.md translation
  - Gap analysis

EFFICIENT_MODEL (env): used for fast/real-time tasks
  - Per-answer live preview section updates (<500ms required)
  - Inline KB chat overlay
  - Clarifying Q&A to fill gaps
  - Existing chat endpoint (unchanged)
"""
import os
from enum import Enum
from typing import AsyncIterator

from openai import AsyncOpenAI


class LLMTier(str, Enum):
    FRONTIER = "frontier"
    EFFICIENT = "efficient"


class LLMRouter:
    def __init__(self):
        self.frontier = os.getenv("FRONTIER_MODEL", "gpt-4.1")
        self.efficient = os.getenv("EFFICIENT_MODEL", "gpt-4o-mini")
        self._client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _model(self, tier: LLMTier) -> str:
        return self.frontier if tier == LLMTier.FRONTIER else self.efficient

    async def achat_stream(
        self,
        messages: list[dict],
        tier: LLMTier,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Stream token deltas from the selected model tier."""
        stream = await self._client.chat.completions.create(
            model=self._model(tier),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def achat(
        self,
        messages: list[dict],
        tier: LLMTier,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Single non-streaming call — returns full response text."""
        resp = await self._client.chat.completions.create(
            model=self._model(tier),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )
        return resp.choices[0].message.content or ""
