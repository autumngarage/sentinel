"""
Memory — persistent project knowledge across Sentinel sessions.

Sentinel needs to remember what it learned about a project across
sessions. This is NOT the same as chat history — it's structured
knowledge about the project that evolves over time.

What gets persisted:
- State assessments (health snapshots over time)
- Research briefs (what we learned and when)
- Plan history (what we planned and what happened)
- Execution results (what worked, what failed, why)
- Lessons learned (patterns that emerged from past cycles)

Storage: .sentinel/memory/ directory in the project
Format: Markdown files with YAML frontmatter (human-readable, git-trackable)
"""

from sentinel.memory.store import Memory, MemoryEntry

__all__ = ["Memory", "MemoryEntry"]
