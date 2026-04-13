"""
Router — selects the right provider for each role.

The router reads the project's sentinel config to determine which
provider is assigned to each role, instantiates the providers,
and exposes role-based methods.

The key insight: the user configures roles, not models. The router
translates role assignments into provider calls.
"""

from __future__ import annotations

from sentinel.config.schema import RoleName, SentinelConfig
from sentinel.providers.claude import ClaudeProvider
from sentinel.providers.gemini import GeminiProvider
from sentinel.providers.interface import (
    ChatResponse,
    CodeOptions,
    Message,
    Provider,
)
from sentinel.providers.local import LocalProvider
from sentinel.providers.openai import OpenAIProvider

PROVIDER_CLASSES: dict[str, type[Provider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "local": LocalProvider,
}


class Router:
    def __init__(self, config: SentinelConfig) -> None:
        self._providers: dict[str, Provider] = {}
        self._role_map: dict[RoleName, Provider] = {}
        self._init_from_config(config)

    def _init_from_config(self, config: SentinelConfig) -> None:
        roles = {
            RoleName.MONITOR: config.roles.monitor,
            RoleName.RESEARCHER: config.roles.researcher,
            RoleName.PLANNER: config.roles.planner,
            RoleName.CODER: config.roles.coder,
            RoleName.REVIEWER: config.roles.reviewer,
        }
        for role_name, role_config in roles.items():
            provider_key = role_config.provider.value
            if provider_key not in self._providers:
                provider_cls = PROVIDER_CLASSES[provider_key]
                if provider_key == "local":
                    endpoint = role_config.endpoint or config.local.ollama_endpoint
                    self._providers[provider_key] = LocalProvider(endpoint=endpoint)
                else:
                    self._providers[provider_key] = provider_cls()
            self._role_map[role_name] = self._providers[provider_key]

    def get_provider(self, role: RoleName) -> Provider:
        """Get the provider assigned to a role."""
        provider = self._role_map.get(role)
        if not provider:
            raise ValueError(f"No provider configured for role: {role}")
        return provider

    async def chat(self, role: RoleName, messages: list[Message]) -> ChatResponse:
        """Chat using the provider assigned to a specific role."""
        provider = self.get_provider(role)
        return await provider.chat(messages)

    async def research(self, messages: list[Message]) -> ChatResponse:
        """Research using the researcher role's provider."""
        provider = self.get_provider(RoleName.RESEARCHER)
        return await provider.research(messages)

    async def code(self, prompt: str, working_directory: str) -> ChatResponse:
        """Execute code using the coder role's provider."""
        provider = self.get_provider(RoleName.CODER)
        return await provider.code(prompt, CodeOptions(working_directory=working_directory))

    async def health_check_all(self) -> dict[str, bool]:
        """Health check all configured providers."""
        results = {}
        for name, provider in self._providers.items():
            results[name] = await provider.health_check()
        return results
