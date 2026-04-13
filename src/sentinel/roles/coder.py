"""
Coder role — executes work items by writing code.

The coder receives a well-scoped work item from the planner and
executes it. Depending on the provider, this may use:
- Claude Agent SDK (full Claude Code agentic loop)
- Codex SDK (OpenAI's agentic coding)
- Direct API (generate code, apply with simple file writes)
- Local model (generate code, apply with simple file writes)

Default provider: Claude Agent SDK (full agentic loop)
Recommended model: claude-sonnet-4-6
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentinel.providers.router import Router
    from sentinel.roles.planner import WorkItem


@dataclass
class ExecutionUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0


@dataclass
class ExecutionResult:
    work_item_id: str
    status: str  # "success", "partial", "failed"
    files_changed: list[str] = field(default_factory=list)
    tests_run: bool = False
    tests_passing: bool = False
    commit_sha: str | None = None
    error: str | None = None
    usage: ExecutionUsage = field(default_factory=ExecutionUsage)


class Coder:
    def __init__(self, router: Router) -> None:
        self.router = router

    async def execute(self, work_item: WorkItem, project_path: str) -> ExecutionResult:
        """Execute a work item."""
        # TODO: Implement code execution
        # 1. Build a detailed prompt from the work item
        #    - Include description, acceptance criteria, relevant files
        #    - Include any attached research brief
        # 2. Dispatch to the coder provider
        #    - If agent-sdk: use Claude Code subprocess
        #    - If codex: use Codex SDK
        #    - If api/local: generate code and apply file changes
        # 3. Run tests to verify
        # 4. Collect results
        raise NotImplementedError
