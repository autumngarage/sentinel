"""
Monitor role — continuously scans the codebase and assesses current state.

This is the "eyes" of Sentinel. It runs frequently (on-change, hourly,
or on-demand) and produces a state assessment that feeds the rest of the loop.

What it scans:
- Git status: uncommitted changes, branch state, recent commits
- Code quality: complexity hotspots, duplication, dead code
- Test coverage: gaps, failing tests, missing edge cases
- Dependency health: outdated deps, known CVEs, license issues
- Architectural drift: deviations from stated patterns in CLAUDE.md
- Open issues: GitHub issues, TODOs in code

Default provider: Local (free, runs continuously)
Recommended model: qwen2.5-coder:14b
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from sentinel.providers.router import Router


@dataclass
class GitStatus:
    branch: str = ""
    uncommitted_changes: int = 0
    recent_commits: list[str] = field(default_factory=list)
    ahead_of_remote: int = 0


@dataclass
class CodeHealth:
    issues: list[StateIssue] = field(default_factory=list)
    score: int = 0  # 0-100


@dataclass
class TestHealth:
    passing: int = 0
    failing: int = 0
    coverage: float | None = None


@dataclass
class DependencyHealth:
    outdated: list[str] = field(default_factory=list)
    vulnerabilities: list[str] = field(default_factory=list)


@dataclass
class StateIssue:
    type: Literal["quality", "test", "dependency", "architecture", "todo"]
    severity: Literal["low", "medium", "high", "critical"]
    file: str | None = None
    line: int | None = None
    description: str = ""


@dataclass
class StateAssessment:
    timestamp: str = ""
    git: GitStatus = field(default_factory=GitStatus)
    code_health: CodeHealth = field(default_factory=CodeHealth)
    test_health: TestHealth = field(default_factory=TestHealth)
    dependency_health: DependencyHealth = field(default_factory=DependencyHealth)
    changed_since_last_scan: list[str] = field(default_factory=list)


class Monitor:
    def __init__(self, router: Router) -> None:
        self.router = router

    async def assess(self, project_path: str) -> StateAssessment:
        """Run a full state assessment of the project."""
        # TODO: Implement state assessment
        # 1. Run git commands to get repo state
        # 2. Ask the monitor LLM to analyze code quality
        # 3. Run tests and collect results
        # 4. Check dependencies
        # 5. Compare against previous scan
        raise NotImplementedError
