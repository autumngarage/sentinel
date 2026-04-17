"""Version is derived from git at build time, never hard-coded.

Dogfood on portfolio_new (2026-04-17) surfaced that `uv tool install
--force --from .` served a stale cached wheel because the version
(`0.2.0`) hadn't bumped between commits — uv's cache key is
(name, version), so the build cache hit even though source had
changed. Moving to git-derived versions (via `hatch-vcs`) ensures every
commit produces a unique version and the cache never serves stale
bits.

These tests guard the dynamic-version setup: a future revert to a
hard-coded version in pyproject.toml or __init__.py would reintroduce
the staleness bug.
"""

from __future__ import annotations

import re
from pathlib import Path

import sentinel

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"


def test_version_is_non_empty():
    assert sentinel.__version__
    assert isinstance(sentinel.__version__, str)


def test_version_is_pep440_shaped():
    """PEP 440: digits.digits.digits, optional .devN / .postN, optional +local.

    Dynamic versions from hatch-vcs look like `0.2.1.dev12+g49c9044d0`
    or `0.2.1` for a clean tag. Catches a silent regression where
    __version__ gets set to "unknown" or an empty string.
    """
    pattern = r"^\d+\.\d+(\.\d+)?([.-]?(dev|post|rc|a|b)\d+)?(\+[\w.]+)?$"
    assert re.match(pattern, sentinel.__version__), (
        f"__version__={sentinel.__version__!r} is not PEP 440-shaped"
    )


def test_pyproject_declares_dynamic_version():
    """Regression guard: pyproject.toml must NOT hard-code version.

    A reverted `version = "X.Y.Z"` line would reintroduce the uv cache
    staleness bug where reinstalling from the same source tree serves a
    cached wheel because the cache key (name, version) is stable across
    commits. dynamic = ["version"] + hatch-vcs is the fix.
    """
    text = PYPROJECT.read_text()
    # Allow commented-out version lines or version= in other sections;
    # the concern is a top-level [project] `version = "..."` assignment.
    project_section_match = re.search(
        r"\[project\](.*?)(?=^\[|\Z)", text, re.MULTILINE | re.DOTALL,
    )
    assert project_section_match, "pyproject.toml is missing [project] section"
    project_section = project_section_match.group(1)
    assert not re.search(r'^version\s*=\s*"', project_section, re.MULTILINE), (
        "pyproject.toml [project] hard-codes version — must use "
        "`dynamic = [\"version\"]` with hatch-vcs instead. See dogfood "
        "finding [2] in plans/dogfood-2026-04-17.md."
    )
    assert 'dynamic = ["version"]' in project_section or \
           "dynamic = ['version']" in project_section, (
        "pyproject.toml [project] must declare dynamic = [\"version\"]"
    )


def test_pyproject_configures_hatch_vcs():
    """hatch-vcs must be wired as the version source."""
    text = PYPROJECT.read_text()
    assert "hatch-vcs" in text, "hatch-vcs not declared in build-system.requires"
    assert "[tool.hatch.version]" in text, (
        "missing [tool.hatch.version] config"
    )
    assert re.search(r'source\s*=\s*"vcs"', text), (
        "hatch-vcs source must be 'vcs' (derive from git)"
    )


def test_init_reads_version_from_metadata():
    """__init__.py must read from importlib.metadata, not hard-code.

    Static readers are the same staleness trap as a hard-coded
    pyproject version: they desync from the built wheel.
    """
    init_text = (REPO_ROOT / "src" / "sentinel" / "__init__.py").read_text()
    assert "importlib.metadata" in init_text, (
        "__init__.py must use importlib.metadata to derive __version__"
    )
    assert not re.search(
        r'^__version__\s*=\s*"\d+\.\d+',
        init_text,
        re.MULTILINE,
    ), (
        "__init__.py hard-codes __version__ — must derive from "
        "importlib.metadata.version(\"sentinel\") instead"
    )
