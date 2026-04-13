"""Tests for the provider router."""

import pytest

from sentinel.config.schema import RoleName, SentinelConfig
from sentinel.providers.claude import ClaudeProvider
from sentinel.providers.gemini import GeminiProvider
from sentinel.providers.local import LocalProvider
from sentinel.providers.router import Router


@pytest.fixture
def config() -> SentinelConfig:
    return SentinelConfig(
        project={"name": "test", "path": "/tmp/test"},
        roles={
            "monitor": {"provider": "local", "model": "qwen2.5-coder:14b"},
            "researcher": {"provider": "gemini", "model": "gemini-2.5-pro"},
            "planner": {"provider": "claude", "model": "claude-opus-4-6"},
            "coder": {"provider": "claude", "model": "claude-sonnet-4-6"},
            "reviewer": {"provider": "gemini", "model": "gemini-2.5-pro"},
        },
    )


class TestRouter:
    def test_maps_roles_to_providers(self, config: SentinelConfig) -> None:
        router = Router(config)
        assert isinstance(router.get_provider(RoleName.MONITOR), LocalProvider)
        assert isinstance(router.get_provider(RoleName.RESEARCHER), GeminiProvider)
        assert isinstance(router.get_provider(RoleName.PLANNER), ClaudeProvider)
        assert isinstance(router.get_provider(RoleName.CODER), ClaudeProvider)
        assert isinstance(router.get_provider(RoleName.REVIEWER), GeminiProvider)

    def test_reuses_provider_instances(self, config: SentinelConfig) -> None:
        """Planner and coder both use claude — should be the same instance."""
        router = Router(config)
        planner_provider = router.get_provider(RoleName.PLANNER)
        coder_provider = router.get_provider(RoleName.CODER)
        assert planner_provider is coder_provider

    def test_invalid_role_raises(self, config: SentinelConfig) -> None:
        router = Router(config)
        with pytest.raises(ValueError, match="No provider configured"):
            router.get_provider("nonexistent")  # type: ignore[arg-type]
