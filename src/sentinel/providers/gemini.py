"""
Gemini provider — Google GenAI SDK

Particularly strong for research (native Google Search grounding)
and cost-effective scanning (Flash models at $0.30/MTok).

Models: gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite
"""

from __future__ import annotations

import os

from sentinel.providers.interface import (
    ChatOptions,
    ChatResponse,
    Message,
    Provider,
    ProviderCapabilities,
    ProviderName,
    ResearchOptions,
)

GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


class GeminiProvider(Provider):
    name = ProviderName.GEMINI
    available_models = GEMINI_MODELS
    capabilities = ProviderCapabilities(
        chat=True,
        web_search=True,
        agentic_code=False,
        tool_use=True,
        long_context=True,
        thinking=True,
        streaming=True,
        batch=True,
    )

    async def chat(
        self, messages: list[Message], options: ChatOptions | None = None
    ) -> ChatResponse:
        # TODO: Implement via google-genai SDK
        raise NotImplementedError

    async def research(
        self, messages: list[Message], options: ResearchOptions | None = None
    ) -> ChatResponse:
        # TODO: Implement with Google Search grounding (native to API)
        # This is Gemini's killer feature — web search is built into the
        # API call, not a separate tool. The model can search and cite inline.
        raise NotImplementedError

    async def health_check(self) -> bool:
        return bool(os.environ.get("GEMINI_API_KEY"))
