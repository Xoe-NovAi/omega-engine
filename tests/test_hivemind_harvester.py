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


def test_harvest_execution_produces_artifacts(tmp_path, monkeypatch):
    # Ensure harvest_once runs cleanly and writes latest.md and latest.json
    res = harvest_once()
    assert res == 0
    
    repo_root = Path(__file__).resolve().parent.parent
    overview_dir = repo_root / "data" / "coordination" / "hivemind_overview"
    assert (overview_dir / "latest.json").exists()
    assert (overview_dir / "latest.md").exists()
    
    data = json.loads((overview_dir / "latest.json").read_text())
    assert data["generator"]["llm_used"] is False
    assert "radar" in data