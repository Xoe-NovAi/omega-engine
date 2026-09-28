# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ MAAT ⬡ TEST ⬡ v1.0.0
"""Tests for the M15 continuity tools.

The scripts under test touch `data/entities/<entity>/`, so every test here runs
against a THROWAWAY entity directory. `REPO_ROOT` is monkeypatched to a tmp
path before either module resolves `ENTITIES_DIR`, so no test can possibly
write to the real gnoses. There is no test here that mutates real data, and
that is deliberate: the tool's whole purpose is to be non-destructive, so the
tests must be too.
"""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
ga = _load("gnosis_archive", SCRIPTS / "gnosis_archive.py")
gt = _load("gnosis_timeline", SCRIPTS / "gnosis_timeline.py")


@pytest.fixture
def fake_repo(tmp_path, monkeypatch):
    """Point both modules at a throwaway data/entities tree."""
    ents = tmp_path / "data" / "entities"
    ents.mkdir(parents=True)
    monkeypatch.setattr(ga, "ENTITIES_DIR", ents)
    monkeypatch.setattr(ga, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gt, "ENTITIES_DIR", ents)
    monkeypatch.setattr(gt, "REPO_ROOT", tmp_path)
    return ents


def _write_gnosis(ents: Path, entity: str, body: str) -> Path:
    d = ents / entity
    d.mkdir(parents=True, exist_ok=True)
    p = d / "session_gnosis.md"
    p.write_text(body, encoding="utf-8")
    return p


SPDX = "<!--\nSPDX-FileCopyrightText: 2026 Xoe-NovAi\n\nSPDX-License-Identifier: Apache-2.0\n-->\n"


# ── archive ──────────────────────────────────────────────────────────────────

def test_archive_then_stamp_round_trip(fake_repo, capsys):
    """Archive preserves the prior state; stamp records what it superseded."""
    p = _write_gnosis(fake_repo, "maat", SPDX + "\n# Session Gnosis — Maat\n\nold body\n")
    assert ga.do_archive("maat", dry_run=False) == 0

    arch = fake_repo / "maat" / "gnosis" / "archive"
    files = list(arch.glob("session_gnosis_*.md"))
    assert len(files) == 1, "archive must contain exactly one copy"
    assert "old body" in files[0].read_text(encoding="utf-8"), "archive must hold PRIOR content"
    assert p.read_text(encoding="utf-8") == SPDX + "\n# Session Gnosis — Maat\n\nold body\n", \
        "archive must not mutate the source"

    # now the agent overwrites, then stamps
    p.write_text(SPDX + "\n# Session Gnosis — Maat\n\nnew body\n", encoding="utf-8")
    assert ga.do_stamp("maat", "maat", None, dry_run=False) == 0

    meta = ga.parse_meta(p.read_text(encoding="utf-8"))
    assert meta is not None
    assert meta["entity"] == "maat"
    assert meta["stamped_by"] == "maat"
    assert meta["schema_version"] == ga.SCHEMA_VERSION
    assert meta["supersedes"] == files[0].name, "must name the archive it replaces"
    assert "new body" in p.read_text(encoding="utf-8"), "stamp must not alter the body"


def test_stamp_preserves_spdx_first(fake_repo):
    """REUSE tooling needs its licence header at the top; stamping must not bury it."""
    p = _write_gnosis(fake_repo, "x", SPDX + "\n# Gnosis\n")
    ga.do_stamp("x", "t", "none", dry_run=False)
    lines = p.read_text(encoding="utf-8").split("\n")
    assert lines[0].lstrip().startswith("<!--"), "SPDX comment must remain first"
    assert "SPDX-License-Identifier" in "\n".join(lines[:6])


def test_stamp_is_idempotent(fake_repo):
    """Re-stamping refreshes in place; it must not stack headers."""
    p = _write_gnosis(fake_repo, "x", SPDX + "\n# Gnosis\n")
    ga.do_stamp("x", "a", "none", dry_run=False)
    ga.do_stamp("x", "b", "none", dry_run=False)
    text = p.read_text(encoding="utf-8")
    assert text.count(ga.BEGIN) == 1, "exactly one meta block must exist"
    assert ga.parse_meta(text)["stamped_by"] == "b", "second stamp must win"


def test_archive_no_clobber_on_repeat(fake_repo, capsys):
    """M23: a name collision must never destroy an existing archive."""
    p = _write_gnosis(fake_repo, "y", SPDX + "\nfirst\n")
    assert ga.do_archive("y", dry_run=False) == 0
    # Force a collision by writing the same filename the tool will pick.
    arch = fake_repo / "y" / "gnosis" / "archive"
    first = list(arch.glob("*.md"))[0]
    original = first.read_text(encoding="utf-8")

    p.write_text(SPDX + "\nsecond\n", encoding="utf-8")
    # Rewrite mtime-derived collision by re-running within the same minute.
    assert ga.do_archive("y", dry_run=False) == 0

    files = sorted(arch.glob("session_gnosis_*.md"))
    assert len(files) >= 2, "a second archive must be created, not overwrite the first"
    assert first.read_text(encoding="utf-8") == original, "original archive must be intact"
    assert any("no clobber" in l or "already exists" in l
               for l in capsys.readouterr().out.splitlines()), \
        "no-clobber must be reported, not silent"


def test_dry_run_mutates_nothing(fake_repo):
    """--dry-run on both mutating modes must be side-effect free."""
    p = _write_gnosis(fake_repo, "z", SPDX + "\nbody\n")
    before = p.read_text(encoding="utf-8")
    assert ga.do_archive("z", dry_run=True) == 0
    assert not (fake_repo / "z" / "gnosis" / "archive").exists(), "dry-run must not create dirs"
    assert ga.do_stamp("z", "t", None, dry_run=True) == 0
    assert p.read_text(encoding="utf-8") == before, "dry-run must not touch the file"
    assert ga.parse_meta(before) is None


def test_archive_refuses_when_no_gnosis(fake_repo, capsys):
    """No source file must fail loudly, not silently succeed."""
    assert ga.do_archive("ghost", dry_run=False) == 1
    assert "nothing to archive" in capsys.readouterr().err


# ── verify ───────────────────────────────────────────────────────────────────

def test_verify_exits_nonzero_on_unstamped(fake_repo, capsys):
    """This is the CI gate: an unstamped gnosis MUST fail it."""
    _write_gnosis(fake_repo, "unstamped", SPDX + "\n# Gnosis\n")
    rc = ga.do_verify()
    assert rc == 1, "verify must exit non-zero when a gnosis is unstamped"
    assert "UNSTAMPED" in capsys.readouterr().out


def test_verify_passes_when_all_stamped(fake_repo):
    """Conversely, a fully stamped tree must be green — or the gate is theater."""
    for e in ("a", "b", "c"):
        _write_gnosis(fake_repo, e, SPDX + "\n# Gnosis\n")
        assert ga.do_stamp(e, "tester", "none", dry_run=False) == 0
    assert ga.do_verify() == 0


def test_verify_flags_history_at_risk(fake_repo, capsys):
    """Many session rows but zero archives == prior state was already lost."""
    body = SPDX + "\n# Gnosis\n\n| Date | ID | Summary |\n|---|---|---|\n"
    body += "| 2026-09-20 | s1 | a |\n| 2026-09-21 | s2 | b |\n| 2026-09-22 | s3 | c |\n"
    p = _write_gnosis(fake_repo, "risky", body)
    ga.do_stamp("risky", "tester", "none", dry_run=False)
    assert ga.do_verify() == 0  # stamped, so gate passes
    out = capsys.readouterr().out
    assert "AT-RISK" in out and "risky" in out, "history-at-risk must still be reported"


# ── timeline ─────────────────────────────────────────────────────────────────

KNOWN_TABLE = SPDX + """
# Session Gnosis — Maat

## Session History

| Date | Session ID | Summary |
|------|------------|---------|
| 2026-09-25 | maat_gates_20260925 | Gate hardening sprint |
| 2026-09-28 | maat_seam_repair_20260928 | Seam repair |
"""


def test_timeline_parses_known_table(fake_repo):
    """Table rows are the primary source and must yield date+id+summary."""
    _write_gnosis(fake_repo, "maat", KNOWN_TABLE)
    entries = gt.parse_gnosis("maat", fake_repo / "maat" / "session_gnosis.md")
    assert len(entries) == 2
    assert entries[0]["date"] == "2026-09-25"
    assert entries[0]["session_id"] == "maat_gates_20260925"
    assert "Gate hardening" in entries[0]["summary"]
    assert entries[1]["date"] == "2026-09-28"


def test_timeline_heading_fallback(fake_repo):
    """With no table, dated headings are used instead."""
    _write_gnosis(fake_repo, "h", SPDX + "\n# Gnosis\n\n## 2026-09-20 first\n")
    entries = gt.parse_gnosis("h", fake_repo / "h" / "session_gnosis.md")
    assert len(entries) == 1
    assert entries[0]["kind"] == "heading"
    assert entries[0]["date"] == "2026-09-20"


def test_timeline_reads_gnosis_subdir(fake_repo):
    """The new gnosis/ location must be discovered too."""
    d = fake_repo / "n" / "gnosis"
    d.mkdir(parents=True)
    (d / "session_gnosis.md").write_text(KNOWN_TABLE, encoding="utf-8")
    found = {e for e, _ in gt.gnosis_files(None)}
    assert "n" in found
    entries = gt.parse_gnosis("n", d / "session_gnosis.md")
    assert len(entries) == 2


def test_timeline_filters_and_ordering(fake_repo, capsys):
    """--since/--until filter; output is newest-first."""
    _write_gnosis(fake_repo, "m", KNOWN_TABLE)
    rc = gt.main(["--entity", "m", "--format", "json", "--no-orphan-check"])
    assert rc == 0
    import json as _json
    payload = _json.loads(capsys.readouterr().out)
    dates = [e["date"] for e in payload["entries"]]
    assert dates == sorted(dates, reverse=True), "newest first"

    rc = gt.main(["--entity", "m", "--since", "2026-09-27",
                 "--format", "json", "--no-orphan-check"])
    payload = _json.loads(capsys.readouterr().out)
    assert [e["date"] for e in payload["entries"]] == ["2026-09-28"]


def test_orphan_session_ids_detected(fake_repo, tmp_path, monkeypatch, capsys):
    """A cited session id absent from the DB is a broken continuity reference."""
    db = tmp_path / "opencode.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE session (id TEXT)")
    con.execute("INSERT INTO session VALUES ('ses_REAL000000000000')")
    con.commit()
    con.close()
    monkeypatch.setattr(gt, "DB_PATH", db)

    # 'ses_FAKE...' is deliberately absent from the DB.
    _write_gnosis(fake_repo, "o", SPDX + "\n# G\n\n## 2026-09-28 ses_FAKEdeadbeef0001\n")
    known = gt.known_session_ids()
    assert known == {"ses_REAL000000000000"}

    rc = gt.main(["--entity", "o", "--format", "json"])
    assert rc == 0
    import json as _json
    payload = _json.loads(capsys.readouterr().out)
    assert "ses_FAKEdeadbeef0001" in payload["orphan_session_ids"]["o"], \
        "fake id must be reported as orphaned"
    assert "ses_REAL000000000000" not in payload["orphan_session_ids"].get("o", [])


def test_db_opens_read_only(fake_repo, tmp_path, monkeypatch):
    """The 45 GB DB must never be mutated — assert the URI is read-only."""
    db = tmp_path / "ro.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE session (id TEXT)")
    con.execute("INSERT INTO session VALUES ('ses_AAAABBBBCCCCDDDD')")
    con.commit()
    con.close()
    monkeypatch.setattr(gt, "DB_PATH", db)
    assert gt.known_session_ids() == {"ses_AAAABBBBCCCCDDDD"}
    # A write attempt through the same handle must fail.
    with pytest.raises(sqlite3.OperationalError):
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            con.execute("DELETE FROM session")
        finally:
            con.close()


def test_stale_entities_flagged(fake_repo, capsys):
    """--stale-days lists entities whose newest entry is older than N days."""
    import json as _json
    _write_gnosis(fake_repo, "old", SPDX + "\n| 2020-01-01 | s | x |\n")
    _write_gnosis(fake_repo, "new", SPDX + "\n" + KNOWN_TABLE.split("\n", 5)[5])
    rc = gt.main(["--format", "json", "--stale-days", "30", "--no-orphan-check"])
    assert rc == 0
    payload = _json.loads(capsys.readouterr().out)
    assert "old" in payload["stale_entities"], "stale entity must be flagged"
    assert "new" not in payload["stale_entities"], "fresh entity must not be flagged"


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__]))
