"""
Sentinel — Autonomous Meta-Agent for Software Projects

Manages software projects through a continuous loop:
  1. Assess State  — Monitor scans the codebase through multiple lenses
  2. Research      — Researcher investigates best approaches
  3. Plan          — Planner creates prioritized work items
  4. Delegate      — Coder executes, Reviewer verifies

Each step is powered by a configurable LLM provider (CLI-based, no API keys stored):
  - Monitor    → default: Local/Ollama (free, runs often)
  - Researcher → default: Gemini CLI (web search, cheap)
  - Planner    → default: Claude CLI (best judgment)
  - Coder      → default: Claude Code (agentic coding)
  - Reviewer   → default: Gemini CLI (independent from coder)

Goals are derived from CLAUDE.md, README, and GitHub issues — not stored separately.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__ = _pkg_version("sentinel")
except PackageNotFoundError:
    # Running from an uninstalled source checkout (rare — direct `python
    # -m` against src/). Fall back to a sentinel so --version still works
    # rather than crashing on import.
    __version__ = "0.0.0+unknown"

# Silence the sentinel logger by default — errors are captured in
# ProjectState.errors / ScanResult.error and surfaced via the CLI.
# Users who want verbose output can configure logging themselves.
import logging as _logging

_logging.getLogger("sentinel").addHandler(_logging.NullHandler())
