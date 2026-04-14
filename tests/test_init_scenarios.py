"""Scenario-matrix tests for sentinel init.

Covers every combination of installed provider CLIs to make sure the
setup wizard produces sane configs on any user's machine.

All tests use fake CLI stubs (via the `fake_cli_env` fixture in
conftest.py) and an isolated temp project directory. No real LLM
calls are made.
"""

from __future__ import annotations

import tomllib
from pathlib import Path  # noqa: TC003 — runtime use in _read_config

from click.testing import CliRunner

from sentinel.cli.main import main


def _read_config(project_dir: Path) -> dict:
    """Load the config sentinel init just wrote."""
    return tomllib.loads((project_dir / ".sentinel" / "config.toml").read_text())


# ---------- No CLIs available ----------

class TestNoProviders:
    """User has no LLM provider CLI installed."""

    def test_init_bails_with_actionable_message(
        self, fake_cli_env, isolated_home,
    ):
        fake_cli_env()  # empty — no stubs
        runner = CliRunner()
        result = runner.invoke(main, ["init", "--yes"])
        assert result.exit_code == 0  # exits cleanly, just prints hints
        assert "No providers available" in result.output
        assert "brew install" in result.output or "install" in result.output.lower()
        # No config should have been written
        assert not (isolated_home / ".sentinel" / "config.toml").exists()


# ---------- Single CLI available ----------

class TestSingleProvider:
    """Only one provider CLI installed — config must still be usable."""

    def test_only_claude(self, fake_cli_env, isolated_home):
        fake_cli_env(claude=True)
        CliRunner().invoke(main, ["init", "--yes"])
        config = _read_config(isolated_home)
        # Every role must be assigned — no empty config
        for role in ("monitor", "researcher", "planner", "coder", "reviewer"):
            assert config["roles"][role]["provider"] == "claude", (
                f"{role} should fall back to claude when it's the only provider"
            )

    def test_only_gemini(self, fake_cli_env, isolated_home):
        fake_cli_env(gemini=True)
        CliRunner().invoke(main, ["init", "--yes"])
        config = _read_config(isolated_home)
        for role in ("monitor", "researcher", "planner", "coder", "reviewer"):
            assert config["roles"][role]["provider"] == "gemini"

    def test_only_codex(self, fake_cli_env, isolated_home):
        fake_cli_env(codex=True)
        CliRunner().invoke(main, ["init", "--yes"])
        config = _read_config(isolated_home)
        for role in ("monitor", "researcher", "planner", "coder", "reviewer"):
            assert config["roles"][role]["provider"] == "openai"


# ---------- Combinations ----------

class TestCombinations:
    """Multiple providers — defaults should pick smart per-role."""

    def test_claude_plus_gemini(self, fake_cli_env, isolated_home):
        """The common case — Claude Code + Gemini CLI, no Ollama, no Codex."""
        fake_cli_env(claude=True, gemini=True)
        CliRunner().invoke(main, ["init", "--yes"])
        config = _read_config(isolated_home)

        # Monitor should prefer Gemini Flash (cheap/fast)
        assert config["roles"]["monitor"]["provider"] == "gemini"
        assert "flash" in config["roles"]["monitor"]["model"].lower()

        # Planner/coder should default to claude (best for judgment + agentic)
        assert config["roles"]["planner"]["provider"] == "claude"
        assert config["roles"]["coder"]["provider"] == "claude"

        # Reviewer must not equal coder provider (independence)
        assert (
            config["roles"]["reviewer"]["provider"]
            != config["roles"]["coder"]["provider"]
        )

    def test_all_four_providers(self, fake_cli_env, isolated_home):
        fake_cli_env(claude=True, codex=True, gemini=True, ollama=True)
        CliRunner().invoke(main, ["init", "--yes"])
        config = _read_config(isolated_home)

        # Monitor prefers local when available
        assert config["roles"]["monitor"]["provider"] == "local"

        # Reviewer ≠ coder (independence check)
        assert (
            config["roles"]["reviewer"]["provider"]
            != config["roles"]["coder"]["provider"]
        )


# ---------- Preserves invariants ----------

class TestInvariants:
    """Things that must be true of any generated config."""

    def test_all_roles_assigned(self, fake_cli_env, isolated_home):
        fake_cli_env(claude=True, gemini=True)
        CliRunner().invoke(main, ["init", "--yes"])
        config = _read_config(isolated_home)

        required_roles = {"monitor", "researcher", "planner", "coder", "reviewer"}
        assert set(config["roles"].keys()) == required_roles

        for role, role_config in config["roles"].items():
            assert role_config.get("provider"), f"{role} missing provider"
            assert role_config.get("model"), f"{role} missing model"

    def test_budget_has_sensible_defaults(self, fake_cli_env, isolated_home):
        fake_cli_env(claude=True)
        CliRunner().invoke(main, ["init", "--yes"])
        config = _read_config(isolated_home)

        assert config["budget"]["daily_limit_usd"] > 0
        assert config["budget"]["warn_at_usd"] > 0
        assert config["budget"]["warn_at_usd"] <= config["budget"]["daily_limit_usd"]

    def test_project_type_detected(self, fake_cli_env, isolated_home):
        fake_cli_env(claude=True)
        # Pretend this temp dir is a Python project
        (isolated_home / "pyproject.toml").write_text(
            '[project]\nname = "fake"\n',
        )
        CliRunner().invoke(main, ["init", "--yes"])
        config = _read_config(isolated_home)
        assert config["project"]["type"] == "python"

    def test_non_interactive_mode_auto_proceeds(self, fake_cli_env, isolated_home):
        """Running in a pipe (no TTY) must not hang on confirmation."""
        fake_cli_env(claude=True)
        runner = CliRunner()
        result = runner.invoke(main, ["init"])  # no --yes
        # CliRunner simulates non-TTY stdin → init should auto-proceed
        assert result.exit_code == 0
        assert (isolated_home / ".sentinel" / "config.toml").exists()


# ---------- Re-running init ----------

class TestReinit:
    """Running init twice should not clobber existing state."""

    def test_skips_existing_config(self, fake_cli_env, isolated_home):
        fake_cli_env(claude=True)
        CliRunner().invoke(main, ["init", "--yes"])

        # Manually edit the config to verify we don't overwrite
        config_path = isolated_home / ".sentinel" / "config.toml"
        edited = config_path.read_text().replace(
            'provider = "claude"', 'provider = "claude"  # user-edited',
        )
        config_path.write_text(edited)

        # Re-run
        CliRunner().invoke(main, ["init", "--yes"])
        # Marker should still be there
        assert "# user-edited" in config_path.read_text()

    def test_skips_existing_goals(self, fake_cli_env, isolated_home):
        fake_cli_env(claude=True)
        CliRunner().invoke(main, ["init", "--yes"])

        goals_path = isolated_home / ".sentinel" / "goals.md"
        goals_path.write_text("# my custom goals\n")

        CliRunner().invoke(main, ["init", "--yes"])
        assert goals_path.read_text() == "# my custom goals\n"
