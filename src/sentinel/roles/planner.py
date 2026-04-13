"""
Planner role — strategic decisions, task decomposition, prioritization.

The planner takes the state assessment and research briefs and produces
a prioritized backlog of well-scoped work items. Each item has clear
acceptance criteria so the coder knows when it's done and the reviewer
knows what to check.

Default provider: Claude Opus 4.6 (best judgment and reasoning)
Recommended model: claude-opus-4-6
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from sentinel.config.schema import Goals
    from sentinel.providers.router import Router
    from sentinel.roles.monitor import StateAssessment
    from sentinel.roles.researcher import ResearchBrief


@dataclass
class WorkItem:
    id: str
    title: str
    description: str
    type: Literal["feature", "bugfix", "refactor", "test", "docs", "chore"]
    priority: Literal["critical", "high", "medium", "low"]
    estimated_complexity: int  # 1=trivial, 5=major
    files: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    research_brief: ResearchBrief | None = None
    risk_assessment: str = ""
    blocked_by: list[str] = field(default_factory=list)


@dataclass
class Plan:
    timestamp: str
    goals: Goals
    assessment: StateAssessment
    backlog: list[WorkItem] = field(default_factory=list)
    rationale: str = ""  # why these items, in this order


class Planner:
    def __init__(self, router: Router) -> None:
        self.router = router

    async def plan(
        self,
        goals: Goals,
        assessment: StateAssessment,
        research: list[ResearchBrief],
    ) -> Plan:
        """Generate a plan from current state and research."""
        # TODO: Implement planning
        # 1. Analyze goals vs current state to identify gaps
        # 2. Use research briefs to inform approach
        # 3. Decompose gaps into atomic work items
        # 4. Prioritize by impact x effort x risk
        # 5. Add acceptance criteria to each item
        raise NotImplementedError

    async def reprioritize(self, plan: Plan, new_assessment: StateAssessment) -> Plan:
        """Re-prioritize an existing backlog based on new information."""
        raise NotImplementedError
