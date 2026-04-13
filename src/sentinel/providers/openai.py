"""
OpenAI provider — Responses API + Codex SDK

Supports all roles. The Codex SDK mode provides agentic code execution
similar to Claude Agent SDK.

Models: gpt-5.4, gpt-5.4-mini, gpt-5.3-codex, o4-mini
"""

from __future__ import annotations

import os

from sentinel.providers.interface import (
    ChatOptions,
    ChatResponse,
    CodeOptions,
    Message,
    Provider,
    ProviderCapabilities,
    ProviderName,
    ResearchOptions,
)

OPENAI_MODELS = [
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gpt-5.3-codex",
    "o4-mini",
    "o3",
]


class OpenAIProvider(Provider):
    name = ProviderName.OPENAI
    available_models = OPENAI_MODELS
    capabilities = ProviderCapabilities(
        chat=True,
        web_search=True,
        agentic_code=True,
        tool_use=True,
        long_context=True,
        thinking=True,
        streaming=True,
        batch=True,
    )

    async def chat(
        self, messages: list[Message], options: ChatOptions | None = None
    ) -> ChatResponse:
        # TODO: Implement via openai SDK (Responses API)
        raise NotImplementedError

    async def research(
        self, messages: list[Message], options: ResearchOptions | None = None
    ) -> ChatResponse:
        # TODO: Implement via Responses API with web_search built-in tool
        raise NotImplementedError

    async def code(self, prompt: str, options: CodeOptions | None = None) -> ChatResponse:
        # TODO: Implement via Codex SDK
        raise NotImplementedError

    async def health_check(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))
