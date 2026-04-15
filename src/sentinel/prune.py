"""Age-based prune for `.sentinel/runs/` per-cycle journals.

`sentinel work --every 10m` runs ~144 cycles/day. Without explicit
retention, a year of operation accumulates ~50k journal files in
`.sentinel/runs/`. That breaks the "design for scale-up" principle.

Mechanism:
- One target directory: `.sentinel/runs/`
- One rule: anything older than `retention.runs_days` is deleted
- Runs at the start of every `sentinel work` cycle (cheap when nothing's
  expired — just an mtime walk over a small directory)

Long-lived artifacts (`scans/`, `verifications.jsonl`, `backlog.md`,
`proposals/`) live OUTSIDE `runs/` and are never touched. The single-
directory scope is deliberate: no per-artifact retention tiers, no size
caps, no special-casing. Add complexity only when the simple rule
demonstrably fails in practice.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path  # noqa: TC003 — Path used at runtime for stat/iterdir

logger = logging.getLogger(__name__)

RUNS_DIRNAME = "runs"


def prune_runs(project_path: Path, retention_days: int) -> int:
    """Delete `.sentinel/runs/` entries older than retention_days.

    Returns the number of items removed. Returns 0 when the runs dir
    doesn't exist yet (true on every project before the run-journal
    mechanism ships, or before the first cycle on a fresh project).

    retention_days <= 0 disables pruning — the function returns 0
    without walking the directory. Use this to opt out entirely.
    """
    if retention_days <= 0:
        return 0

    runs_dir = project_path / ".sentinel" / RUNS_DIRNAME
    if not runs_dir.exists():
        return 0

    cutoff = time.time() - (retention_days * 86400)
    removed = 0

    # Top-level entries only — each cycle writes a single journal file
    # (or a directory in future variants). We don't recurse arbitrarily;
    # if someone organizes runs/ into nested dirs later, this still
    # handles them as opaque entries with their own mtimes.
    for entry in runs_dir.iterdir():
        try:
            mtime = entry.stat().st_mtime
        except OSError as e:
            # File disappeared between iterdir and stat (concurrent prune,
            # external deletion). Skip it — next cycle will find it gone.
            logger.debug("prune: stat failed for %s: %s", entry, e)
            continue

        if mtime >= cutoff:
            continue

        try:
            if entry.is_dir():
                # Recursive rmdir for entry-as-directory layouts
                _rmtree(entry)
            else:
                entry.unlink()
            removed += 1
        except OSError as e:
            # Couldn't delete — log and move on. A failing prune
            # shouldn't break the cycle.
            logger.warning("prune: failed to remove %s: %s", entry, e)

    return removed


def _rmtree(path: Path) -> None:
    """Recursive directory removal. Stdlib shutil.rmtree exists but
    we keep this local + minimal to avoid an extra import path and so
    OSError handling stays in one place."""
    for child in path.iterdir():
        if child.is_dir():
            _rmtree(child)
        else:
            child.unlink()
    path.rmdir()
