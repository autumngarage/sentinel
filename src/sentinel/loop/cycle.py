"""Core loop cycle implementation."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sentinel.roles.coder import Coder, ExecutionResult
from sentinel.roles.monitor import Monitor, StateAssessment
from sentinel.roles.planner import Plan, Planner
from sentinel.roles.researcher import ResearchBrief, Researcher
from sentinel.roles.reviewer import Reviewer, ReviewResult

if TYPE_CHECKING:
    from sentinel.config.schema import Goals, SentinelConfig
    from sentinel.providers.router import Router


@dataclass
class CycleResult:
    timestamp: str = ""
    assessment: StateAssessment = field(default_factory=StateAssessment)
    research_briefs: list[ResearchBrief] = field(default_factory=list)
    plan: Plan | None = None
    executions: list[ExecutionResult] = field(default_factory=list)
    reviews: list[ReviewResult] = field(default_factory=list)
    total_cost_usd: float = 0.0
    duration_ms: int = 0


class Loop:
    def __init__(self, config: SentinelConfig, router: Router) -> None:
        self.config = config
        self.router = router
        self.monitor = Monitor(router)
        self.researcher = Researcher(router)
        self.planner = Planner(router)
        self.coder = Coder(router)
        self.reviewer = Reviewer(router)

    async def cycle(self) -> CycleResult:
        """Run one full cycle of the loop."""
        start = time.time()
        goals = self.config.goals
        if not goals:
            raise ValueError("No goals configured. Run `sentinel goals` to set project goals.")

        # Step 1: KNOW GOALS — already in config
        # Step 2: ASSESS STATE
        assessment = await self.monitor.assess(self.config.project.path)

        # Step 3: RESEARCH
        research_briefs = await self._research_phase(goals, assessment)

        # Step 4: PLAN
        plan = await self.planner.plan(goals, assessment, research_briefs)

        # Step 5: DELEGATE
        executions, reviews = await self._execute_phase(plan)

        return CycleResult(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            assessment=assessment,
            research_briefs=research_briefs,
            plan=plan,
            executions=executions,
            reviews=reviews,
            total_cost_usd=sum(e.usage.cost_usd for e in executions),
            duration_ms=int((time.time() - start) * 1000),
        )

    async def _research_phase(
        self, goals: Goals, assessment: StateAssessment
    ) -> list[ResearchBrief]:
        # TODO: Determine what needs researching based on goals + state
        return []

    async def _execute_phase(
        self, plan: Plan
    ) -> tuple[list[ExecutionResult], list[ReviewResult]]:
        executions: list[ExecutionResult] = []
        reviews: list[ReviewResult] = []

        # Execute top priority items (respecting budget)
        for item in plan.backlog[:3]:  # limit per cycle
            result = await self.coder.execute(item, self.config.project.path)
            executions.append(result)

            if result.status == "success":
                review = await self.reviewer.review(item, result, self.config.project.path)
                reviews.append(review)

        return executions, reviews
