# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""W1-4 unit tests for scripts/correct_ics_provenance.py.

Fixture-based ONLY — never touches the live 17G opencode.db.
Covers: Tier-0 resolver (hit/miss/db-down), ledger append integrity
(root-cause regression test for the rename-clobber bug), anchor recall,
and idempotent update-in-place semantics.
"""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "correct_ics_provenance.py"

spec = importlib.util.spec_from_file_location("prov_worker", SCRIPT)
assert spec is not None and spec.loader is not None
prov = importlib.util.module_from_spec(spec)
sys.modules["prov_worker"] = prov
spec.loader.exec_module(prov)


# ---------------------------------------------------------------- fixtures

@pytest.fixture()
def fixture_db(tmp_path):
    """Minimal replica of opencode.db message table."""
    db = tmp_path / "opencode.db"
    con = sqlite3.connect(db)
    con.execute(
        "CREATE TABLE message (id text PRIMARY KEY, session_id text NOT NULL,"
        " time_created integer NOT NULL, time_updated integer NOT NULL, data text NOT NULL)"
    )
    con.execute(
        "CREATE INDEX msg_idx ON message (session_id, time_created, id)"
    )

    def insert(sid, role, model):
        con.execute(
            "INSERT INTO message VALUES (?,?,?,?,?)",
            (f"msg_{sid}_{role}_{model}_{con.total_changes}", sid, 1787000000000, 1787000000000,
             json.dumps({"role": role, "modelID": model})),
        )

    # hot-swap session: 2 models
    for m in ("x-preview-f-free", "nemotron-3-ultra-free", "x-preview-f-free"):
        insert("ses_known1111111111", "assistant", m)
    insert("ses_known1111111111", "user", None)
    # single-model session
    insert("ses_single22222222", "assistant", "big-pickle")
    # session with user rows only -> no stamps
    insert("ses_nouser33333333", "user", "whatever")
    con.commit()
    con.close()
    return db


@pytest.fixture()
def worker_env(tmp_path, monkeypatch, fixture_db):
    monkeypatch.setattr(prov, "REPO", tmp_path)
    monkeypatch.setattr(prov, "DB_PATH", fixture_db)
    monkeypatch.setattr(prov, "AUDIT_LOG", tmp_path / "ledger" / "provenance_corrections.jsonl")
    monkeypatch.setattr(prov, "SCAN_ROOTS", [tmp_path / "scan"])
    scan = tmp_path / "scan"
    scan.mkdir(parents=True, exist_ok=True)
    return scan


# ---------------------------------------------------------------- resolver

def test_resolver_hit_multi_model(fixture_db):
    con = sqlite3.connect(f"file:{fixture_db}?mode=ro", uri=True)
    res = prov.db_session_models(con, "ses_known1111111111")
    con.close()
    assert res is not None
    counts = res
    assert counts["x-preview-f-free"] == 2
    assert counts["nemotron-3-ultra-free"] == 1


def test_resolver_unknown_session_returns_none(fixture_db):
    con = sqlite3.connect(f"file:{fixture_db}?mode=ro", uri=True)
    assert prov.db_session_models(con, "ses_missing9999999") is None
    con.close()


def test_resolver_db_down_graceful(monkeypatch):
    con = None  # simulates unavailable db
    assert prov.db_session_models(con, "ses_whatever00000") is None


def test_open_db_ro_never_writes(worker_env):
    """Safety Engineer: connection must be read-only at the SQLite level.

    Uses worker_env so prov.DB_PATH points at the tmp fixture db — NOT the
    real ~/.local/share/opencode/opencode.db (WAL mode with writable side
    files makes PRAGMA wal_checkpoint succeed on a read-only connection).
    """
    con = prov.open_db_ro()
    assert con is not None
    with pytest.raises(sqlite3.OperationalError):
        con.execute("CREATE TABLE evil (x int)")
    # journal_mode=WAL requires write access — reliably raises on a
    # read-only connection (wal_checkpoint is a no-op in DELETE mode).
    with pytest.raises(sqlite3.OperationalError):
        con.execute("PRAGMA journal_mode=WAL")
    con.close()


# ---------------------------------------------------------------- verify

def test_verify_resolved_multi_model(worker_env):
    f = worker_env / "doc.md"
    f.write_text(
        "# Doc\n⬡ OMEGA ⬡ KALI ⬡ ox alpha ⬡ opencode ⬡ trc_x ⬡ ACTIVE\n"
        "Session ID: ses_known1111111111\n", encoding="utf-8")
    claim = prov.parse_file(f)
    verdict = prov.verify(claim, prov.open_db_ro())
    # fuzzy match: claimed 'ox alpha' aliases to x-preview-f-free which IS
    # among the stamps -> VERIFIED even though the session hot-swapped
    assert verdict["verdict"] == "VERIFIED"
    assert set(verdict["actual_models"]) == {"x-preview-f-free", "nemotron-3-ultra-free"}


def test_verify_verified_single_model(worker_env):
    f = worker_env / "single.md"
    f.write_text(
        "# Doc\n⬡ OMEGA ⬡ KALI ⬡ big pickle ⬡ opencode ⬡ trc_x ⬡ ACTIVE\n"
        "Session ID: ses_single22222222\n", encoding="utf-8")
    claim = prov.parse_file(f)
    verdict = prov.verify(claim, prov.open_db_ro())
    assert verdict["verdict"] == "VERIFIED"
    assert verdict["actual_models"] == ["big-pickle"]


def test_verify_unresolvable_falls_back_na(worker_env):
    f = worker_env / "stale.md"
    f.write_text(
        "# Doc\n⬡ OMEGA ⬡ KALI ⬡ gemini ⬡ opencode ⬡ trc_x ⬡ ACTIVE\n"
        "Session ID: ses_gone999999999\n", encoding="utf-8")
    claim = prov.parse_file(f)
    verdict = prov.verify(claim, prov.open_db_ro())
    assert verdict["verdict"] == "UNANCHORED"
    assert verdict["actual_models"] == []


def test_anchor_recall_deep_session(worker_env):
    """GAP-1: session ref below line 20 but within ANCHOR_ZONE must be found."""
    body = ["# Title"] + [f"filler line {i}" for i in range(30)]
    body += ["Referenced session: ses_single22222222"]
    f = worker_env / "deep.md"
    f.write_text(
        "\n".join(body[:5]) +
        "\n⬡ OMEGA ⬡ KALI ⬡ big pickle ⬡ opencode ⬡ trc_x ⬡ ACTIVE\n" +
        "\n".join(body[5:]) + "\n", encoding="utf-8")
    claim = prov.parse_file(f)
    assert "ses_single22222222" in claim["session_refs"]


# ---------------------------------------------------------------- ledger

def test_audit_append_does_not_clobber(worker_env):
    """ROOT-CAUSE REGRESSION: old code renamed tmp OVER ledger (last-writer-wins)."""
    for i in range(5):
        prov.audit({"ts": f"t{i}", "file": f"f{i}.md"})
    ledger = prov.AUDIT_LOG
    lines = ledger.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 5  # old bug: exactly 1 survivor
    assert [json.loads(l)["file"] for l in lines] == [f"f{i}.md" for i in range(5)]


# ------------------------------------------------------- update-in-place

def test_update_in_place_preserves_first_audit(worker_env):
    f = worker_env / "up.md"
    original_ts = "2026-08-23T20:39:41Z"
    f.write_text(
        "# Doc\n⬡ OMEGA ⬡ KALI ⬡ gemini ⬡ opencode ⬡ trc_x ⬡ ACTIVE\n"
        "Session ID: ses_single22222222\n"
        f"\n<!-- PROVENANCE-CORRECTED {original_ts} — FP-04 audit\n"
        "claimed_model: gemini | verdict: UNANCHORED | no session anchor in header zone\n"
        "actual_models(Tier0): n/a\n-->\n", encoding="utf-8")
    claim = prov.parse_file(f)
    assert claim["existing_annotation"]["verdict"] == "UNANCHORED"
    assert claim["existing_annotation"]["ts"] == original_ts
    verdict = prov.verify(claim, prov.open_db_ro())
    assert verdict["verdict"] == "MISATTRIBUTED"  # gemini claimed, big-pickle stamped
    assert prov.needs_update(claim, verdict)
    action = prov.apply_annotation(f, claim, verdict)
    assert action == "updated"
    text = f.read_text(encoding="utf-8")
    assert text.count("PROVENANCE-CORRECTED") == 1  # no double annotation
    assert f"first_audit: {original_ts}" in text     # historian: ts preserved
    assert "verdict: MISATTRIBUTED" in text


def test_no_churn_when_semantically_current(worker_env):
    f = worker_env / "cur.md"
    f.write_text(
        "# Doc\n⬡ OMEGA ⬡ KALI ⬡ gemini ⬡ opencode ⬡ trc_x ⬡ ACTIVE\n"
        "Session ID: ses_gone999999999\n"
        "\n<!-- PROVENANCE-CORRECTED 2026-08-24T03:00:00Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit\n"
        "claimed_model: gemini | verdict: UNANCHORED | session refs not found in DB\n"
        "actual_models(Tier0): n/a\n-->\n", encoding="utf-8")
    claim = prov.parse_file(f)
    verdict = prov.verify(claim, prov.open_db_ro())
    assert not prov.needs_update(claim, verdict)


def test_annotation_block_regex_matches_legacy_format():
    text = (
        "body\n"
        "<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit\n"
        "claimed_model: deepseek-v4-flash | verdict: UNANCHORED | no session anchor in header zone\n"
        "actual_models(Tier0): n/a\n"
        "-->\n"
    )
    ex = prov._existing_annotation(text)
    assert ex["ts"] == "2026-08-23T20:39:41Z"
    assert ex["claimed"] == "deepseek-v4-flash"
    assert ex["verdict"] == "UNANCHORED"
    assert ex["note"] == "no session anchor in header zone"
    assert ex["models"] == []


# ------------------------------------------------------- DC-01 fail-closed

def _annotated_file(worker_env, name="dc01.md"):
    f = worker_env / name
    f.write_text(
        "# Doc\n⬡ OMEGA ⬡ KALI ⬡ big pickle ⬡ opencode ⬡ trc_x ⬡ ACTIVE\n"
        "Session ID: ses_single22222222\n"
        "\n<!-- PROVENANCE-CORRECTED 2026-08-24T03:00:00Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit\n"
        "claimed_model: big pickle | verdict: VERIFIED\n"
        "actual_models(Tier0): big-pickle\n-->\n", encoding="utf-8")
    return f


def test_apply_aborts_when_db_unreachable(worker_env, monkeypatch):
    """DC-01 REGRESSION: db outage on the write path must fail CLOSED —
    nonzero exit, zero file mutations, zero ledger lines. The old
    graceful-n/a fallback would have rewritten real Tier-0 verdicts."""
    f = _annotated_file(worker_env)
    before = f.read_text(encoding="utf-8")
    monkeypatch.setattr(prov, "open_db_ro", lambda: None)  # simulate outage
    rc = prov.main(["--apply"])
    assert rc != 0
    assert f.read_text(encoding="utf-8") == before          # zero mutations
    assert not prov.AUDIT_LOG.exists()                      # zero ledger lines


def test_apply_abort_names_db_path(worker_env, monkeypatch, capsys):
    """The collapse message must name the unresolved DB_PATH (forensics)."""
    _annotated_file(worker_env)
    monkeypatch.setattr(prov, "open_db_ro", lambda: None)
    prov.main(["--apply"])
    err = capsys.readouterr().err
    assert "[TOOL-CHAIN-COLLAPSE]" in err
    assert str(prov.DB_PATH) in err


def test_dry_run_stays_graceful_when_db_unreachable(worker_env, monkeypatch, capsys):
    """Dry-run KEEPS graceful n/a degradation (read-only luxury)."""
    f = _annotated_file(worker_env)
    monkeypatch.setattr(prov, "open_db_ro", lambda: None)
    rc = prov.main([])
    assert rc == 0
    assert f.read_text(encoding="utf-8").count("PROVENANCE-CORRECTED") == 1  # untouched
    assert not prov.AUDIT_LOG.exists()
