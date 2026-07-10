# 🔱 Omega Engine — Sovereignty Ratio Tests (D203)
# ⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research

import pytest
import json
import sqlite3
from pathlib import Path
from omega.observability.sovereignty import get_sovereignty_ratio


@pytest.fixture
def seeded_db(tmp_path):
    """Create a temporary MetricsDB with known local/cloud data."""
    db = tmp_path / "metrics.db"
    conn = sqlite3.connect(str(db))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            trace_id TEXT,
            provider TEXT,
            model_used TEXT,
            latency_ms REAL NOT NULL,
            prompt_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            is_cloud INTEGER DEFAULT 0,
            cost_usd REAL DEFAULT 0.0
        );
    """)
    # 80 local, 20 cloud — use timestamps within last 7 days for since filter
    from datetime import datetime, timezone, timedelta
    now_ts = datetime.now(timezone.utc).timestamp()
    old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).timestamp()
    for i in range(80):
        conn.execute(
            "INSERT INTO performance (ts, trace_id, provider, model_used, latency_ms, is_cloud) VALUES (?, ?, ?, ?, ?, 0)",
            (now_ts, f"t{i}", "local_provider", "model", 100.0),
        )
    for i in range(20):
        conn.execute(
            "INSERT INTO performance (ts, trace_id, provider, model_used, latency_ms, is_cloud) VALUES (?, ?, ?, ?, ?, 1)",
            (now_ts, f"t{i+100}", "cloud_provider", "gpt4", 500.0),
        )
    conn.commit()
    conn.close()
    return db


class TestSovereigntyRatio:
    def test_returns_dict_with_keys(self):
        """D203: get_sovereignty_ratio returns expected keys."""
        result = get_sovereignty_ratio()
        assert isinstance(result, dict)
        assert "local_count" in result
        assert "cloud_count" in result
        assert "total" in result
        assert "ratio_local" in result
        assert "ratio_cloud" in result

    def test_empty_db_returns_zeros(self, tmp_path):
        """D203: Empty or missing DB returns zero counts."""
        result = get_sovereignty_ratio(db_path=tmp_path / "nonexistent.db")
        assert result["total"] == 0
        assert result["ratio_local"] == 0.0

    def test_known_ratio(self, seeded_db):
        """D203: 80 local + 20 cloud → 80% local, 20% cloud."""
        result = get_sovereignty_ratio(db_path=seeded_db)
        assert result["local_count"] == 80
        assert result["cloud_count"] == 20
        assert result["total"] == 100
        assert result["ratio_local"] == 0.8
        assert result["ratio_cloud"] == 0.2

    def test_provider_breakdown(self, seeded_db):
        """D203: Provider breakdown includes both providers."""
        result = get_sovereignty_ratio(db_path=seeded_db)
        assert "local_provider" in result["provider_breakdown"]
        assert "cloud_provider" in result["provider_breakdown"]
        assert result["provider_breakdown"]["local_provider"]["count"] == 80
        assert result["provider_breakdown"]["cloud_provider"]["count"] == 20

    def test_since_filter_recent(self, seeded_db):
        """D203: since_days with recent data returns all rows."""
        result = get_sovereignty_ratio(db_path=seeded_db, since_days=7)
        # Data was inserted with now_ts, so it's within the last 7 days
        assert result["total"] == 100

    def test_since_filter_excludes_old(self, tmp_path):
        """D203: since_days excludes old data."""
        import sqlite3
        from datetime import datetime, timezone, timedelta

        db = tmp_path / "metrics.db"
        conn = sqlite3.connect(str(db))
        conn.execute("""
            CREATE TABLE performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL, trace_id TEXT, provider TEXT,
                model_used TEXT, latency_ms REAL NOT NULL,
                prompt_tokens INTEGER DEFAULT 0, completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0, is_cloud INTEGER DEFAULT 0, cost_usd REAL DEFAULT 0.0
            )
        """)
        # 10 old rows (30 days ago)
        old_ts = (datetime.now(timezone.utc) - timedelta(days=30)).timestamp()
        for i in range(10):
            conn.execute(
                "INSERT INTO performance (ts, trace_id, provider, model_used, latency_ms, is_cloud) VALUES (?,?,?,?,?,0)",
                (old_ts, f"old_{i}", "local", "m", 10.0),
            )
        conn.commit()
        conn.close()

        result = get_sovereignty_ratio(db_path=db, since_days=7)
        assert result["total"] == 0  # All 10 rows are 30 days old

        result_all = get_sovereignty_ratio(db_path=db)
        assert result_all["total"] == 10  # Without filter, find all
