# 🔱 Omega Engine — Sovereignty Ratio Query (D203)
# AP: AP-SOVEREIGNTY-RATIO-v1.0.0
# ⬡ OMEGA ⬡ RESEARCHER ⬡ hy3-free ⬡ opencode ⬡ trc_research
#
# Queries MetricsDB performance table for local vs cloud inference ratio.
# The `is_cloud` field is set per-response by the ModelGateway (M22 provenance).
# Local=0, Cloud=1.
#
# [id-soft: vet-016] cvar — sovereignty ratio as a cvar-table metric

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Default MetricsDB location (matches MetricsDB class default)
METRICS_DB_PATH = Path("data/observability/metrics.db")

# [Performance] Cache of db_paths for which the corrected schema has been
# ensured. The classification table and view only need to be built once per
# process per db_path — rebuilding on every sovereignty query wastes a
# YAML parse + SQLite executescript.
_schema_ensured_for: set[str] = set()


def _ensure_corrected_schema(db_path: str | Path, force: bool = False) -> None:
    """Ensure provider_classification + v_performance_corrected exist (M22 SSOT).

    Idempotent. Uses MetricsDB so the classification table and corrected
    view are the single, shared definition of cloud/local.
    [Performance] Cached per db_path — only builds once per process unless
    force=True (e.g., after a known config change).
    """
    key = str(db_path)
    if not force and key in _schema_ensured_for:
        return
    from omega.observability.metrics_db import MetricsDB

    db = MetricsDB(Path(db_path))
    try:
        db.initialize()
        db.create_corrected_performance_view()
        _schema_ensured_for.add(key)
    finally:
        db.close()


def get_sovereignty_ratio(
    db_path: str | Path = METRICS_DB_PATH,
    since_days: int | None = None,
) -> Dict[str, Any]:
    """
    Query the local vs cloud inference ratio from MetricsDB.

    Args:
        db_path: Path to the MetricsDB SQLite database.
        since_days: Optional — only count inferences from last N days.

    Returns:
        Dict with keys: local_count, cloud_count, total, ratio_local,
        ratio_cloud, provider_breakdown, since, generated_at.
        Returns empty counts if DB doesn't exist or has no data.
    """
    db = Path(db_path)
    if not db.exists():
        logger.warning(f"MetricsDB not found at {db_path}")
        return {
            "local_count": 0,
            "cloud_count": 0,
            "total": 0,
            "ratio_local": 0.0,
            "ratio_cloud": 0.0,
            "provider_breakdown": {},
            "since": "no_data",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    try:
        conn = sqlite3.connect(str(db))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Check if performance table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='performance'")
        if not cur.fetchone():
            conn.close()
            return {
                "local_count": 0,
                "cloud_count": 0,
                "total": 0,
                "ratio_local": 0.0,
                "ratio_cloud": 0.0,
                "provider_breakdown": {},
                "since": "no_table",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        # Time filter
        since_ts = None
        if since_days:
            since_ts = datetime.now(timezone.utc).timestamp() - since_days * 86400

        # Aggregate counts (corrected classification from providers.yaml)
        # Ensure the corrected schema/view exists before querying it.
        _ensure_corrected_schema(db)
        if since_ts:
            cur.execute(
                """
                SELECT
                    SUM(CASE WHEN is_cloud_corrected = 0 THEN 1 ELSE 0 END) as local_count,
                    SUM(CASE WHEN is_cloud_corrected = 1 THEN 1 ELSE 0 END) as cloud_count,
                    COUNT(*) as total
                FROM v_performance_corrected
                WHERE ts >= ?
                """,
                (since_ts,),
            )
        else:
            cur.execute(
                """
                SELECT
                    SUM(CASE WHEN is_cloud_corrected = 0 THEN 1 ELSE 0 END) as local_count,
                    SUM(CASE WHEN is_cloud_corrected = 1 THEN 1 ELSE 0 END) as cloud_count,
                    COUNT(*) as total
                FROM v_performance_corrected
                """
            )

        row = cur.fetchone()
        local_count = row["local_count"] or 0
        cloud_count = row["cloud_count"] or 0
        total = row["total"] or 0

        # Provider breakdown (corrected classification)
        if since_ts:
            cur.execute(
                """
                SELECT provider, is_cloud_corrected, COUNT(*) as cnt
                FROM v_performance_corrected
                WHERE ts >= ?
                GROUP BY provider, is_cloud_corrected
                ORDER BY cnt DESC
                """,
                (since_ts,),
            )
        else:
            cur.execute(
                """
                SELECT provider, is_cloud_corrected, COUNT(*) as cnt
                FROM v_performance_corrected
                GROUP BY provider, is_cloud_corrected
                ORDER BY cnt DESC
                """
            )

        provider_breakdown = {}
        for prow in cur.fetchall():
            provider_breakdown[prow["provider"]] = {
                "count": prow["cnt"],
                "is_cloud": bool(prow["is_cloud_corrected"]),
            }

        conn.close()

        ratio_local = local_count / max(total, 1)
        ratio_cloud = cloud_count / max(total, 1)

        return {
            "local_count": local_count,
            "cloud_count": cloud_count,
            "total": total,
            "ratio_local": round(ratio_local, 4),
            "ratio_cloud": round(ratio_cloud, 4),
            "provider_breakdown": provider_breakdown,
            "since": f"last_{since_days}_days" if since_days else "all_time",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    except sqlite3.Error as e:
        logger.error(f"MetricsDB query failed: {e}")
        return {
            "local_count": 0,
            "cloud_count": 0,
            "total": 0,
            "ratio_local": 0.0,
            "ratio_cloud": 0.0,
            "provider_breakdown": {},
            "error": str(e),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
