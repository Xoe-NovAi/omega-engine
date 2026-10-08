# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""check-hub-imports must DESCRIBE the tree it tested. [D-620]

THE DEFECT
----------
`Makefile:1027` ran `git diff HEAD` in `$CWD`, applied the result onto a
freshly-created detached worktree at HEAD, and then reported:

    check-hub-imports PASSED (6 modules import cleanly in a clean venv)

The venv was clean. The CODE WAS NOT. On a tree with modified files this
returns 0 while describing HEAD — a false-green generator.

WHAT IS ASSERTED
----------------
1. `banner()` names the tested tree, ALWAYS.
2. An overlay is announced with its file count AND an explicit statement that
   the verdict does NOT describe HEAD.
3. Pristine mode announces no-overlay and never writes a patch — enforcement
   is structural (no patch file exists), not a convention in the Makefile.
4. `require-pristine` FAILS on a dirty tree with a distinct exit code.
5. The verdict line carries the tested-tree identity on pass AND on fail.
6. The Makefile no longer contains the ambiguous "clean venv" claim and DOES
   invoke the describer, so the script cannot be orphaned.

MUTATION PROVENANCE
-------------------
The discrimination proof is recorded in the D-620 report, not asserted by a
comment. These tests are written to go RED when `banner()` is emptied,
`BANNER_MARKER` is deleted, `write_patch` ignores pristine mode, or the
`require_pristine` branch is removed — each was verified by mutating
`scripts/check_hub_import_gate.py` and observing a failure.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_hub_import_gate as gate  # noqa: E402


@pytest.fixture()
def sandbox(tmp_path):
    """A throwaway git repo with one commit and one dirty tracked file."""
    repo = tmp_path / "repo"
    repo.mkdir()

    def g(*args, **kw):
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, check=True, **kw)

    g("init", "-q")
    g("config", "user.email", "t@t.t")
    g("config", "user.name", "t")
    (repo / "mod.py").write_text("x = 1\n")
    (repo / "other.py").write_text("y = 1\n")
    g("add", "-A")
    g("commit", "-qm", "init")
    return repo


# ── 1/2: the banner always describes the tree ────────────────────────────────

def test_banner_always_carries_marker(sandbox):
    """A green result must never be ambiguous. Marker present when CLEAN."""
    p = gate.plan(sandbox, gate.MODE_PRISTINE)
    out = gate.banner(p)
    assert gate.BANNER_MARKER in out
    assert p.head_sha in out


def test_marker_literal_is_pinned(sandbox):
    """The marker is asserted as a LITERAL, not only via the module constant.

    Asserting `gate.BANNER_MARKER in out` alone is a tautology: rename the
    constant and the assertion still passes, which is exactly the mutation
    that would let someone quietly change or drop the visible banner tag.
    This is the test that makes M2 (rename the marker) go red.
    """
    out = gate.banner(gate.plan(sandbox, gate.MODE_PRISTINE))
    assert "GATE-FIDELITY" in out


def test_banner_reports_overlay_with_count_and_files(sandbox):
    (sandbox / "mod.py").write_text("x = 2\n")  # dirty ONE tracked file
    p = gate.plan(sandbox, gate.MODE_AUTO)

    assert p.overlaid is True
    assert p.dirty is True
    out = gate.banner(p)
    assert "GATE-FIDELITY" in out
    # The count is stated as a count, not merely implied by a file listing.
    assert "1 uncommitted file(s)" in out
    # The file itself is named — an operator can see WHAT was tested.
    assert "mod.py" in out
# And it says, in words, that this is not a verdict about HEAD.
    assert "not HEAD" in out


def test_overlay_count_matches_file_list(sandbox):
    """If the banner claims N files, it must name exactly N. Otherwise the
    banner is a decoration and the count is a second, independent lie."""
    for name in ("mod.py", "other.py"):
        (sandbox / name).write_text("changed\n")
    p = gate.plan(sandbox, gate.MODE_AUTO)
    out = gate.banner(p)
    assert "2 uncommitted file(s)" in out
    named = [ln for ln in out.splitlines() if ln.strip().startswith("+ ")]
    assert len(named) == 2
    assert {ln.strip()[2:] for ln in named} == {"mod.py", "other.py"}


def test_pristine_banner_says_no_overlay(sandbox):
    (sandbox / "mod.py").write_text("x = 99\n")  # DIRTY
    p = gate.plan(sandbox, gate.MODE_PRISTINE)

    assert p.overlaid is False          # override, not "diff was empty"
    assert p.dirty is True              # the tree IS dirty — that is still known
    out = gate.banner(p)
    assert "NO overlay" in out
    assert "describes HEAD exactly" in out
    # Critically: it must NOT claim an overlay it did not perform.
    assert "OVERLAY APPLIED" not in out


# ── 3: pristine enforcement is STRUCTURAL ────────────────────────────────────

def test_write_patch_refuses_in_pristine_mode(sandbox):
    (sandbox / "mod.py").write_text("x = 3\n")
    dest = sandbox / "overlay.patch"
    p = gate.plan(sandbox, gate.MODE_PRISTINE)

    wrote = gate.write_patch(sandbox, dest, p)
    assert wrote is False
    # No patch file => the Makefile's `[ -s ... ]` test is false => no overlay.
    # The guarantee does not depend on the Makefile cooperating.
    assert not dest.exists()


def test_write_patch_writes_in_auto_mode(sandbox):
    (sandbox / "mod.py").write_text("x = 4\n")
    dest = sandbox / "overlay.patch"
    p = gate.plan(sandbox, gate.MODE_AUTO)
    assert gate.write_patch(sandbox, dest, p) is True
    assert dest.exists()
    assert "x = 4" in dest.read_text()


def test_patch_is_empty_when_tree_is_clean(sandbox):
    dest = sandbox / "overlay.patch"
    p = gate.plan(sandbox, gate.MODE_AUTO)
    assert p.overlaid is False
    assert gate.write_patch(sandbox, dest, p) is False


# ── 4: require-pristine fails loudly, distinctly ────────────────────────────

def test_require_pristine_fails_on_dirty_tree(sandbox, capsys):
    (sandbox / "mod.py").write_text("x = 5\n")
    rc = gate.main(["--repo", str(sandbox), "--mode", gate.MODE_PRISTINE,
                    "--require-pristine"])
    assert rc == gate.EXIT_DIRTY_IN_PRISTINE_MODE
    assert rc != 0
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "mod.py" in out          # names what is dirty


def test_require_pristine_passes_on_clean_tree(sandbox, capsys):
    rc = gate.main(["--repo", str(sandbox), "--mode", gate.MODE_PRISTINE,
                    "--require-pristine"])
    assert rc == gate.EXIT_OK
    assert gate.BANNER_MARKER in capsys.readouterr().out


def test_require_pristine_off_allows_dirty_tree(sandbox):
    """The release path is strict; the LOCAL path must still test work-in-
    progress. That asymmetry is the point — it is opt-in, not imposed."""
    (sandbox / "mod.py").write_text("x = 6\n")
    rc = gate.main(["--repo", str(sandbox), "--mode", gate.MODE_AUTO])
    assert rc == gate.EXIT_OK


# ── 5: the verdict line is the gate's final word — it must be honest ────────

def test_verdict_line_passes_state_the_tree(sandbox):
    (sandbox / "mod.py").write_text("x = 7\n")
    p = gate.plan(sandbox, gate.MODE_AUTO)
    v = gate.verdict_line(p, 6, ok=True)
    assert "PASSED" in v
    assert p.head_sha in v
    assert "UNCOMMITTED WORK, NOT HEAD" in v


def test_verdict_line_failures_also_state_the_tree(sandbox):
    """A failure that hides its scope sends the operator to the wrong tree."""
    p = gate.plan(sandbox, gate.MODE_AUTO)
    v = gate.verdict_line(p, 6, ok=False)
    assert "FAILED" in v
    assert p.head_sha in v


def test_verdict_line_pristine_makes_no_uncommitted_claim(sandbox):
    p = gate.plan(sandbox, gate.MODE_PRISTINE)
    v = gate.verdict_line(p, 6, ok=True)
    assert "pristine" in v
    assert "UNCOMMITTED WORK, NOT HEAD" not in v


# ── 6: the Makefile is wired to the describer ───────────────────────────────

def test_makefile_invokes_the_gate_describer():
    mk = (REPO / "Makefile").read_text()
    assert "scripts/check_hub_import_gate.py" in mk


def test_makefile_no_longer_makes_the_ambiguous_claim():
    """The exact string that produced the false green."""
    mk = (REPO / "Makefile").read_text()
    assert "modules import cleanly in a clean venv" not in mk


def test_makefile_passed_line_states_tested_tree():
    mk = (REPO / "Makefile").read_text()
    assert "tested tree:" in mk


def test_makefile_failed_line_states_tested_tree():
    """Both outcomes carry the tree. A failure with no scope is a wild goose
    chase for whoever has to reproduce it."""
    mk = (REPO / "Makefile").read_text()
    assert mk.count("--label-only") >= 2


def test_ci_and_release_use_pristine():
    for wf in ("ci.yml", "release.yml", "sote.yml"):
        txt = (REPO / ".github" / "workflows" / wf).read_text()
        assert "HUB_IMPORT_MODE=pristine" in txt, wf
        assert "require_clean=1" in txt, wf


# ── the CWD trap itself ──────────────────────────────────────────────────────

def test_plan_is_independent_of_cwd(tmp_path, monkeypatch, sandbox):
    """THE ORIGINAL TRAP. The old code ran `git diff HEAD` in `$CWD`.

    Invoking the gate from a subdirectory must not change which tree it
    describes, and must not silently diff nothing.
    """
    sub = sandbox / "deep" / "nested"
    sub.mkdir(parents=True)
    (sandbox / "mod.py").write_text("x = 8\n")

    from_root = gate.plan(sandbox, gate.MODE_AUTO)
    monkeypatch.chdir(sub)
    from_subdir = gate.plan(sandbox, gate.MODE_AUTO)

    assert from_subdir.overlay_files == from_root.overlay_files == ["mod.py"]
    assert from_subdir.head_sha == from_root.head_sha
    assert from_subdir.overlaid is True


def test_untracked_files_are_disclosed_not_silently_dropped(sandbox):
    """The gate excludes untracked files by design. Silently excluding them
    while saying "1 uncommitted file" would be a second, quieter lie."""
    (sandbox / "brand_new.py").write_text("z = 1\n")
    out = gate.banner(gate.plan(sandbox, gate.MODE_AUTO),
                      gate.untracked_files(sandbox))
    assert "untracked file(s) NOT tested" in out
    assert "brand_new.py" in out
