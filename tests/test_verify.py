"""Tests for the post-execute verifier.

Verification is the third signal alongside Coder + Reviewer: an
objective re-run of the project's own lint and test commands. These
tests cover the contract — what verdicts the verifier produces in
which conditions, that we never invent commands, that subprocess
errors fall through cleanly, and that the JSONL log appends rather
than overwriting.
"""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003 — runtime use via tmp_path
from unittest.mock import patch

from sentinel.verify import (
    CheckResult,
    WorkItemVerification,
    discover_checks,
    persist_verification,
    run_check,
    verify_work_item,
)


class TestRunCheck:
    def test_no_command_returns_no_check_defined(self, tmp_path: Path) -> None:
        result = run_check("lint", None, tmp_path)
        assert result.verdict == "no_check_defined"
        assert result.command is None

    def test_passing_command_returns_pass(self, tmp_path: Path) -> None:
        # /bin/true exits 0 — universally available, deterministic
        result = run_check("lint", "/usr/bin/true", tmp_path)
        assert result.verdict == "pass"
        assert result.command == "/usr/bin/true"

    def test_failing_command_returns_fail(self, tmp_path: Path) -> None:
        result = run_check("lint", "/usr/bin/false", tmp_path)
        assert result.verdict == "fail"

    def test_nonexistent_command_returns_skipped(self, tmp_path: Path) -> None:
        """A configured tool that isn't installed is an environment gap,
        not a code defect — record `skipped` with an install hint so the
        work item can still ship on the strength of other checks. Rolling
        up as `fail` would block every Swift project without swiftlint,
        every Python project without ruff, etc., from shipping any code
        (the exact failure mode that triggered this fix on autumn-mail
        2026-04-18). no_check_defined is still reserved for 'project
        never configured a command at all' (covered above)."""
        result = run_check(
            "lint", "/no/such/command/at/all", tmp_path,
        )
        assert result.verdict == "skipped"
        assert "not installed" in result.evidence

    def test_missing_known_tool_includes_install_hint(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """Skipped evidence for known tools carries the install hint so
        the operator can close the gap without spelunking docs. We force
        FileNotFoundError via monkeypatch rather than relying on the
        real tool being absent on the test host — swiftlint may or may
        not be installed on dev machines, and the unit under test is
        'how do we format the evidence when the tool is missing',
        independent of the host's installed tooling."""
        def raise_fnf(*_args, **_kwargs):
            raise FileNotFoundError(2, "No such file or directory", "swiftlint")
        monkeypatch.setattr("sentinel.verify.subprocess.run", raise_fnf)
        result = run_check("lint", "swiftlint", tmp_path)
        assert result.verdict == "skipped"
        assert "swiftlint" in result.evidence
        assert "brew install swiftlint" in result.evidence

    def test_missing_unknown_tool_falls_back_to_bare_message(
        self, tmp_path: Path,
    ) -> None:
        """Unknown tools still produce a useful skipped message even
        without an install hint."""
        result = run_check("lint", "totally-unknown-binary-xyz", tmp_path)
        assert result.verdict == "skipped"
        assert "totally-unknown-binary-xyz" in result.evidence
        assert "skipping" in result.evidence

    def test_evidence_is_truncated(self, tmp_path: Path) -> None:
        """Long output gets clipped to MAX_EVIDENCE_CHARS — postmortem
        readers want the failing tail, not megabytes of stdout."""
        # Generate ~5KB of output via a shell command
        result = run_check(
            "lint",
            "sh -c 'for i in $(seq 1 500); do echo line-$i; done; exit 1'",
            tmp_path,
        )
        assert result.verdict == "fail"
        # Should be capped well under 5000 chars
        assert len(result.evidence) <= 1000
        # The tail should still be intact (we trim the head, not the tail)
        assert "line-500" in result.evidence

    def test_timeout_marks_fail_with_evidence(self, tmp_path: Path) -> None:
        """A slow check that exceeds timeout becomes fail (something is
        wrong), not no_check_defined (we couldn't tell)."""
        result = run_check(
            "test", "sleep 5", tmp_path, timeout_s=1,
        )
        assert result.verdict == "fail"
        assert "timed out" in result.evidence


class TestVerifyWorkItem:
    def test_all_passing_yields_verified(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        monkeypatch.setattr(
            "sentinel.verify.discover_checks",
            lambda _: {"lint": "/usr/bin/true", "test": "/usr/bin/true"},
        )
        result = verify_work_item(tmp_path, "wi-1", "Test item")
        assert result.overall == "verified"
        assert all(c.verdict == "pass" for c in result.checks)

    def test_any_failing_yields_not_verified(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """Even one failed check flips overall to not_verified — the
        whole point of verification is that ANY broken invariant
        invalidates the diff."""
        monkeypatch.setattr(
            "sentinel.verify.discover_checks",
            lambda _: {"lint": "/usr/bin/true", "test": "/usr/bin/false"},
        )
        result = verify_work_item(tmp_path, "wi-2", "Bad item")
        assert result.overall == "not_verified"

    def test_no_commands_yields_no_check_defined(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """A project with no configured lint/test commands gets
        no_check_defined — sentinel never silently passes a work
        item it can't actually verify."""
        monkeypatch.setattr(
            "sentinel.verify.discover_checks",
            lambda _: {"lint": None, "test": None},
        )
        result = verify_work_item(tmp_path, "wi-3", "Untestable")
        assert result.overall == "no_check_defined"

    def test_mixed_pass_and_no_command_is_verified(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """Lint passes, test command not configured → still verified.
        We have at least one positive signal and no negative signals."""
        monkeypatch.setattr(
            "sentinel.verify.discover_checks",
            lambda _: {"lint": "/usr/bin/true", "test": None},
        )
        result = verify_work_item(tmp_path, "wi-4", "Half-checked")
        assert result.overall == "verified"

    def test_pass_plus_skipped_yields_verified(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """A project with one passing check + one configured-but-
        uninstalled tool must end up `verified` — skipped checks don't
        poison a clean bill of health from the checks that actually
        ran. The alternative (roll up as not_verified) would block
        every Swift project without swiftlint from shipping."""
        monkeypatch.setattr(
            "sentinel.verify.discover_checks",
            lambda _: {
                "lint": "/usr/bin/true",  # passes
                "test": "/no/such/command",  # not installed → skipped
            },
        )
        result = verify_work_item(tmp_path, "wi-x", "Half-skipped")
        assert result.overall == "verified"
        verdicts = {c.name: c.verdict for c in result.checks}
        assert verdicts == {"lint": "pass", "test": "skipped"}

    def test_pass_plus_fail_yields_not_verified(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """A real failure still propagates — skipped handling must not
        mask genuine check failures."""
        monkeypatch.setattr(
            "sentinel.verify.discover_checks",
            lambda _: {
                "lint": "/usr/bin/true",  # passes
                "test": "/usr/bin/false",  # fails
            },
        )
        result = verify_work_item(tmp_path, "wi-y", "Real fail")
        assert result.overall == "not_verified"

    def test_all_skipped_yields_unverified(
        self, tmp_path: Path, monkeypatch,
    ) -> None:
        """Every configured check skipped for missing tools → we have
        no signal at all. Must not claim `verified` (no positive signal)
        and must not claim `not_verified` (nothing actually failed).
        The `unverified` verdict captures 'tools were configured but
        none of them ran' distinctly from both."""
        monkeypatch.setattr(
            "sentinel.verify.discover_checks",
            lambda _: {
                "lint": "/no/such/lint",
                "test": "/no/such/test",
            },
        )
        result = verify_work_item(tmp_path, "wi-z", "All skipped")
        assert result.overall == "unverified"
        assert all(c.verdict == "skipped" for c in result.checks)

    def test_records_metadata(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(
            "sentinel.verify.discover_checks",
            lambda _: {"lint": "/usr/bin/true"},
        )
        result = verify_work_item(
            tmp_path, "wi-5", "With metadata", branch="feat/x",
        )
        assert result.work_item_id == "wi-5"
        assert result.work_item_title == "With metadata"
        assert result.branch == "feat/x"
        assert result.timestamp  # non-empty ISO 8601


class TestPersistVerification:
    def test_writes_jsonl_at_expected_path(self, tmp_path: Path) -> None:
        v = WorkItemVerification(
            work_item_id="wi-1",
            work_item_title="Test",
            overall="verified",
            checks=[
                CheckResult(
                    name="lint", command="/usr/bin/true",
                    verdict="pass", duration_s=0.1, evidence="ok",
                ),
            ],
            branch="feat/x",
            timestamp="2026-04-15T10:00:00+00:00",
        )
        path = persist_verification(tmp_path, v)
        assert path == tmp_path / ".sentinel" / "verifications.jsonl"
        assert path.exists()

    def test_jsonl_lines_are_individually_parseable(
        self, tmp_path: Path,
    ) -> None:
        """Each line must be valid JSON on its own — trend tooling
        streams the file line-by-line."""
        for i in range(3):
            persist_verification(tmp_path, WorkItemVerification(
                work_item_id=f"wi-{i}",
                work_item_title=f"Item {i}",
                overall="verified",
                checks=[],
                timestamp=f"2026-04-15T10:00:0{i}+00:00",
            ))

        log = (tmp_path / ".sentinel" / "verifications.jsonl").read_text()
        lines = [ln for ln in log.splitlines() if ln.strip()]
        assert len(lines) == 3
        for ln in lines:
            payload = json.loads(ln)
            assert "work_item_id" in payload
            assert "overall" in payload

    def test_writes_on_every_outcome(self, tmp_path: Path) -> None:
        """Regression guard for V2 of autumn-garage journal
        2026-04-18-first-cycle-attempt-findings: today's v0.3.3 cycle
        had two verifier failures that didn't appear in
        verifications.jsonl. Persist must happen regardless of
        outcome — pass, fail, skipped, no_check_defined all produce a
        line, so the jsonl is a faithful audit log."""
        outcomes = [
            ("pass-item", "verified", "pass"),
            ("fail-item", "not_verified", "fail"),
            ("skip-item", "unverified", "skipped"),
            ("nocheck-item", "no_check_defined", "no_check_defined"),
        ]
        for wi_id, overall, check_verdict in outcomes:
            persist_verification(tmp_path, WorkItemVerification(
                work_item_id=wi_id,
                work_item_title=wi_id,
                overall=overall,
                checks=[CheckResult(
                    name="lint", command="x", verdict=check_verdict,
                    duration_s=0.0, evidence="test",
                )],
                timestamp="2026-04-18T10:00:00+00:00",
            ))
        log = (tmp_path / ".sentinel" / "verifications.jsonl").read_text()
        lines = [ln for ln in log.splitlines() if ln.strip()]
        assert len(lines) == len(outcomes)
        parsed_ids = {json.loads(ln)["work_item_id"] for ln in lines}
        assert parsed_ids == {wi_id for wi_id, _, _ in outcomes}

    def test_appends_does_not_overwrite(self, tmp_path: Path) -> None:
        v1 = WorkItemVerification(
            work_item_id="first", work_item_title="First",
            overall="verified", checks=[], timestamp="t1",
        )
        v2 = WorkItemVerification(
            work_item_id="second", work_item_title="Second",
            overall="not_verified", checks=[], timestamp="t2",
        )
        persist_verification(tmp_path, v1)
        persist_verification(tmp_path, v2)

        log = (tmp_path / ".sentinel" / "verifications.jsonl").read_text()
        assert "first" in log
        assert "second" in log


class TestDiscoverChecks:
    def test_uses_state_detection(self, tmp_path: Path) -> None:
        """Verifier must not invent commands — it reuses state.py's
        detect_project_type so verifier and scan agree on what 'this
        project's lint command' is."""
        with patch("sentinel.state.detect_project_type") as mock_detect:
            mock_detect.return_value = {
                "lint_command": "ruff check .",
                "test_command": "pytest",
            }
            result = discover_checks(tmp_path)
            mock_detect.assert_called_once_with(tmp_path)
            assert result == {"lint": "ruff check .", "test": "pytest"}

    def test_touchstone_config_overrides_detection(self, tmp_path: Path) -> None:
        """If the project has an explicit .touchstone-config, that wins
        over auto-detection — same precedence as state.py uses for
        scans, so the two paths can never disagree."""
        touchstone_config = tmp_path / ".touchstone-config"
        touchstone_config.write_text(
            "lint_command=my-custom-lint\n"
            "test_command=my-custom-test\n",
        )
        with patch("sentinel.state.detect_project_type") as mock_detect:
            mock_detect.return_value = {
                "lint_command": "auto-detected-lint",
                "test_command": "auto-detected-test",
            }
            result = discover_checks(tmp_path)
            assert result["lint"] == "my-custom-lint"
            assert result["test"] == "my-custom-test"
