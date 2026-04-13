"""
Claude provider — Anthropic API + Claude Agent SDK

Supports all roles. The Agent SDK mode wraps Claude Code as a subprocess,
giving full agentic coding capability (file editing, terminal, test running).

Models: claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5
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

CLAUDE_MODELS = [
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
]


class ClaudeProvider(Provider):
    name = ProviderName.CLAUDE
    available_models = CLAUDE_MODELS
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
        # TODO: Implement via anthropic SDK
        raise NotImplementedError

    async def research(
        self, messages: list[Message], options: ResearchOptions | None = None
    ) -> ChatResponse:
        # TODO: Implement via Anthropic SDK with web_search tool
        raise NotImplementedError

    async def code(self, prompt: str, options: CodeOptions | None = None) -> ChatResponse:
        # TODO: Implement via claude-agent-sdk (Claude Code as subprocess)
        raise NotImplementedError

    async def health_check(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
