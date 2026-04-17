"""Cycle summary bucket counts.

Dogfood on portfolio_new (2026-04-17) surfaced that after a cycle where
both work items were coded, reviewed, and rejected, the final banner
read `Items executed: 2 • Approved: 0 • Failed: 0` — the rejections
vanished from the totals because the counter only incremented on
"approved" or "failed". Reviewer rejections (`rejected`, `changes`)
slipped through both branches.

These tests pin the bucketing rule: every executed item lands in
exactly one of approved/rejected/failed, so the buckets always sum
to the executed count.
"""

from __future__ import annotations

import pytest

from sentinel.cli.work_cmd import _bucket_outcome


@pytest.mark.parametrize(
    ("success", "expected"),
    [
        ("approved", "approved"),
        ("changes", "rejected"),
        ("rejected", "rejected"),
        ("failed", "failed"),
        # Defensive: anything unexpected (None, empty, surprise token)
        # buckets to "failed" so it stays visible — silently dropping
        # the count is exactly the bug we're fixing.
        (None, "failed"),
        ("", "failed"),
        ("unexpected_new_status", "failed"),
    ],
)
def test_bucket_outcome_maps_known_tokens(success, expected):
    assert _bucket_outcome(success) == expected


def test_bucket_outcome_invariant_buckets_partition_executed():
    """For any sequence of cycle outcomes, approved + rejected + failed
    must equal executed. This is the invariant that was broken pre-fix."""
    outcomes = [
        "approved", "approved", "rejected", "changes",
        "failed", None, "approved",
    ]
    counts = {"approved": 0, "rejected": 0, "failed": 0}
    for outcome in outcomes:
        counts[_bucket_outcome(outcome)] += 1
    assert sum(counts.values()) == len(outcomes), (
        f"Bucket totals {counts} do not partition {len(outcomes)} executed items"
    )


def test_bucket_outcome_rejected_distinct_from_failed():
    """A reviewer rejection (coder quality issue) must NOT be lumped
    with tooling failures (harness broke). Operators need to distinguish
    'try iterating the coder' from 'something is wrong with the system.'"""
    assert _bucket_outcome("rejected") != _bucket_outcome("failed")
    assert _bucket_outcome("changes") != _bucket_outcome("failed")
