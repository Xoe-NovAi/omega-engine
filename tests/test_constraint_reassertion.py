# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
# ⬡ OMEGA ⬡ MAAT ⬡ TEST ⬡ v1.0.0
"""Compaction-Immune Constraint Re-assertion Layer (P0-2, Governance Decay defense).

THE THREAT
----------
arXiv:2606.22528 ("Governance Decay", Jun 2026) measured that context compaction
silently erases *in-context* governance constraints: agents that reliably obey
standing rules while those rules are visible go on to perform prohibited tool
actions after compaction. Reproduced in LangGraph, AutoGen, and the OpenAI
Agents SDK.

The failure mode these tests pin is SPECIFIC and worth stating precisely,
because a green run of the wrong assertions would look identical to a green run
of the right ones: the interesting bug is not "the manifest is missing", it is
**"the manifest is silently absent and the caller cannot tell."** An empty
constraint set reads to an agent as "no constraints apply" -- which is precisely
the belief the threat exploits. So the assertions below are weighted toward
*loudness of failure*, not just presence of file.

COVERAGE MAP
------------
  (a) manifest exists and fits the 4KB injection budget
  (b) loader exits 1 on a missing manifest (and prints nothing to stdout)
  (c) all Tier-0 five IDs are present
  (d) the compaction-immune header string is present
  (e) hydration wiring actually re-asserts constraints (not just the loader)
  (f) gnosis stamping records the constraint set + digest
  (g) degradation paths refuse rather than returning an empty set
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "docs" / "governance" / "CONSTRAINTS.md"
LOADER = REPO_ROOT / "scripts" / "load_constraints.py"
HYDRATION = REPO_ROOT / "scripts" / "opencode-hydration.py"
GNOSIS_ARCHIVE = REPO_ROOT / "scripts" / "gnosis_archive.py"

MAX_MANIFEST_BYTES = 4096
TIER0_IDS = ("M1", "M7", "M11", "M15", "M23")
STRUCTURAL_IDS = ("M2", "M28")

# The exact string the task specification mandates. Asserted byte-for-byte
# because its value is that the artifact is RECOGNISABLE on re-injection: a
# manifest that quietly lost this banner is not the artifact we think it is.
EXPECTED_BANNER = (
    "This file is COMPACTION-IMMUNE. It is re-injected at every post-compact hydration."
)


def _run_loader(*args: str, env: dict[str, str] | None = None):
    """Invoke the loader as a SUBPROCESS -- exit codes are part of the contract.

    Testing main() in-process would prove the return value but not the exit
    code, and the exit code is what a gate or a Makefile actually observes.
    """
    import os

    full_env = {**os.environ, **(env or {})}
    return subprocess.run(
        [sys.executable, str(LOADER), *args],
        capture_output=True,
        text=True,
        env=full_env,
        cwd=str(REPO_ROOT),
    )


def _load_module(path: Path, name: str):
    """Import a script by path (they are not importable by module name)."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    # Sibling imports inside these scripts resolve against scripts/; make that
    # true for the in-process import too.
    sys.path.insert(0, str(LOADER.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(LOADER.parent))
    return mod


@pytest.fixture(scope="module")
def loader():
    return _load_module(LOADER, "load_constraints_under_test")


# ── (a) manifest exists and fits the injection budget ────────────────────────

def test_manifest_exists():
    assert MANIFEST.is_file(), f"constraint manifest missing at {MANIFEST}"


def test_manifest_within_4kb_budget():
    """A manifest that grows past 4KB is a manifest that will be truncated or
    skipped by whatever injects it. The budget is the feature."""
    size = MANIFEST.stat().st_size
    assert size <= MAX_MANIFEST_BYTES, (
        f"manifest is {size} bytes, over the {MAX_MANIFEST_BYTES}-byte budget; "
        f"trim prose, not mandate lines"
    )


def test_manifest_is_tracked_not_gitignored():
    """A governance artifact that is gitignored does not ship. This is the whole
    reason the manifest lives in docs/governance/ rather than data/coordination/
    (which .gitignore:116 excludes, and which a later `data/**/*.md` rule at
    .gitignore:272 re-excludes even for .md files)."""
    r = subprocess.run(
        ["git", "check-ignore", "-q", str(MANIFEST.relative_to(REPO_ROOT))],
        cwd=str(REPO_ROOT),
    )
    assert r.returncode != 0, (
        f"{MANIFEST.relative_to(REPO_ROOT)} is gitignored -- the constraint "
        "manifest must be a tracked, shipped artifact"
    )


# ── (b) loader exits 1 on missing manifest (M23) ─────────────────────────────

def test_loader_exits_1_when_manifest_missing(tmp_path):
    missing = tmp_path / "NO_SUCH_CONSTRAINTS.md"
    assert not missing.exists()
    r = _run_loader(env={"OMEGA_CONSTRAINTS_MANIFEST": str(missing)})
    assert r.returncode == 1, (
        f"expected exit 1 on missing manifest, got {r.returncode}. A soft-fail "
        "here reads to the caller as 'no constraints apply' (M23)."
    )


def test_loader_prints_nothing_to_stdout_when_missing(tmp_path):
    """The distinguishing assertion. Empty stdout is what separates "refused
    loudly" from "succeeded with zero constraints" -- and the latter is the
    exact shape of the vulnerability."""
    missing = tmp_path / "GONE.md"
    r = _run_loader("--format", "md", env={"OMEGA_CONSTRAINTS_MANIFEST": str(missing)})
    assert r.returncode == 1
    assert r.stdout.strip() == "", f"stdout must be empty on refusal, got: {r.stdout!r}"


def test_loader_reports_failure_on_stderr(tmp_path):
    missing = tmp_path / "GONE.md"
    r = _run_loader(env={"OMEGA_CONSTRAINTS_MANIFEST": str(missing)})
    assert "CONSTRAINT-MANIFEST-MISSING" in r.stderr


@pytest.mark.parametrize("fmt", ["md", "json", "ids"])
def test_loader_exit_1_in_every_output_format(tmp_path, fmt):
    """No format is allowed to be the soft one."""
    missing = tmp_path / "GONE.md"
    r = _run_loader("--format", fmt, env={"OMEGA_CONSTRAINTS_MANIFEST": str(missing)})
    assert r.returncode == 1, f"--format {fmt} did not fail loud"


def test_loader_rejects_manifest_without_banner(tmp_path):
    """A manifest stripped of its COMPACTION-IMMUNE banner is not servable.

    Without this check, deleting one line from the manifest would silently
    downgrade it to an ordinary doc that the loader happily serves.
    """
    stripped = tmp_path / "NO_BANNER.md"
    stripped.write_text(
        "\n".join(
            ln for ln in MANIFEST.read_text(encoding="utf-8").splitlines()
            if "COMPACTION-IMMUNE. It is re-injected" not in ln
        ),
        encoding="utf-8",
    )
    r = _run_loader(env={"OMEGA_CONSTRAINTS_MANIFEST": str(stripped)})
    assert r.returncode == 1, "banner-less manifest was served; that is a silent downgrade"


def test_loader_succeeds_on_real_manifest():
    r = _run_loader()
    assert r.returncode == 0, f"loader failed on the real manifest: {r.stderr}"
    assert r.stdout.strip() != ""


# ── (c) Tier-0 five IDs present ─────────────────────────────────────────────

@pytest.mark.parametrize("mandate_id", TIER0_IDS)
def test_tier0_ids_present_in_manifest(loader, mandate_id):
    """The Tier-0 five: M1 AnyIO, M7 Local-First, M11 Soul Integrity,
    M15 Continuity, M23 Failure Integrity."""
    text = MANIFEST.read_text(encoding="utf-8")
    assert f"**{mandate_id}**" in text, f"Tier-0 mandate {mandate_id} absent from manifest"


@pytest.mark.parametrize("mandate_id", STRUCTURAL_IDS)
def test_structural_prohibitions_present(loader, mandate_id):
    """Structural prohibitions with no second line of defence: M2 firewall,
    M28 artifact preservation."""
    text = MANIFEST.read_text(encoding="utf-8")
    assert f"**{mandate_id}**" in text, f"structural mandate {mandate_id} absent"


def test_hop_rule_present(loader):
    """M10/M15 Hop Rule -- named in the brief as must-never-be-compacted."""
    text = MANIFEST.read_text(encoding="utf-8")
    assert "Hop Rule" in text
    assert "Never self-delegate" in text


def test_loader_reports_no_missing_required_ids(loader):
    data = loader.load_constraints()
    assert data["missing_required"] == [], (
        f"loader reports missing required IDs: {data['missing_required']}"
    )


def test_loader_check_gate_passes():
    r = _run_loader("--check")
    assert r.returncode == 0, f"--check failed: {r.stderr}"


# ── (d) compaction-immune header string present ─────────────────────────────

def test_compaction_immune_header_string_present():
    assert EXPECTED_BANNER in MANIFEST.read_text(encoding="utf-8"), (
        "the exact compaction-immune header string is required so the artifact "
        "is recognisable on re-injection"
    )


def test_banner_constant_matches_manifest(loader):
    """The loader's constant and the file's banner must not drift apart."""
    assert loader.COMPACTION_IMMUNE_BANNER == EXPECTED_BANNER
    assert EXPECTED_BANNER in MANIFEST.read_text(encoding="utf-8")


def test_provenance_footer_present():
    """Date, AP token, and the threat reference that explains WHY this exists."""
    text = MANIFEST.read_text(encoding="utf-8")
    assert "AP-MAAT-v1.0.0" in text
    assert "2026-10-03" in text
    assert "2606.22528" in text, "the arXiv threat reference must be recorded"


# ── (e) hydration wiring re-asserts constraints ──────────────────────────────

def test_hydration_attaches_constraints(loader):
    """The loader existing is not the defence -- the hydration path calling it
    is. This asserts the wiring, which is the part most likely to rot."""
    hydration = _load_module(HYDRATION, "opencode_hydration_under_test")
    result = hydration.hydrate_session("ses_constraint_reassertion_probe")

    assert "constraints" in result, "hydration returned no constraints block"
    assert EXPECTED_BANNER in result["constraints"]
    for mandate_id in TIER0_IDS:
        assert mandate_id in result["constraint_ids"], (
            f"hydration dropped Tier-0 mandate {mandate_id}"
        )


def test_hydration_constraints_apply_even_with_no_task_state(loader):
    """An agent that remembers NOTHING is the one most likely to act
    unconstrained. Constraints must be attached on the not-restored path too."""
    hydration = _load_module(HYDRATION, "opencode_hydration_no_task_state")
    result = hydration.hydrate_session("ses_definitely_absent_session_id")
    assert result["constraint_ids"], "constraints dropped on the empty-task-state path"


def test_hydration_records_provenance(loader):
    hydration = _load_module(HYDRATION, "opencode_hydration_provenance")
    result = hydration.hydrate_session("ses_provenance_probe")
    src = result["constraint_source"]
    assert src["compaction_immune"] is True
    assert src["path"].endswith("CONSTRAINTS.md")
    assert src["size_bytes"] <= MAX_MANIFEST_BYTES


def test_hydration_refuses_when_manifest_missing(tmp_path, monkeypatch):
    """M23 end-to-end: no hydration payload may be produced without constraints.

    This is the single most important test in the file. If it regressed to
    returning `{"restored": False}` on a missing manifest, every downstream
    caller would carry on with an empty constraint set and nothing would say so.
    """
    monkeypatch.setenv(
        "OMEGA_CONSTRAINTS_MANIFEST", str(tmp_path / "GONE.md")
    )
    hydration = _load_module(HYDRATION, "opencode_hydration_missing_manifest")
    with pytest.raises(hydration.ConstraintManifestMissing):
        hydration.hydrate_session("ses_anything")


def test_hydration_cli_exits_1_when_manifest_missing(tmp_path):
    import os

    missing = tmp_path / "GONE.md"
    r = subprocess.run(
        [sys.executable, str(HYDRATION), "ses_probe"],
        capture_output=True,
        text=True,
        env={**os.environ, "OMEGA_CONSTRAINTS_MANIFEST": str(missing)},
        cwd=str(REPO_ROOT),
    )
    assert r.returncode == 1, f"hydration CLI returned {r.returncode}, expected 1"
    assert r.stdout.strip() == "", "hydration emitted a payload despite missing constraints"


# ── (f) gnosis stamping records the constraint set ───────────────────────────

def test_gnosis_stamp_block_includes_constraints():
    gnosis = _load_module(GNOSIS_ARCHIVE, "gnosis_archive_under_test")
    block = gnosis.build_block("probe_entity", "tester", "none")
    assert "constraints:" in block
    assert "constraints_digest:" in block
    for mandate_id in TIER0_IDS:
        assert mandate_id in block, f"gnosis stamp header dropped {mandate_id}"


def test_gnosis_stamp_digest_is_stable():
    gnosis = _load_module(GNOSIS_ARCHIVE, "gnosis_archive_digest_stable")
    a = gnosis.build_block("e", "t", "none")
    b = gnosis.build_block("e", "t", "none")
    digest = lambda b: [x for x in b.splitlines() if "constraints_digest" in x][0]
    assert digest(a) == digest(b), "constraint digest must be deterministic"


def test_gnosis_stamp_refuses_without_manifest(tmp_path, monkeypatch):
    """A gnosis stamped with no constraint set would read as stamped to
    `verify` while carrying nothing -- a falsely-stamped continuity record."""
    monkeypatch.setenv("OMEGA_CONSTRAINTS_MANIFEST", str(tmp_path / "GONE.md"))
    gnosis = _load_module(GNOSIS_ARCHIVE, "gnosis_archive_missing_manifest")
    with pytest.raises(gnosis.ConstraintManifestMissing):
        gnosis.build_block("probe_entity", "tester", "none")


def test_gnosis_verify_mode_still_green():
    """`make check-engine` runs `gnosis_archive.py verify` as its M15 gate.
    The new constraint dependency must not make that gate red."""
    r = subprocess.run(
        [sys.executable, str(GNOSIS_ARCHIVE), "verify"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert r.returncode == 0, f"M15 gnosis verify gate regressed: {r.stderr[-500:]}"


# ── (g) output shape is machine-consumable ───────────────────────────────────

def test_json_format_is_valid_json():
    r = _run_loader("--format", "json")
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["banner"] == EXPECTED_BANNER
    assert set(TIER0_IDS).issubset(set(payload["ids"]))
    assert all({"id", "law"} <= set(c) for c in payload["constraints"])


def test_ids_format_is_space_separated():
    r = _run_loader("--format", "ids")
    assert r.returncode == 0
    ids = r.stdout.split()
    assert set(TIER0_IDS).issubset(set(ids))
    assert all(i.startswith("M") for i in ids)