"""
Roles — the five agents that power Sentinel's loop.

Each role represents a distinct function in the project management loop:

  1. Monitor    — ASSESS current state
  2. Researcher — RESEARCH expertise to guide next steps
  3. Planner    — PLAN prioritized work items
  4. Coder      — DELEGATE and execute tasks
  5. Reviewer   — VERIFY completed work

Goals (step 0) are stored in config, not a role — they're the user's
intent, not an LLM's output.
"""

from sentinel.roles.coder import Coder
from sentinel.roles.monitor import Monitor
from sentinel.roles.planner import Planner
from sentinel.roles.researcher import Researcher
from sentinel.roles.reviewer import Reviewer

__all__ = ["Coder", "Monitor", "Planner", "Researcher", "Reviewer"]
