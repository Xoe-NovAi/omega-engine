# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract tests for the secret-history gate (scripts/check_secret_history.py).

The gate exists because `make gate-secrets` had no way to record a
disposition: it failed on any non-zero match count, including history the
project had already audited, so it could never go green. A gate that always
fails is equivalent to no gate, and one that can be silenced is worse — so
these tests pin both halves: the audited baseline is usable AND un-audited
material still fails.
"""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_secret_history.py"
BASELINE = REPO_ROOT / ".secret-history-baseline.toml"

_spec = importlib.util.spec_from_file_location("check_secret_history", SCRIPT)
checker = importlib.util.module_from_spec(_spec)
sys.modules["check_secret_history"] = checker
_spec.loader.exec_module(checker)


def test_baseline_is_not_gitignored():
    """The baseline must be a reviewable tracked file, not a local artifact."""
    import subprocess

    rel = str(BASELINE.relative_to(REPO_ROOT))
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", rel], cwd=REPO_ROOT
    )
    assert ignored.returncode != 0, "baseline must not be gitignored"


def test_baseline_stores_no_secret_material():
    """The baseline ships publicly, so it may contain hashes but never tokens."""
    text = BASELINE.read_text(encoding="utf-8")
    for name, rx in checker.PATTERNS.items():
        assert not rx.search(text), (
            f"baseline contains a raw {name}-shaped string; store only sha256 hashes"
        )


def test_baseline_entries_are_complete_and_unique():
    entries = checker.load_baseline()
    # [CUT-20261007] The audited count grows as history is audited (6 at
    # inception: 2 revoked + 4 public; +22 test-fixture mocks 2026-10-07).
    # Pin the SHAPE of every entry, not the count — the count is a fact to
    # report, never a contract to break when the next audit lands.
    assert len(entries) >= 6, f"baseline lost audited tokens: {len(entries)}"
    for digest, entry in entries.items():
        assert re.fullmatch(r"[0-9a-f]{16}", digest)
        assert entry["disposition"] in {"revoked", "retained-public", "purged", "test-fixture"}
        assert len(entry["why"]) > 20, "every disposition needs a real WHY"


def test_every_history_token_is_baselined():
    """Integration: durable refs must be fully accounted for."""
    history = checker.scan_history()
    baseline = checker.load_baseline()
    unaudited = sorted(set(history) - set(baseline))
    assert not unaudited, f"un-audited tokens in history: {unaudited}"


def test_no_revoked_token_exists_in_the_working_tree():
    """A rotated credential must never be pasted back into a tracked file."""
    baseline = checker.load_baseline()
    tree = checker.scan_tree()
    revoked = {
        digest
        for digest, entry in baseline.items()
        if entry["disposition"] in checker.TREE_FORBIDDEN_DISPOSITIONS
    }
    assert not (set(tree) & revoked), (
        f"a revoked token reappeared in the working tree: {sorted(set(tree) & revoked)}"
    )


def test_un_audited_token_is_reported(monkeypatch, capsys):
    """An unknown token must FAIL, not be quietly baselined."""
    bogus = "fc-" + "A" * 24
    monkeypatch.setattr(
        checker, "scan_history", lambda: {checker.token_hash(bogus): {"x.md"}}
    )
    monkeypatch.setattr(checker, "scan_tree", dict)
    assert checker.main() == 1
    out = capsys.readouterr().out
    assert "un-audited" in out
    assert bogus not in out, "the gate must never print secret material"
    assert checker.token_hash(bogus) in out


def test_revoked_token_in_tree_is_reported(monkeypatch, capsys):
    """Baselining a token does NOT license pasting it back into a file."""
    baseline = checker.load_baseline()
    revoked_digest = next(
        d for d, e in baseline.items() if e["disposition"] == "revoked"
    )
    monkeypatch.setattr(checker, "scan_history", lambda: {revoked_digest: {"old.md"}})
    monkeypatch.setattr(checker, "scan_tree", lambda: {revoked_digest: {"new.md"}})
    assert checker.main() == 1
    assert "must never be pasted back" in capsys.readouterr().out


def test_fully_audited_history_passes(monkeypatch, capsys):
    baseline = checker.load_baseline()
    monkeypatch.setattr(
        checker, "scan_history", lambda: {d: {"old.md"} for d in baseline}
    )
    monkeypatch.setattr(
        checker,
        "scan_tree",
        lambda: {
            d: {"data/secrets-public.toml"}
            for d, e in baseline.items()
            if e["disposition"] == "retained-public"
        },
    )
    assert checker.main() == 0
    assert "PASSED" in capsys.readouterr().out


def test_missing_baseline_is_a_toolchain_collapse_not_a_pass():
    with pytest.raises(checker.ToolchainCollapse):
        checker.load_baseline(REPO_ROOT / "does-not-exist.toml")


def test_incomplete_baseline_entry_is_rejected(tmp_path):
    bad = tmp_path / "baseline.toml"
    bad.write_text(
        'schema = 1\n[[entries]]\nid = "x"\nsha256_16 = "0123456789abcdef"\n',
        encoding="utf-8",
    )
    with pytest.raises(checker.ToolchainCollapse):
        checker.load_baseline(bad)


def test_duplicate_baseline_hash_is_rejected(tmp_path):
    entry = (
        '[[entries]]\nid = "{i}"\nsha256_16 = "0123456789abcdef"\n'
        'disposition = "revoked"\nwhy = "a sufficiently long rationale here"\n'
    )
    bad = tmp_path / "baseline.toml"
    bad.write_text(
        "schema = 1\n" + entry.format(i="a") + entry.format(i="b"), encoding="utf-8"
    )
    with pytest.raises(checker.ToolchainCollapse):
        checker.load_baseline(bad)


def test_token_hash_is_sha256_prefix():
    import hashlib

    assert checker.token_hash("abc") == hashlib.sha256(b"abc").hexdigest()[:16]
    assert len(checker.token_hash("abc")) == checker.HASH_PREFIX_LEN


def test_git_regex_uses_posix_ere_without_non_capturing_groups():
    """git -G compiles with POSIX ERE; (?:...) silently breaks the scan."""
    combined = "|".join(rx.pattern for rx in checker.PATTERNS.values())
    assert "(?:" not in combined, "non-capturing groups are invalid in git -G"

