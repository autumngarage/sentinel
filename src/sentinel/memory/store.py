"""Memory storage implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class MemoryEntry:
    id: str
    type: Literal["assessment", "research", "plan", "execution", "lesson"]
    timestamp: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)


class Memory:
    def __init__(self, project_path: str) -> None:
        self.memory_dir = Path(project_path) / ".sentinel" / "memory"

    async def save(self, entry: MemoryEntry) -> None:
        """Write entry as markdown file with frontmatter."""
        raise NotImplementedError

    async def load(self, entry_id: str) -> MemoryEntry | None:
        """Read and parse a memory entry."""
        raise NotImplementedError

    async def search(
        self, query: str, entry_type: str | None = None
    ) -> list[MemoryEntry]:
        """Search memory entries by content and type."""
        raise NotImplementedError

    async def recent(self, count: int, entry_type: str | None = None) -> list[MemoryEntry]:
        """Get most recent entries."""
        raise NotImplementedError
