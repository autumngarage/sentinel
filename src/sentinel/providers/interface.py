"""
Provider interface — the unified abstraction across all LLM providers.

Every provider (Claude, OpenAI, Gemini, Local/Ollama) implements this
interface. The router selects a provider based on role configuration.

Design decisions:
- chat() is the universal primitive — all providers support it
- research() adds web search capability (not all providers support it)
- code() adds agentic code execution (only Claude Agent SDK and Codex SDK)
- Providers declare their capabilities so the router can make informed choices
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal


class ProviderName(StrEnum):
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    LOCAL = "local"


@dataclass
class Message:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict


@dataclass
class ToolCall:
    name: str
    arguments: dict


@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cost_usd: float = 0.0


@dataclass
class ChatResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: TokenUsage = field(default_factory=TokenUsage)
    model: str = ""
    provider: ProviderName = ProviderName.CLAUDE


@dataclass
class ChatOptions:
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    tools: list[ToolDefinition] | None = None
    system_prompt: str | None = None
    thinking: bool = False


@dataclass
class ResearchOptions(ChatOptions):
    web_search: bool = True
    max_sources: int = 10


@dataclass
class CodeOptions:
    working_directory: str = "."
    allowed_tools: list[str] | None = None
    max_budget_usd: float | None = None
    max_turns: int | None = None


@dataclass
class ProviderCapabilities:
    chat: bool = True
    web_search: bool = False
    agentic_code: bool = False
    tool_use: bool = False
    long_context: bool = False  # 200k+ tokens
    thinking: bool = False  # extended reasoning
    streaming: bool = False
    batch: bool = False


class Provider(ABC):
    """Base class for all LLM providers."""

    name: ProviderName
    capabilities: ProviderCapabilities
    available_models: list[str]

    @abstractmethod
    async def chat(
        self, messages: list[Message], options: ChatOptions | None = None
    ) -> ChatResponse:
        """Basic chat completion — all providers support this."""

    async def research(
        self, messages: list[Message], options: ResearchOptions | None = None
    ) -> ChatResponse:
        """Chat with web search grounding — not all providers support this."""
        # Default: fall back to regular chat
        return await self.chat(messages, options)

    async def code(self, prompt: str, options: CodeOptions | None = None) -> ChatResponse:
        """Agentic code execution — only Claude Agent SDK and Codex SDK."""
        raise NotImplementedError(
            f"Provider {self.name} does not support agentic code execution. "
            "Consider using claude or openai for the coder role."
        )

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is configured and reachable."""
