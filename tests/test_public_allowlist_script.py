# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Regression: the allowlist cut must remove SYMLINKS from the index.

`scripts/apply_public_allowlist.sh` guarded its `git rm --cached` loop with

    if [[ ! -f "$f" ]]; then ... skip ... fi

`-f` is FALSE for a symlink whose target is a directory, and FALSE for a
DANGLING symlink. So the removal was silently SKIPPED for exactly the entries
that most need removing, while the script's own report still listed them as
"would be removed".

Real impact on the already-published `release/debut` (3c051021):

    data/library -> /media/arcana-novai/omega_library/library-archive
    data/memory  -> /media/arcana-novai/omega_library/memory-archive

Both were classified REMOVE, then dropped with "WARN: skip ... (not in working
tree)". The symlink blobs shipped publicly, leaking the operator account name
and the host mount layout.

The fix is `[[ ! -e "$f" && ! -L "$f" ]]` — skip only when the path is truly
absent AND is not a symlink, so regular files, directories, live symlinks and
dangling symlinks are all handed to `git rm --cached`.

Each test builds a real throwaway git repo, runs the real script, and asserts
on `git ls-files`. Nothing is mocked; M28 is respected throughout — removals
are index-only and the working tree is left intact.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "apply_public_allowlist.sh"

# A minimal allowlist in the exact format the script parses.
# `keep.txt` is allowed; everything else — including symlinks — is cut.
MINIMAL_ALLOWLIST = """# 🔱 minimal test allowlist
## ✅ ALLOW — Public Surface

```
keep.txt
```

## 🚫 FORGE — NOT on Public Surface

```
forge/
```
"""


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


def _make_repo(tmp_path: Path) -> Path:
    """A throwaway repo whose index is clean (--confirm requires it)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "allowlist-test")
    _git(repo, "config", "commit.gpgsign", "false")

    (repo / "keep.txt").write_text("public\n")
    (repo / "secret.txt").write_text("private\n")
    (repo / "allowlist.txt").write_text(MINIMAL_ALLOWLIST)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "seed")
    return repo


def _run_script(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT), "--allowlist", "allowlist.txt", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        timeout=120,
    )


def _tracked(repo: Path) -> set[str]:
    return set(_git(repo, "ls-files").split())


# ── the regression itself ───────────────────────────────────────────────────


@pytest.mark.skipif(shutil.which("git") is None, reason="git required")
def test_symlink_to_directory_is_removed_from_index(tmp_path: Path):
    """THE leak. `-f` is false for a symlink-to-directory, so `-f` skipped it."""
    repo = _make_repo(tmp_path)
    target = tmp_path / "outside" / "library-archive"
    target.mkdir(parents=True)
    (repo / "data").mkdir()
    (repo / "data" / "library").symlink_to(target, target_is_directory=True)

    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "add symlink")
    assert "data/library" in _tracked(repo)

    proc = _run_script(repo, "--confirm")
    assert proc.returncode == 0, proc.stdout + proc.stderr

    tracked = _tracked(repo)
    assert "keep.txt" in tracked, "allowed file must survive"
    assert "secret.txt" not in tracked, "non-allowed file must be cut"
    assert "data/library" not in tracked, (
        "SYMLINK LEAK: data/library survived the cut — its target "
        "(/media/<user>/omega_library/...) would be published verbatim"
    )
    # M28: index-only. The working tree must be untouched.
    assert (repo / "data" / "library").is_symlink(), "working tree must be intact"


def test_absolute_target_symlink_leak_is_closed(tmp_path: Path):
    """The exact published leak: an absolute host path as the link target."""
    repo = _make_repo(tmp_path)
    (repo / "data").mkdir()
    (repo / "data" / "memory").symlink_to("/media/arcana-novai/omega_library/memory-archive")

    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "add leak")

    _run_script(repo, "--confirm")
    assert "data/memory" not in _tracked(repo)


def test_dangling_symlink_is_removed_from_index(tmp_path: Path):
    """`-e` is false for a dangling symlink, so `-e` alone would also skip it."""
    repo = _make_repo(tmp_path)
    (repo / "data").mkdir()
    (repo / "data" / "library").symlink_to("/media/does-not-exist/anywhere")

    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "add dangling symlink")

    proc = _run_script(repo, "--confirm")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "data/library" not in _tracked(repo)
    assert "skip data/library" not in proc.stderr, (
        f"symlink was skipped, not removed:\n{proc.stderr}"
    )


def test_symlink_to_regular_file_is_removed_from_index(tmp_path: Path):
    """`-f` was TRUE here, so this path already worked — guard the regression."""
    repo = _make_repo(tmp_path)
    (repo / "real.txt").write_text("payload\n")
    (repo / "data").mkdir()
    (repo / "data" / "link.txt").symlink_to(repo / "real.txt")

    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "add file symlink")

    _run_script(repo, "--confirm")
    tracked = _tracked(repo)
    assert "data/link.txt" not in tracked
    assert "real.txt" not in tracked


def test_regular_file_removal_still_works(tmp_path: Path):
    """No regression on the ordinary path."""
    repo = _make_repo(tmp_path)
    proc = _run_script(repo, "--confirm")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    tracked = _tracked(repo)
    assert tracked == {"keep.txt", "allowlist.txt"}, tracked
    assert (repo / "secret.txt").is_file(), "M28: working tree file must survive"


def test_genuinely_absent_path_is_skipped_but_loudly(tmp_path: Path):
    """`-e` false AND `-L` false: the guard's remaining case.

    The prescribed guard is `[[ ! -e "$f" && ! -L "$f" ]]`, so a path that is
    in the index, absent from the working tree, and NOT a symlink is skipped.
    What must never happen is a SILENT skip — M23. The path must be named in
    the warning so an operator can see the index and the tree have diverged.
    """
    repo = _make_repo(tmp_path)
    # Commit a path that never exists in the working tree. `--assume-unchanged`
    # keeps `git status --porcelain` clean so the --confirm dirty-check does not
    # short-circuit before the guard is reached.
    empty_blob = _git(repo, "hash-object", "-w", "--stdin").strip()
    _git(repo, "update-index", "--add", "--cacheinfo", f"100644,{empty_blob},ghost.txt")
    _git(repo, "commit", "-qm", "add a path with no working-tree entry")
    _git(repo, "update-index", "--assume-unchanged", "ghost.txt")
    assert "ghost.txt" in _tracked(repo)

    proc = _run_script(repo, "--confirm")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "ghost.txt" in proc.stderr, f"the skip must be reported, got: {proc.stderr!r}"
    assert "not a symlink" in proc.stderr, proc.stderr
    # Everything genuinely present in the tree was still cut.
    assert "secret.txt" not in _tracked(repo)
    assert "keep.txt" in _tracked(repo)


# ── classification must see symlinks, not just regular files ─────────────────


def test_summary_reports_symlink_counts(tmp_path: Path):
    """Classification counts symlinks as a distinct kind, not as files.

    `data/library` (symlink -> absolute host path) and `keep_link.txt`
    (symlink -> regular file) are both cut; `keep.txt` is allowed. Both
    symlinks must be COUNTED, which the old working-tree `-f` test could not
    do — it classified neither of them as anything at all.
    """
    repo = _make_repo(tmp_path)
    (repo / "data").mkdir()
    (repo / "data" / "library").symlink_to("/media/arcana-novai/omega_library/library-archive")
    (repo / "keep_link.txt").symlink_to("keep.txt")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "symlinks")

    proc = _run_script(repo, "--summary")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert re.search(r"Symlinks removed:\s*2\b", proc.stdout), proc.stdout
    assert re.search(r"Symlinks kept:\s*0\b", proc.stdout), proc.stdout


def test_kept_symlinks_are_reported_with_their_target(tmp_path: Path):
    """A symlink the allowlist KEEPS still ships as a pointer — must be loud.

    This does not change the boundary (M23: boundary changes need a human); it
    makes an invisible leak impossible.
    """
    repo = _make_repo(tmp_path)
    (repo / "keep.txt").unlink()
    (repo / "keep.txt").symlink_to("/media/arcana-novai/omega_library/library-archive")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "allowed symlink")

    proc = _run_script(repo, "--confirm")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "keep.txt" in _tracked(repo), "allowlist must still keep it"
    assert "SYMLINK LEAK AUDIT" in proc.stdout, proc.stdout
    assert "keep.txt" in proc.stdout
    assert "/media/arcana-novai/omega_library/library-archive" in proc.stdout, (
        "the audit must print the target that would be published"
    )
    assert "LEAK" in proc.stdout


def test_audit_does_not_flag_regular_files_as_symlinks(tmp_path: Path):
    """Only index mode 120000 is a symlink.

    Regression guard: an earlier draft of the audit tested "does the index know
    this path" instead of "is this path a symlink", so it reported EVERY kept
    file as a leak and printed file CONTENT as if it were a target path.
    """
    repo = _make_repo(tmp_path)
    proc = _run_script(repo, "--confirm")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "SYMLINK LEAK AUDIT" not in proc.stdout, proc.stdout
    assert re.search(r"Symlinks kept:\s*0\b", proc.stdout), proc.stdout
    # The audit block is the only place a blob's CONTENT is printed as a
    # target path. With no symlinks there must be no such block at all, so no
    # file content can have leaked into one.
    assert "CHECK " not in proc.stdout and "  LEAK  " not in proc.stdout, proc.stdout


def test_strict_refuses_while_a_symlink_is_kept(tmp_path: Path):
    repo = _make_repo(tmp_path)
    (repo / "keep.txt").unlink()
    (repo / "keep.txt").symlink_to("/media/arcana-novai/omega_library/library-archive")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "allowed symlink")

    proc = _run_script(repo, "--strict")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "symlink" in proc.stderr.lower(), proc.stderr


# ── static guard against re-introducing the buggy predicate ─────────────────


def test_script_has_no_bare_f_guard_before_git_rm():
    """The `-f` guard must not come back.

    `-f` is false for symlink-to-directory and for dangling symlinks; `-e` is
    false for dangling symlinks. Only `! -e && ! -L` covers every case.
    """
    text = SCRIPT.read_text(encoding="utf-8")
    code_lines = [
        ln.strip()
        for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    guard_lines = [
        ln for ln in code_lines if re.search(r"\[\[.*-[fel] \"\$f\"", ln)
    ]
    for ln in guard_lines:
        assert re.search(r"\[\[ ! -e \"\$f\" && ! -L \"\$f\" \]\]", ln), (
            f"guard on $f must test -e AND -L, found: {ln!r}"
        )
    assert '[[ ! -e "$f" && ! -L "$f" ]]' in text
    assert not any(
        re.search(r"\[\[ ! -f \"\$f\"", ln) for ln in code_lines
    ), "the buggy -f guard must not come back"


def test_script_reports_symlinks_read_from_the_index():
    """Symlink detection must read index mode 120000, not stat the tree."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert "120000" in text, "must key off the git index symlink mode"
    assert "INDEX_MODE" in text