"""
The Loop — Sentinel's core execution cycle.

Implements the five-step cycle that mirrors what a human technical PM does:

  1. KNOW GOALS    — Read project goals from config
  2. ASSESS STATE  — Monitor scans the codebase
  3. RESEARCH      — Researcher investigates best approaches
  4. PLAN          — Planner creates prioritized backlog
  5. DELEGATE      — Coder executes, Reviewer verifies

The loop can run in different cadences:
  - Single cycle: `sentinel cycle`
  - Continuous: `sentinel watch` (re-runs after each delegation)
  - Scheduled: via cron or Claude Code scheduled tasks
  - Triggered: on git push, PR merge, issue creation
  - Manual: `sentinel cycle` when you want it

The ultimate dogfooding goal: Sentinel manages its own development.
"""

from sentinel.loop.cycle import CycleResult, Loop

__all__ = ["CycleResult", "Loop"]
