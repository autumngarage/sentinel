"""
Local provider — Ollama via OpenAI-compatible API

Uses the OpenAI SDK pointed at localhost. Zero cost, full privacy,
works offline. Best for the Monitor role and simple coding tasks.

Models: whatever the user has pulled in Ollama
"""

from __future__ import annotations

from sentinel.providers.interface import (
    ChatOptions,
    ChatResponse,
    Message,
    Provider,
    ProviderCapabilities,
    ProviderName,
)


class LocalProvider(Provider):
    name = ProviderName.LOCAL
    capabilities = ProviderCapabilities(
        chat=True,
        web_search=False,
        agentic_code=False,
        tool_use=True,  # partial — works with Qwen, Llama 3.1+
        long_context=False,  # typically 32K-128K, not 1M
        thinking=False,
        streaming=True,
        batch=False,
    )

    def __init__(self, endpoint: str = "http://localhost:11434/v1") -> None:
        self.endpoint = endpoint
        self.available_models: list[str] = []

    async def chat(
        self, messages: list[Message], options: ChatOptions | None = None
    ) -> ChatResponse:
        # TODO: Implement via openai SDK with base_url pointed at Ollama
        # from openai import AsyncOpenAI
        # client = AsyncOpenAI(base_url=self.endpoint, api_key="ollama")
        raise NotImplementedError

    async def health_check(self) -> bool:
        # TODO: Check if Ollama is running and responsive
        # try: httpx.get(f"{self.endpoint.replace('/v1', '')}/api/tags")
        return False

    async def discover_models(self) -> list[str]:
        """Discover which models the user has pulled in Ollama."""
        # TODO: GET http://localhost:11434/api/tags
        return []
