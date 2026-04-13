"""
Reviewer role — verifies completed work against acceptance criteria.

The reviewer checks the coder's output independently. By default, it
uses a DIFFERENT provider than the coder — this prevents the same
model from reviewing its own work (same blind spots).

Default provider: Gemini (independent from Claude coder)
Recommended model: gemini-2.5-pro
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from sentinel.providers.router import Router
    from sentinel.roles.coder import ExecutionResult
    from sentinel.roles.planner import WorkItem


@dataclass
class ReviewIssue:
    file: str
    line: int | None = None
    severity: Literal["blocking", "warning"] = "warning"
    description: str = ""
    suggested_fix: str | None = None


@dataclass
class ReviewResult:
    work_item_id: str
    verdict: Literal["approved", "changes-requested", "rejected"]
    blocking_issues: list[ReviewIssue] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    acceptance_criteria_met: dict[str, bool] = field(default_factory=dict)


class Reviewer:
    def __init__(self, router: Router) -> None:
        self.router = router

    async def review(
        self,
        work_item: WorkItem,
        execution_result: ExecutionResult,
        project_path: str,
    ) -> ReviewResult:
        """Review completed work against acceptance criteria."""
        # TODO: Implement review
        # 1. Read the diff of changed files
        # 2. Check each acceptance criterion
        # 3. Look for common issues (security, silent failures, missing tests)
        # 4. Produce structured review result
        raise NotImplementedError
