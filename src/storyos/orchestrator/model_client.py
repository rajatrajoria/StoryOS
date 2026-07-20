"""
Provider-agnostic LLM client.

This module is the ONLY place in the codebase that knows about
provider SDKs (OpenAI, Anthropic, etc.).

Every agent communicates with models exclusively through ModelClient.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from anthropic import Anthropic
from openai import OpenAI


# ============================================================
# Provider Enum
# ============================================================


class ModelProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


# ============================================================
# Model Configuration
# ============================================================


@dataclass(slots=True, frozen=True)
class ModelConfig:
    """
    Configuration describing which model an agent should use.
    """

    provider: ModelProvider
    model: str
    temperature: float = 0.2
    max_tokens: int = 4096


# ============================================================
# Unified Model Response
# ============================================================


@dataclass(slots=True)
class ModelResponse:
    """
    Provider-independent model response.
    """

    content: str

    provider: ModelProvider
    model: str
    prompt_version: str

    input_tokens: int
    output_tokens: int

    latency_ms: float
    estimated_cost_usd: float


# ============================================================
# Default Model Map
# ============================================================

DEFAULT_MODEL_MAP: Final[dict[str, ModelConfig]] = {
    "research": ModelConfig(
        provider=ModelProvider.OPENAI,
        model="gpt-5",
    ),
    "angle": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model="claude-sonnet-4-20250514",
    ),
    "outline": ModelConfig(
        provider=ModelProvider.OPENAI,
        model="gpt-5",
    ),
    "draft": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model="claude-sonnet-4-20250514",
    ),
    "critic": ModelConfig(
        provider=ModelProvider.OPENAI,
        model="gpt-5-mini",
    ),
    "fact_check": ModelConfig(
        provider=ModelProvider.OPENAI,
        model="gpt-5",
    ),
    "voice": ModelConfig(
        provider=ModelProvider.OPENAI,
        model="gpt-5-mini",
    ),
    "visual": ModelConfig(
        provider=ModelProvider.OPENAI,
        model="gpt-5-mini",
    ),
}


# ============================================================
# Pricing
# USD per 1M tokens
# ============================================================

_MODEL_PRICING: Final = {
    "gpt-5": {
        "input": 1.25,
        "output": 10.00,
    },
    "gpt-5-mini": {
        "input": 0.25,
        "output": 2.00,
    },
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00,
    },
}


# ============================================================
# Client
# ============================================================


class ModelClient:
    """
    Unified LLM client.

    Agents never directly call provider SDKs.
    They only call `client.complete(...)`.
    """

    def __init__(self) -> None:
        self._openai = OpenAI()
        self._anthropic = Anthropic()

    # --------------------------------------------------------

    def complete(
        self,
        *,
        system_prompt: str,
        user_content: str,
        model_config: ModelConfig,
        prompt_version: str,
    ) -> ModelResponse:
        """
        Execute a completion against the configured provider.
        """

        if model_config.provider == ModelProvider.OPENAI:
            return self._complete_openai(
                system_prompt=system_prompt,
                user_content=user_content,
                model_config=model_config,
                prompt_version=prompt_version,
            )

        if model_config.provider == ModelProvider.ANTHROPIC:
            return self._complete_anthropic(
                system_prompt=system_prompt,
                user_content=user_content,
                model_config=model_config,
                prompt_version=prompt_version,
            )

        raise ValueError(
            f"Unsupported provider: {model_config.provider}"
        )

    # --------------------------------------------------------

    def _complete_openai(
        self,
        *,
        system_prompt: str,
        user_content: str,
        model_config: ModelConfig,
        prompt_version: str,
    ) -> ModelResponse:

        start = time.perf_counter()

        response = self._openai.chat.completions.create(
            model=model_config.model,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
        )

        latency_ms = (time.perf_counter() - start) * 1000

        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        cost = self._estimate_cost(
            model=model_config.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        content = response.choices[0].message.content or ""

        return ModelResponse(
            content=content,
            provider=ModelProvider.OPENAI,
            model=model_config.model,
            prompt_version=prompt_version,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            estimated_cost_usd=cost,
        )

    # --------------------------------------------------------

    def _complete_anthropic(
        self,
        *,
        system_prompt: str,
        user_content: str,
        model_config: ModelConfig,
        prompt_version: str,
    ) -> ModelResponse:

        start = time.perf_counter()

        response = self._anthropic.messages.create(
            model=model_config.model,
            system=system_prompt,
            max_tokens=model_config.max_tokens,
            temperature=model_config.temperature,
            messages=[
                {
                    "role": "user",
                    "content": user_content,
                }
            ],
        )

        latency_ms = (time.perf_counter() - start) * 1000

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        cost = self._estimate_cost(
            model=model_config.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        # Extract textual content cleanly
        content = ""
        if response.content and len(response.content) > 0:
            first_block = response.content[0]
            if hasattr(first_block, "text"):
                content = first_block.text

        return ModelResponse(
            content=content,
            provider=ModelProvider.ANTHROPIC,
            model=model_config.model,
            prompt_version=prompt_version,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            estimated_cost_usd=cost,
        )

    # --------------------------------------------------------

    def _estimate_cost(
        self,
        *,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:

        pricing = _MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return round(input_cost + output_cost, 6)