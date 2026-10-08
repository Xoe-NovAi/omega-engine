# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Decide-and-DESCRIBE the tree `make check-hub-imports` is about to test. [D-620]

THE DEFECT THIS EXISTS TO KILL
------------------------------
`Makefile:1027` ran `git diff HEAD` **in `$CWD`** and applied that patch onto a
freshly-created detached worktree at HEAD. The intent was legitimate: test the
work you are about to commit, not the work you committed three days ago.

The defect was in the REPORTING, not the intent. The gate's success line read:

    check-hub-imports PASSED (6 modules import cleanly in a clean venv)

"clean venv" is true. "clean" also modifies the code under test, and the line
never said which tree produced the verdict. So on a tree with N modified files
the gate would return 0 while describing HEAD — a false-green generator. On a
tree with 18 concurrently-modified files it is not theoretical.

THE RULE ENFORCED HERE
----------------------
**A gate's verdict must describe the tree it actually tested.** That is the
whole invariant. Three modes, all explicit, none silent:

    auto     (default)  overlay the tracked working-tree diff, and SAY SO
    pristine             never overlay; test HEAD exactly
    require-pristine     never overlay AND fail if the tree is dirty

`auto` keeps the valuable behaviour (uncommitted work gets tested). `pristine`
and `require-pristine` exist for the release/CI path, where the artefact about
to ship IS HEAD and anything else is a lie.

The banner is emitted unconditionally, in every mode, on success AND on
failure. A green result is never ambiguous about what it covered.

WHY A SCRIPT AND NOT MORE MAKEFILE
----------------------------------
The verdict must be assertable. A banner buried in a backslash-continued shell
line is untestable except by running the whole gate — which builds a venv from
PyPI and takes minutes. Here the decision is a pure function of (repo, mode)
and is unit-testable in milliseconds. `tests/test_check_hub_import_gate.py`
mutates this file to prove the test discriminates.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ── exit codes (M23: distinct failures get distinct codes) ───────────────────
EXIT_OK = 0
EXIT_DIRTY_IN_PRISTINE_MODE = 3
EXIT_GIT_FAILED = 4

MODE_AUTO = "auto"
MODE_PRISTINE = "pristine"

#: Marker the regression test greps for. If someone deletes the banner
#: emission, this string stops appearing and the test goes red — that is the
#: discrimination proof, not a tautology.
BANNER_MARKER = "GATE-FIDELITY"


@dataclass
class Plan:
    """What the gate is about to test, stated before it tests it."""

    mode: str
    head_sha: str
    #: Files whose working-tree content will be overlaid onto HEAD.
    overlay_files: list[str] = field(default_factory=list)
    dirty: bool = False
    #: True when the tested tree is HEAD + uncommitted work, i.e. NOT HEAD.
    overlaid: bool = False

    @property
    def covers_uncommitted(self) -> bool:
        return self.overlaid

    @property
    def tested_tree_label(self) -> str:
        """One-line identity of the tree this verdict is about."""
        if self.overlaid:
            return (f"HEAD {self.head_sha} + {len(self.overlay_files)} "
                    f"uncommitted file(s)")
        return f"HEAD {self.head_sha} (pristine)"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False,
    )


def head_sha(repo: Path) -> str:
    r = _git(repo, "rev-parse", "--short", "HEAD")
    if r.returncode != 0:
        return "UNKNOWN"
    return r.stdout.strip() or "UNKNOWN"


def changed_files(repo: Path) -> list[str]:
    """Tracked files differing from HEAD. Untracked files are EXCLUDED.

    Exclusion is inherited from the gate's original design and is stated in
    the banner, because "3 uncommitted files" when there are 9 would be the
    same class of lie this module exists to prevent.
    """
    r = _git(repo, "diff", "HEAD", "--name-only")
    if r.returncode != 0:
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def untracked_files(repo: Path) -> list[str]:
    r = _git(repo, "ls-files", "--others", "--exclude-standard")
    if r.returncode != 0:
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def plan(repo: Path, mode: str = MODE_AUTO) -> Plan:
    """The pure decision: given a repo and a mode, what tree will be tested?

    Note this reads `$CWD`-independent state via `git -C repo`, and `repo` is
    resolved from the repository root, NOT from wherever make happened to be
    invoked. That is part of the fix: the old code ran `git diff HEAD` against
    an ambient CWD, so invoking the gate from a subdirectory silently diffed
    the wrong tree — or diffed nothing at all.
    """
    sha = head_sha(repo)
    changed = changed_files(repo)
    p = Plan(mode=mode, head_sha=sha, overlay_files=changed, dirty=bool(changed))
    if mode == MODE_AUTO:
        p.overlaid = bool(changed)
    return p


def banner(p: Plan, untracked: list[str] | None = None) -> str:
    """The self-description. Emitted in EVERY mode, on pass AND fail.

    Contains BANNER_MARKER, the HEAD sha, and — when an overlay was applied —
    the file count, the files, and an explicit statement that the verdict does
    NOT describe HEAD.
    """
    untracked = untracked or []
    lines = [f"  [{BANNER_MARKER}] tested tree: {p.tested_tree_label}"]
    if p.overlaid:
        lines.append(
            f"  [{BANNER_MARKER}] OVERLAY APPLIED — this verdict covers "
            f"UNCOMMITTED WORK, not HEAD."
        )
        for f in p.overlay_files:
            lines.append(f"      + {f}")
    else:
        lines.append(
            f"  [{BANNER_MARKER}] NO overlay — the verdict describes HEAD exactly."
        )
    if untracked:
        lines.append(
            f"  [{BANNER_MARKER}] {len(untracked)} untracked file(s) NOT tested "
            f"(excluded by design): {', '.join(untracked[:5])}"
            + (" ..." if len(untracked) > 5 else "")
        )
    return "\n".join(lines)


def verdict_line(p: Plan, module_count: int, ok: bool = True) -> str:
    """The final summary line. Carries the tested-tree identity, always."""
    state = "PASSED" if ok else "FAILED"
    return (f"check-hub-imports {state} — {module_count} modules imported in a "
            f"fresh venv — tested tree: {p.tested_tree_label}"
            + ("  [VERDICT COVERS UNCOMMITTED WORK, NOT HEAD]" if p.overlaid else ""))


def write_patch(repo: Path, dest: Path, p: Plan) -> bool:
    """Materialise the overlay patch. Returns True if a patch was written.

    No patch is written in pristine mode — that is the enforcement, not a
    convention. The Makefile applies the file only if it exists AND is
    non-empty, so an empty/absent patch is a structural no-overlay.
    """
    if not p.overlaid:
        return False
    r = _git(repo, "diff", "HEAD")
    if r.returncode != 0:
        return False
    if not r.stdout.strip():
        return False
    dest.write_text(r.stdout)
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Describe the tree check-hub-imports will test (D-620)")
    ap.add_argument("--repo", default=".", help="repository root (not CWD)")
    ap.add_argument("--mode", default=MODE_AUTO, choices=[MODE_AUTO, MODE_PRISTINE],
                    help="auto=overlay tracked diff; pristine=never overlay")
    ap.add_argument("--require-pristine", action="store_true",
                    help="additionally FAIL if the working tree is dirty")
    ap.add_argument("--patch-out", default=None,
                    help="write the overlay patch here (auto mode only)")
    ap.add_argument("--label-only", action="store_true",
                    help="print only the tested-tree label (for the verdict line)")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        print(f"FAIL: {repo} is not a git repository root", file=sys.stderr)
        return EXIT_GIT_FAILED

    p = plan(repo, args.mode)
    if args.label_only:
        print(p.tested_tree_label + (" [UNCOMMITTED]" if p.overlaid else ""))
        return EXIT_OK
    print(banner(p, untracked_files(repo)))

    if args.require_pristine and p.dirty:
        print("")
        print(f"FAIL: require-pristine mode and {len(p.overlay_files)} tracked "
              f"file(s) differ from HEAD.")
        print("      A release gate must describe the artefact that will ship.")
        for f in p.overlay_files:
            print(f"      - {f}")
        print("      Commit them, stash them, or drop --require-pristine.")
        return EXIT_DIRTY_IN_PRISTINE_MODE

    if args.patch_out:
        wrote = write_patch(repo, Path(args.patch_out), p)
        # Machine-readable, so the Makefile never has to guess.
        print(f"  [{BANNER_MARKER}] patch_written={'yes' if wrote else 'no'}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
