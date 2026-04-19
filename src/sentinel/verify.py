"""Post-execute verification — does the project still pass its own checks?

When Coder commits a feature branch and Reviewer approves it, that's
two LLMs agreeing on a diff. Verification adds a third, deterministic
signal: the project's own lint and test commands, re-run against the
new code. If they pass, the work item is `verified`. If not, it's
`not_verified` regardless of what the reviewer said. Two opinions plus
one objective check.

This module is deliberately narrow — it only runs commands the project
ITSELF has configured (via `.touchstone-config` or auto-detected from
project type). Sentinel never invents a check command. If a project
has no configured lint/test command, the verdict is `no_check_defined`
rather than silently passing.

A configured-but-not-installed tool (e.g. `swiftlint` in a Swift project
on a machine that hasn't `brew install`-ed it) records `skipped` — not
`fail`. A missing tool is an environment gap, not a code defect; treating
it as `fail` would block every Swift project without swiftlint, every
Python project without ruff, etc. from shipping any code. The skipped
verdict carries an install hint so the operator can close the gap.

What this module does NOT do:
- It does not parse Coder's claims or commit messages. The project's
  existing checks are the contract; if they pass, the project's
  invariants still hold. That's a stronger guarantee than parsing
  English from a commit message.
- It does not gate merging. The verifier produces a verdict that the
  journal records; downstream automation (or a future PR) can decide
  what to do with not_verified items. Today, it's an honest signal.
- It does not isolate the project's working tree from check side
  effects (e.g., `.ruff_cache/`, `__pycache__/`). Those are exactly
  what the project's own CI produces; sentinel running the same
  commands inherits the same write footprint, intentionally.
"""

from __future__ import annotations

import json
import logging
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path  # noqa: TC003 — runtime use for fs reads/writes

logger = logging.getLogger(__name__)

# Per-check wall-clock cap so a hung lint/test doesn't eat the cycle.
# Configurable later if needed; 60s is generous for lint, tight for
# big test suites — projects with long suites can configure a faster
# subset as their test_command (CI-grade, not full).
DEFAULT_CHECK_TIMEOUT_S = 60

# Maximum chars of evidence to keep per check. Trim from the END so the
# important "FAILED:" / "errors found:" lines stay in the persisted log.
MAX_EVIDENCE_CHARS = 1000

# Install hints for tools we see in the wild. Keyed by the bare binary
# name (the first token of the configured command). When a check is
# skipped because the tool isn't installed, the evidence includes this
# hint so the operator can close the gap without spelunking docs.
# Intentionally small — just the ones we've encountered in dogfood
# across autumn-garage projects. Add more as they come up.
TOOL_INSTALL_HINTS: dict[str, str] = {
    "swiftlint": "brew install swiftlint",
    "swiftformat": "brew install swiftformat",
    "ruff": "pip install ruff  # or: uv tool install ruff",
    "black": "pip install black",
    "mypy": "pip install mypy",
    "pytest": "pip install pytest  # or: uv add --dev pytest",
    "clippy": "rustup component add clippy",
    "cargo": "install Rust via rustup: https://rustup.rs",
    "eslint": "npm install -g eslint",
    "prettier": "npm install -g prettier",
    "tsc": "npm install -g typescript",
    "shellcheck": "brew install shellcheck",
    "hadolint": "brew install hadolint",
    "golangci-lint": "brew install golangci-lint",
    "gofmt": "install Go: https://go.dev/dl/",
}


def _install_hint(command: str) -> str:
    """Return an install hint for the tool referenced by `command`.

    Splits the command on shell tokens and looks up the first meaningful
    token in TOOL_INSTALL_HINTS. Handles `cargo clippy` (two tokens) by
    also checking the second token. Falls back to an empty string when
    no hint is known — caller substitutes the default message."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return ""
    # Primary: first token (e.g. "swiftlint", "ruff")
    head = Path(tokens[0]).name  # strip any path prefix
    if head in TOOL_INSTALL_HINTS:
        return TOOL_INSTALL_HINTS[head]
    # Secondary: subcommand (e.g. "cargo clippy" → "clippy")
    if len(tokens) > 1 and tokens[1] in TOOL_INSTALL_HINTS:
        return TOOL_INSTALL_HINTS[tokens[1]]
    return ""


def _missing_tool_name(command: str) -> str:
    """Extract the tool name to mention in skipped evidence. Uses the
    first token of the command (stripped of any path prefix) so the
    message reads naturally: `swiftlint not installed`, not
    `/opt/homebrew/bin/swiftlint not installed`."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    return Path(tokens[0]).name if tokens else command


@dataclass
class CheckResult:
    name: str  # "lint" | "test"
    command: str | None  # None if no command available
    verdict: str  # "pass" | "fail" | "skipped" | "no_check_defined"
    duration_s: float = 0.0
    evidence: str = ""  # short tail of stdout+stderr for postmortem


@dataclass
class WorkItemVerification:
    work_item_id: str
    work_item_title: str
    # "verified" | "not_verified" | "unverified" | "no_check_defined"
    overall: str
    checks: list[CheckResult] = field(default_factory=list)
    branch: str | None = None
    timestamp: str = ""


def discover_checks(project_path: Path) -> dict[str, str | None]:
    """Return {check_name: command_or_None} from touchstone-config or
    auto-detect. Reuses state.py's machinery so verification and scan
    state-gathering can never disagree about what a project's lint /
    test commands are."""
    from sentinel.state import _read_touchstone_command, detect_project_type

    touchstone_config = project_path / ".touchstone-config"
    detected = detect_project_type(project_path)
    return {
        "lint": (
            _read_touchstone_command(touchstone_config, "lint_command")
            or detected.get("lint_command")
        ),
        "test": (
            _read_touchstone_command(touchstone_config, "test_command")
            or detected.get("test_command")
        ),
    }


def run_check(
    name: str,
    command: str | None,
    project_path: Path,
    timeout_s: int = DEFAULT_CHECK_TIMEOUT_S,
) -> CheckResult:
    """Run one check. Verdicts:
    - no_check_defined: no command configured
    - pass: command ran and exited 0
    - fail: command ran and exited non-zero, or timed out
    - skipped: command's tool is not installed (FileNotFoundError)
    """
    if not command:
        return CheckResult(
            name=name, command=None, verdict="no_check_defined",
            evidence="(no command configured)",
        )

    started = time.perf_counter()
    try:
        result = subprocess.run(  # noqa: S603 — command is project-owned
            shlex.split(command),
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            name=name, command=command, verdict="fail",
            duration_s=time.perf_counter() - started,
            evidence=f"(timed out after {timeout_s}s)",
        )
    except FileNotFoundError:
        # The configured tool isn't installed on this machine. This is
        # an environment gap, not a code defect — treat it as `skipped`
        # so the work item can still ship on the strength of the other
        # checks. The alternative (rolling up as `fail`) would block
        # every Swift project without swiftlint, every Python project
        # without ruff, etc., from shipping a single line of code.
        # Log a visible warning so the gap doesn't hide silently.
        tool = _missing_tool_name(command)
        hint = _install_hint(command)
        if hint:
            evidence = (
                f"{tool} not installed — skipping this check. "
                f"Install to enable verification: {hint}"
            )
        else:
            evidence = f"{tool} not installed — skipping"
        logger.warning(
            "verifier check %r skipped: %s not installed (hint: %s)",
            name, tool, hint or "none known",
        )
        return CheckResult(
            name=name, command=command, verdict="skipped",
            duration_s=time.perf_counter() - started,
            evidence=evidence,
        )
    except OSError as e:
        # Command was configured but couldn't start for a non-"missing
        # binary" reason (permission denied, exec format error, etc.).
        # This is a misconfiguration, NOT a skipped tool — the binary
        # exists but something about running it is wrong. Surface as
        # fail so it rolls up to not_verified.
        return CheckResult(
            name=name, command=command, verdict="fail",
            duration_s=time.perf_counter() - started,
            evidence=f"command not runnable: {e}",
        )

    duration = time.perf_counter() - started
    output = (result.stdout + result.stderr).strip()
    evidence = output[-MAX_EVIDENCE_CHARS:] if output else "(no output)"
    verdict = "pass" if result.returncode == 0 else "fail"
    return CheckResult(
        name=name, command=command, verdict=verdict,
        duration_s=duration, evidence=evidence,
    )


def verify_work_item(
    project_path: Path,
    work_item_id: str,
    work_item_title: str,
    branch: str | None = None,
    *,
    working_directory: Path | None = None,
) -> WorkItemVerification:
    """Run all configured checks against the project, return a verdict.

    `working_directory` is where the checks actually execute (the
    worktree path in worktree-managed mode). Defaults to `project_path`
    for the legacy single-tree path. Check configuration (touchstone-config
    etc.) is always read from `project_path` since it's repo-wide.

    Overall verdict logic (skipped checks excluded from pass/fail math):
    - All checks have no command → no_check_defined (we couldn't tell)
    - At least one fail → not_verified (claim contradicted by reality)
    - At least one pass, zero fail → verified (skipped checks don't
      poison a clean bill of health from the checks that DID run)
    - Zero pass, zero fail, at least one skipped → unverified (every
      configured check was skipped for missing tools; we have no
      signal at all — don't claim verified)
    """
    checks_config = discover_checks(project_path)
    run_dir = working_directory or project_path
    results = [
        run_check(name, command, run_dir)
        for name, command in checks_config.items()
    ]

    verdicts = [r.verdict for r in results]
    n_pass = sum(1 for v in verdicts if v == "pass")
    n_fail = sum(1 for v in verdicts if v == "fail")
    n_skipped = sum(1 for v in verdicts if v == "skipped")

    if all(v == "no_check_defined" for v in verdicts):
        overall = "no_check_defined"
    elif n_fail > 0:
        overall = "not_verified"
    elif n_pass > 0:
        overall = "verified"
    elif n_skipped > 0:
        # All configured checks skipped (tools missing). We have no
        # signal — don't claim verified, but don't roll up as
        # not_verified either (nothing actually failed).
        overall = "unverified"
    else:
        # Shouldn't reach here (all four bins empty implies zero
        # results, which means discover_checks returned an empty dict),
        # but be conservative if we do.
        overall = "no_check_defined"

    return WorkItemVerification(
        work_item_id=work_item_id,
        work_item_title=work_item_title,
        overall=overall,
        checks=results,
        branch=branch,
        timestamp=datetime.now(UTC).isoformat(),
    )


def persist_verification(
    project_path: Path,
    verification: WorkItemVerification,
) -> Path:
    """Append the verification to .sentinel/verifications.jsonl.

    Append-only, one line per verification, JSON-per-line so trend
    tooling can stream it. Each line is self-describing — never relies
    on prior lines for context.

    Writes happen regardless of outcome — pass, fail, skipped, and
    no_check_defined all produce a line. A verifier run that didn't
    leave a trail is indistinguishable from one that didn't happen,
    which is exactly what the v0.3.3 cycle's V2 finding flagged."""
    sentinel_dir = project_path / ".sentinel"
    sentinel_dir.mkdir(parents=True, exist_ok=True)
    log_path = sentinel_dir / "verifications.jsonl"

    payload = {
        "ts": verification.timestamp,
        "work_item_id": verification.work_item_id,
        "title": verification.work_item_title,
        "branch": verification.branch,
        "overall": verification.overall,
        "checks": [
            {
                "name": c.name,
                "command": c.command,
                "verdict": c.verdict,
                "duration_s": round(c.duration_s, 3),
                "evidence": c.evidence,
            }
            for c in verification.checks
        ],
    }
    with log_path.open("a") as f:
        f.write(json.dumps(payload) + "\n")
    return log_path
