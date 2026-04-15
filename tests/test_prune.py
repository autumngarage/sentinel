"""Tests for the runs/ prune mechanism.

The cycle journal isn't shipped yet (PR B), so prune currently runs
against an empty / nonexistent runs/ dir on every real cycle. These
tests cover the contract regardless: no-op when there's nothing to
prune, removes only items older than retention, never touches anything
outside .sentinel/runs/, fails gracefully on filesystem errors.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from sentinel.prune import prune_runs


def _touch(path: Path, age_days: float) -> None:
    """Create a file (or dir) with mtime set N days in the past."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == "" and not path.exists():
        path.mkdir(parents=True)
    else:
        path.write_text("x")
    past = time.time() - age_days * 86400
    os.utime(path, (past, past))


class TestPruneRuns:
    def test_returns_zero_when_no_dot_sentinel(self, tmp_path: Path) -> None:
        assert prune_runs(tmp_path, retention_days=30) == 0

    def test_returns_zero_when_no_runs_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".sentinel").mkdir()
        assert prune_runs(tmp_path, retention_days=30) == 0

    def test_returns_zero_when_disabled(self, tmp_path: Path) -> None:
        """retention_days <= 0 disables pruning entirely."""
        runs = tmp_path / ".sentinel" / "runs"
        _touch(runs / "old.md", age_days=999)
        assert prune_runs(tmp_path, retention_days=0) == 0
        assert (runs / "old.md").exists(), "disabled prune must not touch files"

    def test_removes_older_than_retention(self, tmp_path: Path) -> None:
        runs = tmp_path / ".sentinel" / "runs"
        _touch(runs / "old.md", age_days=45)
        _touch(runs / "older.md", age_days=100)
        _touch(runs / "fresh.md", age_days=5)

        removed = prune_runs(tmp_path, retention_days=30)

        assert removed == 2
        assert not (runs / "old.md").exists()
        assert not (runs / "older.md").exists()
        assert (runs / "fresh.md").exists(), (
            "fresh file (5 days old) must survive 30-day retention"
        )

    def test_does_not_touch_artifacts_outside_runs(self, tmp_path: Path) -> None:
        """Long-lived artifacts (scans/, verifications.jsonl, etc.) live
        outside runs/ specifically so prune can never touch them."""
        runs = tmp_path / ".sentinel" / "runs"
        _touch(runs / "old.md", age_days=999)
        _touch(tmp_path / ".sentinel" / "scans" / "old-scan.md", age_days=999)
        _touch(tmp_path / ".sentinel" / "verifications.jsonl", age_days=999)
        _touch(tmp_path / ".sentinel" / "backlog.md", age_days=999)

        prune_runs(tmp_path, retention_days=30)

        # runs/ entry gone, everything else preserved
        assert not (runs / "old.md").exists()
        assert (tmp_path / ".sentinel" / "scans" / "old-scan.md").exists()
        assert (tmp_path / ".sentinel" / "verifications.jsonl").exists()
        assert (tmp_path / ".sentinel" / "backlog.md").exists()

    def test_handles_directory_entries(self, tmp_path: Path) -> None:
        """Future variants of the journal may write a per-cycle dir
        instead of a file. Prune must handle both shapes."""
        runs = tmp_path / ".sentinel" / "runs"
        old_dir = runs / "2026-01-01-1200"
        old_dir.mkdir(parents=True)
        (old_dir / "events.jsonl").write_text("{}")
        (old_dir / "manifest.md").write_text("x")
        past = time.time() - 100 * 86400
        os.utime(old_dir / "events.jsonl", (past, past))
        os.utime(old_dir / "manifest.md", (past, past))
        os.utime(old_dir, (past, past))

        removed = prune_runs(tmp_path, retention_days=30)

        assert removed == 1
        assert not old_dir.exists()

    def test_no_removal_when_everything_fresh(self, tmp_path: Path) -> None:
        runs = tmp_path / ".sentinel" / "runs"
        _touch(runs / "a.md", age_days=1)
        _touch(runs / "b.md", age_days=10)
        _touch(runs / "c.md", age_days=29)

        assert prune_runs(tmp_path, retention_days=30) == 0
        assert (runs / "a.md").exists()
        assert (runs / "b.md").exists()
        assert (runs / "c.md").exists()

    def test_disappearing_entry_does_not_crash(self, tmp_path: Path) -> None:
        """A file that vanishes between iterdir and stat (concurrent
        prune from another process, external deletion) must not crash."""
        runs = tmp_path / ".sentinel" / "runs"
        _touch(runs / "ghost.md", age_days=999)

        # Race: delete the file before prune sees it
        original_iterdir = Path.iterdir

        def racy_iterdir(self):  # noqa: ANN001, ANN202
            for entry in original_iterdir(self):
                if entry.name == "ghost.md":
                    entry.unlink()  # vanish between iterdir and stat
                yield entry

        Path.iterdir = racy_iterdir
        try:
            # Should not raise, just skip the missing file
            removed = prune_runs(tmp_path, retention_days=30)
        finally:
            Path.iterdir = original_iterdir

        # We don't assert the count — what matters is that no exception
        # propagated. The ghost was already gone by the time stat ran.
        assert isinstance(removed, int)
