# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

import pytest
import json
from pathlib import Path
from scripts.hivemind_harvest import parse_micro_digest, calculate_heartbeat_tier, harvest_once


def test_parse_micro_digest_full():
    raw = "DOING allowlist scrub · NEXT test gates · BLOCKER none"
    parsed = parse_micro_digest(raw, "", "")
    assert parsed["doing"] == "allowlist scrub"
    assert parsed["next"] == "test gates"
    assert parsed["blocker"] is None
    assert parsed["source"] == "digest"


def test_parse_micro_digest_with_real_blocker():
    raw = "DOING cgroup check · NEXT reboot · BLOCKER kernel panic on N1"
    parsed = parse_micro_digest(raw, "", "")
    assert parsed["doing"] == "cgroup check"
    assert parsed["blocker"] == "kernel panic on N1"


def test_parse_micro_digest_fallback():
    parsed = parse_micro_digest(None, "Running tests across modules", "Continue to next step")
    assert "Running tests" in parsed["doing"]
    assert "Continue" in parsed["next"]
    assert parsed["source"] == "fallback"


def test_heartbeat_tier():
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    
    active_ts = (now - timedelta(minutes=5)).isoformat()
    assert calculate_heartbeat_tier(active_ts, now) == "🟢 ACTIVE"
    
    idle_ts = (now - timedelta(minutes=20)).isoformat()
    assert calculate_heartbeat_tier(idle_ts, now) == "🟡 IDLE"
    
    expired_ts = (now - timedelta(minutes=50)).isoformat()
    assert calculate_heartbeat_tier(expired_ts, now) == "⚫ EXPIRED"


def _snapshot_live_overview() -> dict:
    """Fingerprint every file the harvester could write into the live checkout.

    The harvester's write surface is data/coordination/hivemind_overview/ --
    latest.json, latest.md, latest_good.*, history/ov_*.json, and (past 288
    cycles) archive/MANIFEST.jsonl. We fingerprint size + mtime_ns so an
    in-place rewrite that restores identical bytes still trips the guard.
    """
    live_dir = Path(__file__).resolve().parent.parent / "data" / "coordination" / "hivemind_overview"
    if not live_dir.exists():
        return {}
    return {
        str(p.relative_to(live_dir)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in sorted(live_dir.rglob("*"))
        if p.is_file()
    }


def test_harvest_execution_produces_artifacts(tmp_path, monkeypatch):
    """harvest_once() must write into tmp_path and touch NOTHING live.

    This test previously called harvest_once() bare while accepting tmp_path and
    monkeypatch without using either. get_repo_root() resolves the live checkout
    from __file__, so the "unit" test was writing latest.json/latest.md,
    a history/ record, and past 288 cycles an append-only MANIFEST.jsonl entry
    into live coordination state on every CI run. The assertion below is the
    point: verifying "it produced artifacts" is exactly what let that through.
    """
    live_before = _snapshot_live_overview()

    # tmp_path is the injection point. Every read and write derives from it.
    res = harvest_once(repo_root=tmp_path)
    assert res == 0

    overview_dir = tmp_path / "data" / "coordination" / "hivemind_overview"
    assert (overview_dir / "latest.json").exists()
    assert (overview_dir / "latest.md").exists()

    data = json.loads((overview_dir / "latest.json").read_text())
    assert data["generator"]["llm_used"] is False
    assert "radar" in data

    # The history record must land under tmp_path, not the live checkout.
    assert list((overview_dir / "history").glob("ov_*.json")), "history record not written under tmp_path"

    # THE GUARD: live coordination state must be byte-identical.
    assert _snapshot_live_overview() == live_before, (
        "harvest_once() mutated live data/coordination/hivemind_overview/ — "
        "this test must never write into the checkout"
    )