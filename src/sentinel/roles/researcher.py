"""
Researcher role — deep research to guide the next step.

This is the "brain" that ensures Sentinel makes informed decisions.
Before any non-trivial work, the researcher investigates best practices,
reads documentation, and evaluates alternatives.

Research modes:
- Targeted: "Before implementing X, research how to do it well"
- Exploratory: "What should we be thinking about that we're not?"
- Comparative: "How does our approach compare to alternatives?"
- Consensus: Ask multiple models independently, synthesize disagreements

Inspired by Karpathy's autoresearch:
- Fixed budget per research iteration (makes results comparable)
- Structured results logging (data, not prose)
- Crash recovery (handle failures, log, move on)
- Simplicity-weighted decisions

Default provider: Gemini (built-in Google Search grounding, 1M context)
Recommended model: gemini-2.5-pro
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from sentinel.providers.router import Router
    from sentinel.roles.monitor import StateAssessment


@dataclass
class ResearchFinding:
    source: str
    summary: str
    relevance: Literal["low", "medium", "high"]
    model: str | None = None  # which model produced this (for consensus mode)


@dataclass
class ResearchBrief:
    question: str
    mode: Literal["targeted", "exploratory", "comparative", "consensus"]
    findings: list[ResearchFinding] = field(default_factory=list)
    synthesis: str = ""
    confidence: Literal["low", "medium", "high"] = "medium"
    sources: list[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class ConsensusResult:
    agreements: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    synthesis: str = ""
    model_responses: dict[str, str] = field(default_factory=dict)


class Researcher:
    def __init__(self, router: Router) -> None:
        self.router = router

    async def targeted(self, question: str, context: str | None = None) -> ResearchBrief:
        """Targeted research — investigate a specific topic before acting."""
        # TODO: Implement targeted research
        # 1. Formulate search queries from the question
        # 2. Use researcher provider's web search capability
        # 3. Synthesize findings into actionable brief
        raise NotImplementedError

    async def exploratory(self, assessment: StateAssessment) -> ResearchBrief:
        """Exploratory research — discover what we should be thinking about."""
        # TODO: Implement exploratory research
        # 1. Analyze current state for areas of improvement
        # 2. Search for ecosystem updates relevant to dependencies
        # 3. Check for new patterns/tools that could help
        raise NotImplementedError

    async def comparative(self, topic: str, alternatives: list[str]) -> ResearchBrief:
        """Comparative research — evaluate alternatives."""
        # TODO: Implement comparative research
        # 1. Research each alternative
        # 2. Compare against current approach
        # 3. Produce tradeoff analysis
        raise NotImplementedError

    async def consensus(self, question: str) -> ConsensusResult:
        """Multi-model consensus — ask multiple providers, synthesize."""
        # TODO: Implement multi-model consensus
        # 1. Send the same question to all available providers in parallel
        # 2. Collect independent responses
        # 3. Use the planner model to synthesize agreements/disagreements
        # 4. Rate confidence based on degree of agreement
        raise NotImplementedError
