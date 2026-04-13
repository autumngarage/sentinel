"""Tests for configuration schema."""

import pytest
from pydantic import ValidationError

from sentinel.config.schema import (
    ROLE_DEFAULTS,
    ROLE_DESCRIPTIONS,
    ProviderName,
    RoleConfig,
    RoleName,
    SentinelConfig,
)


class TestRoleNames:
    def test_all_five_roles_exist(self) -> None:
        assert len(RoleName) == 5
        assert RoleName.MONITOR.value == "monitor"
        assert RoleName.RESEARCHER.value == "researcher"
        assert RoleName.PLANNER.value == "planner"
        assert RoleName.CODER.value == "coder"
        assert RoleName.REVIEWER.value == "reviewer"


class TestProviderNames:
    def test_all_four_providers_exist(self) -> None:
        assert len(ProviderName) == 4
        assert ProviderName.CLAUDE.value == "claude"
        assert ProviderName.OPENAI.value == "openai"
        assert ProviderName.GEMINI.value == "gemini"
        assert ProviderName.LOCAL.value == "local"


class TestRoleDefaults:
    def test_defaults_for_all_roles(self) -> None:
        assert len(ROLE_DEFAULTS) == 5
        assert ROLE_DEFAULTS[RoleName.MONITOR].provider == ProviderName.LOCAL
        assert ROLE_DEFAULTS[RoleName.RESEARCHER].provider == ProviderName.GEMINI
        assert ROLE_DEFAULTS[RoleName.PLANNER].provider == ProviderName.CLAUDE
        assert ROLE_DEFAULTS[RoleName.CODER].provider == ProviderName.CLAUDE
        assert ROLE_DEFAULTS[RoleName.REVIEWER].provider == ProviderName.GEMINI

    def test_reviewer_differs_from_coder(self) -> None:
        """Reviewer should default to a different provider than coder."""
        assert (
            ROLE_DEFAULTS[RoleName.REVIEWER].provider
            != ROLE_DEFAULTS[RoleName.CODER].provider
        )


class TestRoleDescriptions:
    def test_descriptions_for_all_roles(self) -> None:
        assert len(ROLE_DESCRIPTIONS) == 5
        for role in RoleName:
            assert role in ROLE_DESCRIPTIONS
            assert len(ROLE_DESCRIPTIONS[role]) > 0


class TestSentinelConfig:
    def test_valid_config(self) -> None:
        config = SentinelConfig(
            project={"name": "test-project", "path": "/tmp/test"},
            goals={
                "description": "Build something great",
                "milestones": ["MVP"],
                "priorities": ["Quality"],
            },
            roles={
                "monitor": {"provider": "local", "model": "qwen2.5-coder:14b"},
                "researcher": {"provider": "gemini", "model": "gemini-2.5-pro"},
                "planner": {"provider": "claude", "model": "claude-opus-4-6"},
                "coder": {"provider": "claude", "model": "claude-sonnet-4-6"},
                "reviewer": {"provider": "gemini", "model": "gemini-2.5-pro"},
            },
        )
        assert config.project.name == "test-project"
        assert config.budget.daily_limit_usd == 15.0  # default

    def test_invalid_provider_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SentinelConfig(
                project={"name": "test", "path": "/tmp"},
                roles={
                    "monitor": {"provider": "invalid", "model": "test"},
                    "researcher": {"provider": "gemini", "model": "test"},
                    "planner": {"provider": "claude", "model": "test"},
                    "coder": {"provider": "claude", "model": "test"},
                    "reviewer": {"provider": "gemini", "model": "test"},
                },
            )

    def test_budget_defaults(self) -> None:
        config = SentinelConfig(
            project={"name": "test", "path": "/tmp"},
            roles={
                "monitor": {"provider": "local", "model": "test"},
                "researcher": {"provider": "gemini", "model": "test"},
                "planner": {"provider": "claude", "model": "test"},
                "coder": {"provider": "claude", "model": "test"},
                "reviewer": {"provider": "gemini", "model": "test"},
            },
        )
        assert config.budget.daily_limit_usd == 15.0
        assert config.budget.warn_at_usd == 10.0
        assert config.budget.track_local_tokens is True


class TestRoleConfig:
    def test_minimal_role_config(self) -> None:
        role = RoleConfig(provider=ProviderName.CLAUDE, model="claude-opus-4-6")
        assert role.provider == ProviderName.CLAUDE
        assert role.schedule == "manual"  # default

    def test_full_role_config(self) -> None:
        role = RoleConfig(
            provider=ProviderName.LOCAL,
            model="qwen2.5-coder:32b",
            endpoint="http://localhost:11434/v1",
            mode="local",
            schedule="on-change",
        )
        assert role.endpoint == "http://localhost:11434/v1"
        assert role.mode == "local"
